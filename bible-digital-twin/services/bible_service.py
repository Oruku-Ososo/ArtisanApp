"""
Services Module

High-level business logic services for the Bible Digital Twin.
Orchestrates data loading, AI models, and knowledge graph operations.
"""

import os
import json
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from database.db_manager import DatabaseManager
from data.loader import BibleDataLoader, TextPreprocessor
from models.embeddings import (
    BiblicalEmbeddingModel, 
    CrossReferenceEngine, 
    NamedEntityRecognizer
)
from knowledge_graph.graph import BiblicalKnowledgeGraph, Entity, Relationship


class BibleService:
    """Main service orchestrating Bible digital twin operations."""
    
    def __init__(self, db_path: str = "./bible_digital_twin.db"):
        self.db = DatabaseManager(db_path)
        self.data_loader = BibleDataLoader()
        self.preprocessor = TextPreprocessor()
        self.embedding_model = BiblicalEmbeddingModel(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.cross_ref_engine = None
        self.ner_model = NamedEntityRecognizer()
        self.knowledge_graph = BiblicalKnowledgeGraph()
        self._initialized = False
    
    def initialize(self, load_models: bool = True):
        """Initialize all components."""
        if load_models:
            try:
                print("Loading embedding model...")
                self.embedding_model.load_model()
                print("Loading NER model...")
                self.ner_model.load_model()
                self.cross_ref_engine = CrossReferenceEngine(self.embedding_model)
                print("Models loaded successfully!")
            except Exception as e:
                print(f"Warning: Could not load models: {e}")
                print("Continuing without AI models...")
        
        self._initialized = True
        print("Bible Digital Twin initialized!")
    
    def load_bible_data(self, json_path: str = None):
        """Load Bible data from JSON file or built-in source."""
        if json_path and os.path.exists(json_path):
            data = self.data_loader.load_json(json_path)
        else:
            # Load built-in sample data
            data = self._get_sample_bible_data()
        
        # Process and store in database
        books_loaded = 0
        verses_loaded = 0
        
        for book_data in data.get('books', []):
            book_name = book_data['name']
            testament = book_data['testament']
            chapters = book_data['chapters']
            
            book_id = self.db.insert_book(book_name, testament, chapters)
            if book_id:
                books_loaded += 1
                
                # Get chapter data - handle both formats
                chapter_data = book_data.get('chapters_data', {})
                
                for chapter_num, verses in chapter_data.items():
                    chapter_id = self.db.insert_chapter(book_id, int(chapter_num))
                    
                    for verse_num, text in verses.items():
                        verse_id = self.db.insert_verse(
                            book_id, chapter_id, int(verse_num), text
                        )
                        verses_loaded += 1
                        
                        # Generate and store embedding
                        if self._initialized and self.embedding_model.model:
                            try:
                                embedding = self.embedding_model.encode([text])[0]
                                self.db.insert_embedding(
                                    verse_id, 
                                    embedding.tobytes(), 
                                    self.embedding_model.model_name
                                )
                                
                                # Index for cross-reference engine
                                if self.cross_ref_engine:
                                    verse_ref = f"{book_name} {chapter_num}:{verse_num}"
                                    self.cross_ref_engine.verse_embeddings[verse_ref] = embedding
                                    idx = len(self.cross_ref_engine.verse_index)
                                    self.cross_ref_engine.verse_index[idx] = verse_ref
                            except Exception as e:
                                pass  # Skip embedding on error
        
        print(f"Loaded {books_loaded} books with {verses_loaded} verses")
        return {'books': books_loaded, 'verses': verses_loaded}
    
    def get_verse(self, book: str, chapter: int, verse: int, 
                  translation: str = 'KJV') -> Optional[Dict]:
        """Get a specific verse."""
        return self.db.get_verse(book, chapter, verse, translation)
    
    def search_verses(self, query: str, top_k: int = 5, 
                      use_semantic: bool = True) -> List[Dict]:
        """Search for verses using full-text or semantic search."""
        if use_semantic and self.cross_ref_engine and self.embedding_model.model:
            # Semantic search
            results = self.cross_ref_engine.find_similar(query, top_k)
            verses = []
            for verse_ref, similarity in results:
                # Parse reference
                parts = verse_ref.split()
                book = parts[0]
                ch_vs = parts[1].split(':')
                chapter = int(ch_vs[0])
                verse_num = int(ch_vs[1])
                
                verse_data = self.get_verse(book, chapter, verse_num)
                if verse_data:
                    verse_data['similarity'] = similarity
                    verses.append(verse_data)
            return verses
        else:
            # Fallback to full-text search
            return self.db.search_verses_fulltext(query, limit=top_k)
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text."""
        if not self._initialized or not self.ner_model.model:
            return []
        return self.ner_model.extract_entities(text)
    
    def add_entity_to_graph(self, entity_id: str, name: str, type: str,
                           attributes: Dict = None, references: List[str] = None):
        """Add an entity to the knowledge graph."""
        entity = Entity(
            id=entity_id,
            name=name,
            type=type,
            attributes=attributes or {},
            references=references or []
        )
        self.knowledge_graph.add_entity(entity)
        self.db.insert_entity(entity_id, name, type, attributes or {}, references or [])
    
    def add_relationship(self, source_id: str, target_id: str, 
                        rel_type: str, attributes: Dict = None,
                        references: List[str] = None):
        """Add a relationship between entities."""
        relationship = Relationship(
            source=source_id,
            target=target_id,
            type=rel_type,
            attributes=attributes or {},
            references=references or []
        )
        self.knowledge_graph.add_relationship(relationship)
        self.db.insert_relationship(source_id, target_id, rel_type, 
                                   attributes, references)
    
    def get_entity(self, entity_id: str) -> Optional[Dict]:
        """Get an entity from the knowledge graph."""
        return self.db.get_entity(entity_id)
    
    def find_entity_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find a path between two entities in the knowledge graph."""
        return self.knowledge_graph.find_path(source, target)
    
    def get_cross_references(self, verse_ref: str) -> List[Dict]:
        """Get cross-references for a verse using semantic similarity."""
        if not self.cross_ref_engine:
            return []
        
        # Parse verse reference
        parts = verse_ref.split()
        if len(parts) < 2:
            return []
        
        book = parts[0]
        ch_vs = parts[1].split(':')
        
        if len(ch_vs) != 2:
            return []
        
        # Get the verse text
        verse_data = self.get_verse(book, int(ch_vs[0]), int(ch_vs[1]))
        if not verse_data:
            return []
        
        # Find similar verses
        similar = self.cross_ref_engine.find_similar(verse_data['text'], top_k=10)
        
        # Filter out the original verse
        references = []
        for ref, sim in similar:
            if ref != verse_ref and sim > 0.5:  # Threshold for relevance
                references.append({'reference': ref, 'similarity': sim})
        
        return references[:5]  # Return top 5
    
    def _get_sample_bible_data(self) -> Dict:
        """Return sample Bible data for demonstration."""
        return {
            "books": [
                {
                    "name": "Genesis",
                    "testament": "Old Testament",
                    "chapters": 50,
                    "chapters_data": {
                        "1": {
                            "1": "In the beginning God created the heaven and the earth.",
                            "2": "And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.",
                            "3": "And God said, Let there be light: and there was light.",
                            "4": "And God saw the light, that it was good: and God divided the light from the darkness.",
                            "5": "And God called the light Day, and the darkness he called Night. And the evening and the morning were the first day."
                        },
                        "2": {
                            "1": "Thus the heavens and the earth were finished, and all the host of them.",
                            "2": "And on the seventh day God ended his work which he had made; and he rested on the seventh day from all his work which he had made.",
                            "3": "And God blessed the seventh day, and sanctified it: because that in it he had rested from all his work which God created and made."
                        }
                    }
                },
                {
                    "name": "John",
                    "testament": "New Testament",
                    "chapters": 21,
                    "chapters_data": {
                        "1": {
                            "1": "In the beginning was the Word, and the Word was with God, and the Word was God.",
                            "2": "The same was in the beginning with God.",
                            "3": "All things were made by him; and without him was not any thing made that was made.",
                            "4": "In him was life; and the life was the light of men.",
                            "5": "And the light shineth in darkness; and the darkness comprehended it not."
                        }
                    }
                },
                {
                    "name": "Psalms",
                    "testament": "Old Testament",
                    "chapters": 150,
                    "chapters_data": {
                        "23": {
                            "1": "The LORD is my shepherd; I shall not want.",
                            "2": "He maketh me to lie down in green pastures: he leadeth me beside the still waters.",
                            "3": "He restoreth my soul: he leadeth me in the paths of righteousness for his name's sake.",
                            "4": "Yea, though I walk through the valley of the shadow of death, I will fear no evil: for thou art with me; thy rod and thy staff they comfort me.",
                            "5": "Thou preparest a table before me in the presence of mine enemies: thou anointest my head with oil; my cup runneth over.",
                            "6": "Surely goodness and mercy shall follow me all the days of my life: and I will dwell in the house of the LORD for ever."
                        }
                    }
                }
            ]
        }


# Singleton instance
_service_instance = None

def get_bible_service() -> BibleService:
    """Get or create the Bible service singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = BibleService()
    return _service_instance
