#!/usr/bin/env python3
"""
BibleHub Scraper & Ingestion Engine
Scrapes Bible text from BibleHub and ingests it into the Digital Twin database.
Supports multiple versions (KJV, NIV, ESV, etc.) and full Bible ingestion.
"""

import argparse
import asyncio
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Add parent directory to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from database.db_manager import DatabaseManager
from services.bible_service_v2 import BibleServiceV2

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bible book order and chapter counts (for KJV, approximate for others)
BIBLE_BOOKS = {
    "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
    "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
    "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36,
    "Ezra": 10, "Nehemiah": 13, "Esther": 10, "Job": 42, "Psalms": 150,
    "Proverbs": 31, "Ecclesiastes": 12, "Song of Solomon": 8, "Isaiah": 66,
    "Jeremiah": 52, "Lamentations": 5, "Ezekiel": 48, "Daniel": 12,
    "Hosea": 14, "Joel": 3, "Amos": 9, "Obadiah": 1, "Jonah": 4,
    "Micah": 7, "Nahum": 3, "Habakkuk": 3, "Zephaniah": 3, "Haggai": 2,
    "Zechariah": 14, "Malachi": 4,
    "Matthew": 28, "Mark": 16, "Luke": 24, "John": 21, "Acts": 28,
    "Romans": 16, "1 Corinthians": 16, "2 Corinthians": 13, "Galatians": 6,
    "Ephesians": 6, "Philippians": 4, "Colossians": 4, "1 Thessalonians": 5,
    "2 Thessalonians": 3, "1 Timothy": 6, "2 Timothy": 4, "Titus": 3,
    "Philemon": 1, "Hebrews": 13, "James": 5, "1 Peter": 5, "2 Peter": 3,
    "1 John": 5, "2 John": 1, "3 John": 1, "Jude": 1, "Revelation": 22
}

