"""
AI Models Module

Implements state-of-the-art transformer models for biblical text analysis,
including semantic search, entity recognition, and cross-referencing.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np


class BiblicalEmbeddingModel:
    """Generate embeddings for biblical texts using transformer models."""
    
    def __init__(self, model_name: str = "bert-base-uncased"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
    
    def load_model(self) -> None:
        """Load the transformer model and tokenizer."""
        try:
            from transformers import AutoModel, AutoTokenizer
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
        except ImportError:
            print("Transformers library not installed. Run: pip install transformers")
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts into vector embeddings."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        outputs = self.model(**inputs)
        
        # Use CLS token embeddings or mean pooling
        embeddings = outputs.last_hidden_state[:, 0, :]
        return embeddings.detach().numpy()
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts."""
        emb1 = self.encode([text1])[0]
        emb2 = self.encode([text2])[0]
        
        cosine_sim = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(cosine_sim)


class CrossReferenceEngine:
    """Find semantically related passages across the Bible."""
    
    def __init__(self, embedding_model: BiblicalEmbeddingModel):
        self.embedding_model = embedding_model
        self.verse_embeddings: Dict[str, np.ndarray] = {}
        self.verse_index: Dict[int, str] = {}
    
    def index_verses(self, verses: Dict[str, str]) -> None:
        """Index all verses for fast similarity search."""
        verse_ids = list(verses.keys())
        verse_texts = list(verses.values())
        
        embeddings = self.embedding_model.encode(verse_texts)
        
        for i, verse_id in enumerate(verse_ids):
            self.verse_embeddings[verse_id] = embeddings[i]
            self.verse_index[len(self.verse_index)] = verse_id
    
    def find_similar(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find the most similar verses to a query."""
        query_embedding = self.embedding_model.encode([query])[0]
        
        similarities = []
        for verse_id, embedding in self.verse_embeddings.items():
            sim = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities.append((verse_id, float(sim)))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]


class NamedEntityRecognizer:
    """Identify biblical entities (people, places, events) in text."""
    
    def __init__(self):
        self.model = None
        self.entity_types = ["PERSON", "LOCATION", "EVENT", "OBJECT", "CONCEPT"]
    
    def load_model(self) -> None:
        """Load NER model (to be implemented with spaCy or custom model)."""
        try:
            import spacy
            self.model = spacy.load("en_core_web_sm")
        except ImportError:
            print("spaCy not installed. Run: pip install spacy && python -m spacy download en_core_web_sm")
    
    def extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities from text."""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        doc = self.model(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return entities
