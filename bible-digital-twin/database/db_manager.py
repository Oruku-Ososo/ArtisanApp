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