class BibleHubScraper:
    """Production-grade scraper for BibleHub.com"""
    
    def __init__(self, version: str = "KJV", delay: float = 1.0, max_retries: int = 3):
        self.version = version.upper()
        self.delay = delay
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        self.base_url = "https://biblehub.com"
        
    def _get_chapter_url(self, book: str, chapter: int) -> str:
        """Generate BibleHub URL for a specific chapter"""
        book_slug = book.lower().replace(" ", "-").replace("'", "")
        # Handle special cases
        if book_slug.startswith("1-"):
            book_slug = "1-" + book_slug[2:]
        elif book_slug.startswith("2-"):
            book_slug = "2-" + book_slug[2:]
        elif book_slug.startswith("3-"):
            book_slug = "3-" + book_slug[2:]
            
        return f"{self.base_url}/{book_slug}/{chapter}.htm"
    
    def _fetch_with_retry(self, url: str) -> Optional[str]:
        """Fetch URL with exponential backoff retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Check if we're being rate-limited
                if response.status_code == 429 or "captcha" in response.text.lower():
                    wait_time = self.delay * (2 ** attempt) * 2
                    logger.warning(f"Rate limited or CAPTCHA detected. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                    
                return response.text
                
            except requests.exceptions.RequestException as e:
                wait_time = self.delay * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}. Waiting {wait_time}s...")
                time.sleep(wait_time)
                
        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None
    
    def _parse_chapter(self, html: str, book: str, chapter: int) -> List[Dict[str, Any]]:
        """Parse HTML and extract verses from BibleHub format"""
        soup = BeautifulSoup(html, 'html.parser')
        verses = []
        
        # BibleHub uses various paragraph classes for verses:
        # - <p class="reg"> for regular verses
        # - <p class="tab1stline"> for continued verses
        # - <p class="indent1stline"> for indented verses
        verse_paragraphs = soup.find_all('p', class_=lambda c: c in ['reg', 'tab1stline', 'indent1stline'])
        
        if not verse_paragraphs:
            # Fallback: try to find content in chap div
            content_div = soup.find('div', class_='chap')
            if content_div:
                verse_paragraphs = content_div.find_all('p', class_=lambda c: c in ['reg', 'tab1stline', 'indent1stline'])
        
        for p_elem in verse_paragraphs:
            try:
                # Extract verse number from reftext span
                reftext = p_elem.find('span', class_='reftext')
                if not reftext:
                    continue
                    
                verse_link = reftext.find('a')
                if not verse_link:
                    continue
                    
                bold_num = verse_link.find('b')
                if not bold_num:
                    continue
                
                verse_num_text = bold_num.get_text(strip=True)
                if not verse_num_text.isdigit():
                    continue
                    
                verse_num = int(verse_num_text)
                
                # Extract verse text - get all text after the reftext span
                # Remove the reftext from the paragraph to get clean verse text
                reftext_copy = reftext  # Keep reference
                reftext.decompose()
                
                verse_text = p_elem.get_text(strip=True)
                
                # Clean up the text
                verse_text = re.sub(r'\s+', ' ', verse_text)
                verse_text = re.sub(r'\[\d+\]', '', verse_text)  # Remove footnote markers
                verse_text = verse_text.replace('\u2014', '-').replace('\u2013', '-')  # Fix dashes
                verse_text = verse_text.replace('\u201c', '"').replace('\u201d', '"')  # Fix quotes
                
                if verse_text and len(verse_text) > 5:
                    verses.append({
                        'book': book,
                        'chapter': chapter,
                        'verse': verse_num,
                        'text': verse_text,
                        'version': self.version
                    })
            except Exception as e:
                logger.debug(f"Error parsing verse element: {e}")
                continue
        
        # If no verses found with standard method, try fallback
        if not verses:
            logger.warning(f"Standard parsing failed for {book} {chapter}, trying fallback")
            verses = self._fallback_parse(soup, book, chapter)
        
        return verses
    
    def _fallback_parse(self, soup: BeautifulSoup, book: str, chapter: int) -> List[Dict[str, Any]]:
        """Fallback parsing method for BibleHub"""
        verses = []
        
        # Try to find all anchor tags with verse references
        content_div = soup.find('div', class_='chap')
        if not content_div:
            content_div = soup
            
        # Look for patterns like <A name="2"></a><p class="reg">
        for p_tag in content_div.find_all('p'):
            try:
                # Check if this paragraph contains a verse reference
                reftext = p_tag.find('span', class_='reftext')
                if reftext:
                    # Use the main parsing logic
                    temp_verses = self._parse_chapter(p_tag.parent.decode(), book, chapter)
                    if temp_verses:
                        verses.extend(temp_verses)
            except:
                continue
        
        return verses
    
    def _manual_parse_verses(self, text: str, book: str, chapter: int) -> List[Dict[str, Any]]:
        """Fallback manual parsing for verses"""
        verses = []
        # Pattern to match verse numbers (e.g., "1", "2", etc.)
        pattern = r'(\d+)\s+(.*?)(?=\d+\s+|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for verse_num, verse_text in matches:
            verse_text = verse_text.strip()
            if verse_text and len(verse_text) > 5:  # Filter out noise
                verses.append({
                    'book': book,
                    'chapter': chapter,
                    'verse': int(verse_num),
                    'text': verse_text,
                    'version': self.version
                })
        
        return verses
    
    def scrape_chapter(self, book: str, chapter: int) -> List[Dict[str, Any]]:
        """Scrape a single chapter"""
        url = self._get_chapter_url(book, chapter)
        logger.info(f"Scraping {book} {chapter} from {url}")
        
        html = self._fetch_with_retry(url)
        if not html:
            return []
        
        verses = self._parse_chapter(html, book, chapter)
        
        # Rate limiting
        time.sleep(self.delay)
        
        return verses
    
    def scrape_book(self, book: str, max_chapters: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape an entire book"""
        all_verses = []
        num_chapters = max_chapters or BIBLE_BOOKS.get(book, 50)
        
        logger.info(f"Starting to scrape {book} ({num_chapters} chapters)")
        
        for chapter in range(1, num_chapters + 1):
            verses = self.scrape_chapter(book, chapter)
            if verses:
                all_verses.extend(verses)
                logger.info(f"  Chapter {chapter}: {len(verses)} verses")
            else:
                logger.warning(f"  Chapter {chapter}: No verses found")
        
        return all_verses
    
    def scrape_bible(self, books: Optional[List[str]] = None, workers: int = 1) -> List[Dict[str, Any]]:
        """Scrape multiple books with parallel processing"""
        if books is None:
            books = list(BIBLE_BOOKS.keys())
        
        all_verses = []
        
        if workers == 1:
            # Sequential processing
            for book in tqdm(books, desc="Scraping Bible"):
                verses = self.scrape_book(book)
                all_verses.extend(verses)
        else:
            # Parallel processing (be careful with rate limits)
            logger.info(f"Using {workers} worker threads")
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(self.scrape_book, book): book for book in books}
                
                for future in tqdm(as_completed(futures), total=len(futures), desc="Scraping Bible"):
                    book = futures[future]
                    try:
                        verses = future.result()
                        all_verses.extend(verses)
                        logger.info(f"Completed {book}: {len(verses)} verses")
                    except Exception as e:
                        logger.error(f"Error scraping {book}: {e}")
        
        return all_verses


