"""
Database Module

Handles database connections and operations for the Bible Digital Twin.
Supports PostgreSQL with pgvector for vector similarity search.
"""

import os
import json
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
import sqlite3


class DatabaseManager:
    """Manage database connections and schema."""
    
    def __init__(self, db_path: str = "./bible_digital_twin.db"):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Get a database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create books table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    testament TEXT NOT NULL,
                    chapters INTEGER NOT NULL
                )
            ''')
            
            # Create chapters table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    chapter_number INTEGER NOT NULL,
                    FOREIGN KEY (book_id) REFERENCES books(id),
                    UNIQUE(book_id, chapter_number)
                )
            ''')
            
            # Create verses table with full-text search
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    chapter_id INTEGER NOT NULL,
                    verse_number INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    translation TEXT DEFAULT 'KJV',
                    FOREIGN KEY (book_id) REFERENCES books(id),
                    FOREIGN KEY (chapter_id) REFERENCES chapters(id),
                    UNIQUE(book_id, chapter_id, verse_number, translation)
                )
            ''')
            
            # Create verse embeddings table for vector search
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verse_embeddings (
                    verse_id INTEGER PRIMARY KEY,
                    embedding BLOB NOT NULL,
                    model_name TEXT NOT NULL,
                    FOREIGN KEY (verse_id) REFERENCES verses(id)
                )
            ''')
            
            # Create entities table for knowledge graph
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    attributes TEXT,
                    refs TEXT
                )
            ''')
            
            # Create relationships table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    attributes TEXT,
                    refs TEXT,
                    FOREIGN KEY (source_id) REFERENCES entities(id),
                    FOREIGN KEY (target_id) REFERENCES entities(id)
                )
            ''')
            
            # Create cross_references table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cross_references (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_verse_id INTEGER NOT NULL,
                    target_verse_id INTEGER NOT NULL,
                    relationship_type TEXT,
                    FOREIGN KEY (source_verse_id) REFERENCES verses(id),
                    FOREIGN KEY (target_verse_id) REFERENCES verses(id)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_verses_book_chapter ON verses(book_id, chapter_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_verses_translation ON verses(translation)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_id)')
            
            conn.commit()
    
    def insert_book(self, name: str, testament: str, chapters: int) -> int:
        """Insert a book and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO books (name, testament, chapters) VALUES (?, ?, ?)',
                (name, testament, chapters)
            )
            cursor.execute('SELECT id FROM books WHERE name = ?', (name,))
            result = cursor.fetchone()
            conn.commit()
            return result['id'] if result else None
    
    def insert_chapter(self, book_id: int, chapter_number: int) -> int:
        """Insert a chapter and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR IGNORE INTO chapters (book_id, chapter_number) VALUES (?, ?)',
                (book_id, chapter_number)
            )
            cursor.execute(
                'SELECT id FROM chapters WHERE book_id = ? AND chapter_number = ?',
                (book_id, chapter_number)
            )
            result = cursor.fetchone()
            conn.commit()
            return result['id'] if result else None
    
    def insert_verse(self, book_id: int, chapter_id: int, verse_number: int, 
                     text: str, translation: str = 'KJV') -> int:
        """Insert a verse and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT OR REPLACE INTO verses 
                   (book_id, chapter_id, verse_number, text, translation) 
                   VALUES (?, ?, ?, ?, ?)''',
                (book_id, chapter_id, verse_number, text, translation)
            )
            conn.commit()
            return cursor.lastrowid
    
    def insert_embedding(self, verse_id: int, embedding: bytes, model_name: str):
        """Store verse embedding."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT OR REPLACE INTO verse_embeddings 
                   (verse_id, embedding, model_name) VALUES (?, ?, ?)''',
                (verse_id, embedding, model_name)
            )
            conn.commit()
    
    def get_verse(self, book_name: str, chapter: int, verse: int, 
                  translation: str = 'KJV') -> Optional[Dict]:
        """Retrieve a specific verse."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT v.id, v.text, v.verse_number, b.name as book_name
                FROM verses v
                JOIN books b ON v.book_id = b.id
                WHERE b.name = ? AND v.chapter_id IN (
                    SELECT id FROM chapters WHERE book_id = (
                        SELECT id FROM books WHERE name = ?
                    ) AND chapter_number = ?
                ) AND v.verse_number = ? AND v.translation = ?
            ''', (book_name, book_name, chapter, verse, translation))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result['id'],
                    'reference': f"{result['book_name']} {chapter}:{verse}",
                    'text': result['text'],
                    'translation': translation
                }
            return None
    
    def search_verses_fulltext(self, query: str, translation: str = 'KJV', 
                                limit: int = 10) -> List[Dict]:
        """Full-text search for verses."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT v.id, v.text, v.verse_number, b.name as book_name, c.chapter_number
                FROM verses v
                JOIN books b ON v.book_id = b.id
                JOIN chapters c ON v.chapter_id = c.id
                WHERE v.text LIKE ? AND v.translation = ?
                LIMIT ?
            ''', (f'%{query}%', translation, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'reference': f"{row['book_name']} {row['chapter_number']}:{row['verse_number']}",
                    'text': row['text'],
                    'translation': translation
                })
            return results
    
    def insert_entity(self, entity_id: str, name: str, type: str, 
                      attributes: Dict, refs: List[str]):
        """Insert an entity into the knowledge graph."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT OR REPLACE INTO entities 
                   (id, name, type, attributes, refs) 
                   VALUES (?, ?, ?, ?, ?)''',
                (entity_id, name, type, json.dumps(attributes), json.dumps(refs))
            )
            conn.commit()
    
    def insert_relationship(self, source_id: str, target_id: str, 
                           rel_type: str, attributes: Dict = None, 
                           refs: List[str] = None):
        """Insert a relationship between entities."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO relationships 
                   (source_id, target_id, type, attributes, refs) 
                   VALUES (?, ?, ?, ?, ?)''',
                (source_id, target_id, rel_type, 
                 json.dumps(attributes or {}), json.dumps(refs or []))
            )
            conn.commit()
    
    def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Retrieve an entity by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM entities WHERE id = ?', (entity_id,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result['id'],
                    'name': result['name'],
                    'type': result['type'],
                    'attributes': json.loads(result['attributes']),
                    'references': json.loads(result['refs'])
                }
            return None
    
    def get_entities_by_type(self, entity_type: str) -> List[Dict]:
        """Get all entities of a specific type."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM entities WHERE type = ?', (entity_type,))
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'name': row['name'],
                    'type': row['type'],
                    'attributes': json.loads(row['attributes']),
                    'references': json.loads(row['refs'])
                })
            return results
    
    def get_relationships(self, entity_id: str) -> List[Dict]:
        """Get all relationships for an entity."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM relationships 
                WHERE source_id = ? OR target_id = ?
            ''', (entity_id, entity_id))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'source_id': row['source_id'],
                    'target_id': row['target_id'],
                    'type': row['type'],
                    'attributes': json.loads(row['attributes']) if row['attributes'] else {},
                    'references': json.loads(row['refs']) if row['refs'] else []
                })
            return results
    
    def get_book_by_name(self, book_name: str) -> Optional[Dict]:
        """Get book information by name."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM books WHERE name = ?', (book_name,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result['id'],
                    'name': result['name'],
                    'testament': result['testament'],
                    'chapters': result['chapters']
                }
            return None
    
    def get_chapter_verses(self, book_name: str, chapter: int, 
                          translation: str = 'KJV') -> List[Dict]:
        """Get all verses in a chapter."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT v.id, v.text, v.verse_number, b.name as book_name
                FROM verses v
                JOIN books b ON v.book_id = b.id
                JOIN chapters c ON v.chapter_id = c.id
                WHERE b.name = ? AND c.chapter_number = ? AND v.translation = ?
                ORDER BY v.verse_number
            ''', (book_name, chapter, translation))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row['id'],
                    'reference': f"{row['book_name']} {chapter}:{row['verse_number']}",
                    'text': row['text'],
                    'translation': translation,
                    'verse_number': row['verse_number']
                })
            return results
    
    def get_book_verses(self, book_name: str, translation: str = 'KJV') -> Optional[Dict]:
        """Get all verses in a book organized by chapter."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM books WHERE name = ?', (book_name,))
            book_result = cursor.fetchone()
            if not book_result:
                return None
            
            cursor.execute('''
                SELECT v.text, v.verse_number, c.chapter_number
                FROM verses v
                JOIN chapters c ON v.chapter_id = c.id
                WHERE v.book_id = ? AND v.translation = ?
                ORDER BY c.chapter_number, v.verse_number
            ''', (book_result['id'], translation))
            
            chapters = {}
            for row in cursor.fetchall():
                ch_num = row['chapter_number']
                if ch_num not in chapters:
                    chapters[ch_num] = []
                chapters[ch_num].append({
                    'verse_number': row['verse_number'],
                    'text': row['text']
                })
            
            return {
                'name': book_result['name'],
                'testament': book_result['testament'],
                'chapters': book_result['chapters'],
                'chapters_data': chapters
            }
    
    def get_embedding(self, verse_id: int) -> Optional[bytes]:
        """Get embedding for a verse."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT embedding FROM verse_embeddings WHERE verse_id = ?', (verse_id,))
            result = cursor.fetchone()
            return result['embedding'] if result else None
    
    def create_bookmark(self, user_id: str, verse_ref: str,
                       notes: str = None, tags: List[str] = None,
                       is_public: bool = False) -> Dict:
        """Create a bookmark."""
        now = datetime.now().isoformat()
        bookmark_id = hash(f"{user_id}{verse_ref}{now}") % 1000000
        
        bookmark = {
            'id': bookmark_id,
            'user_id': user_id,
            'verse_ref': verse_ref,
            'notes': notes,
            'tags': tags or [],
            'is_public': is_public,
            'created_at': now,
            'updated_at': now
        }
        
        # In production, this would be stored in the database
        # For now, store in a simple dict (would use Redis or DB table)
        if not hasattr(self, '_bookmarks'):
            self._bookmarks = {}
        self._bookmarks[bookmark_id] = bookmark
        
        return bookmark
    
    def get_user_bookmarks(self, user_id: str) -> List[Dict]:
        """Get user bookmarks."""
        if not hasattr(self, '_bookmarks'):
            return []
        return [b for b in self._bookmarks.values() if b['user_id'] == user_id]
    
    def delete_bookmark(self, bookmark_id: int) -> bool:
        """Delete a bookmark."""
        if hasattr(self, '_bookmarks') and bookmark_id in self._bookmarks:
            del self._bookmarks[bookmark_id]
            return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM verses')
            total_verses = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM books')
            total_books = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT chapter_id) FROM chapters')
            total_chapters = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM entities')
            total_entities = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM relationships')
            total_relationships = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM verse_embeddings')
            embeddings_count = cursor.fetchone()[0]
            
            return {
                'total_verses': total_verses,
                'total_books': total_books,
                'total_chapters': total_chapters,
                'total_entities': total_entities,
                'total_relationships': total_relationships,
                'embeddings_count': embeddings_count
            }


# Import datetime at module level
from datetime import datetime