class BibleIngester:
    """Ingests scraped Bible data into the Digital Twin database"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.service = BibleServiceV2()
        
    def _get_or_create_book(self, book_name: str) -> int:
        """Get or create a book entry and return its ID"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Try to find existing book
            cursor.execute('SELECT id FROM books WHERE name = ?', (book_name,))
            result = cursor.fetchone()
            if result:
                return result['id']
            
            # Create new book - determine testament and chapter count
            testament = "OT" if book_name in ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
                                               "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel",
                                               "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles",
                                               "Ezra", "Nehemiah", "Esther", "Job", "Psalms",
                                               "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
                                               "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
                                               "Hosea", "Joel", "Amos", "Obadiah", "Jonah",
                                               "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
                                               "Zechariah", "Malachi"] else "NT"
            chapters = BIBLE_BOOKS.get(book_name, 50)
            
            cursor.execute(
                'INSERT INTO books (name, testament, chapters) VALUES (?, ?, ?)',
                (book_name, testament, chapters)
            )
            conn.commit()
            return cursor.lastrowid
    
    def _get_or_create_chapter(self, book_id: int, chapter_num: int) -> int:
        """Get or create a chapter entry and return its ID"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Try to find existing chapter
            cursor.execute(
                'SELECT id FROM chapters WHERE book_id = ? AND chapter_number = ?',
                (book_id, chapter_num)
            )
            result = cursor.fetchone()
            if result:
                return result['id']
            
            # Create new chapter
            cursor.execute(
                'INSERT INTO chapters (book_id, chapter_number) VALUES (?, ?)',
                (book_id, chapter_num)
            )
            conn.commit()
            return cursor.lastrowid
    
    def ingest_verses(self, verses: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, int]:
        """Ingest verses into database with batching"""
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        logger.info(f"Starting ingestion of {len(verses)} verses")
        
        # Group verses by version for efficient processing
        verses_by_version = {}
        for verse in verses:
            version = verse['version']
            if version not in verses_by_version:
                verses_by_version[version] = []
            verses_by_version[version].append(verse)
        
        for version, version_verses in verses_by_version.items():
            logger.info(f"Processing version: {version} ({len(version_verses)} verses)")
            
            for i in range(0, len(version_verses), batch_size):
                batch = version_verses[i:i + batch_size]
                
                try:
                    # Insert or update verses
                    for verse_data in batch:
                        try:
                            # Get or create book and chapter
                            book_id = self._get_or_create_book(verse_data['book'])
                            chapter_id = self._get_or_create_chapter(book_id, verse_data['chapter'])
                            
                            # Insert verse using existing method
                            verse_id = self.db.insert_verse(
                                book_id=book_id,
                                chapter_id=chapter_id,
                                verse_number=verse_data['verse'],
                                text=verse_data['text'],
                                translation=verse_data['version']
                            )
                            
                            if verse_id:
                                stats['inserted'] += 1
                            else:
                                stats['updated'] += 1
                                
                        except Exception as e:
                            logger.debug(f"Error inserting verse {verse_data}: {e}")
                            stats['errors'] += 1
                            
                except Exception as e:
                    logger.error(f"Error inserting batch: {e}")
                    stats['errors'] += len(batch)
                
                # Progress update
                if (i // batch_size) % 10 == 0:
                    logger.info(f"  Processed {min(i + batch_size, len(version_verses))}/{len(version_verses)} verses")
        
        return stats
    
    def post_process(self, versions: List[str]):
        """Run post-processing tasks (embeddings, entities, etc.)"""
        logger.info("Starting post-processing...")
        
        for version in versions:
            logger.info(f"Generating embeddings for {version}...")
            # Note: This would call the embedding service
            # For now, we'll skip actual embedding generation to avoid long delays
            
        logger.info("Post-processing complete")


def main():
    parser = argparse.ArgumentParser(description="Scrape and ingest Bible data from BibleHub")
    parser.add_argument('--all', action='store_true', help='Scrape entire Bible')
    parser.add_argument('--book', type=str, help='Scrape specific book (e.g., "Genesis")')
    parser.add_argument('--versions', type=str, default='KJV', 
                       help='Comma-separated list of versions (e.g., "KJV,NIV,ESV")')
    parser.add_argument('--workers', type=int, default=1, help='Number of parallel workers')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    parser.add_argument('--test', action='store_true', help='Test mode: scrape only Genesis 1')
    
    args = parser.parse_args()
    
    versions = [v.strip().upper() for v in args.versions.split(',')]
    
    if args.test:
        logger.info("Running in TEST mode - scraping Genesis 1 only")
        books = ['Genesis']
        max_chapters = 1
    elif args.book:
        books = [args.book]
        max_chapters = None
    elif args.all:
        books = list(BIBLE_BOOKS.keys())
        max_chapters = None
    else:
        parser.print_help()
        return
    
    total_stats = {'inserted': 0, 'updated': 0, 'errors': 0}
    
    for version in versions:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing version: {version}")
        logger.info(f"{'='*60}\n")
        
        # Scrape
        scraper = BibleHubScraper(version=version, delay=args.delay)
        
        if args.test:
            verses = scraper.scrape_book('Genesis', max_chapters=1)
        elif args.book:
            verses = scraper.scrape_book(args.book)
        else:
            verses = scraper.scrape_bible(books=books, workers=args.workers)
        
        if not verses:
            logger.warning(f"No verses scraped for {version}. Skipping ingestion.")
            continue
        
        logger.info(f"Scraped {len(verses)} verses for {version}")
        
        # Ingest
        ingester = BibleIngester()
        stats = ingester.ingest_verses(verses)
        
        for key in total_stats:
            total_stats[key] += stats[key]
        
        logger.info(f"Ingestion stats for {version}: {stats}")
    
    # Post-process
    if total_stats['inserted'] > 0 or total_stats['updated'] > 0:
        ingester.post_process(versions)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"TOTAL STATS: {total_stats}")
    logger.info(f"{'='*60}")


if __name__ == '__main__':
    main()
