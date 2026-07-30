"""
AI Services Module - Enhancements #9-18
#9: Multi-Model Embedding Support
#10: Hybrid Search (Semantic + Keyword)
#11: Named Entity Recognition Pipeline
#12: Text Summarization
#13: Sentiment Analysis
#14: Topic Modeling
#15: Cross-Reference Engine
#16: Semantic Similarity Clustering
#17: Question Answering
#18: Language Detection
"""
from typing import List, Dict, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer, util
import spacy
from sklearn.cluster import KMeans
import numpy as np
from collections import Counter

class MultiEmbeddingService:
    """Enhancement #9: Multi-Model Embedding Support"""
    
    MODELS = {
        "mini": "sentence-transformers/all-MiniLM-L6-v2",
        "mpnet": "sentence-transformers/all-mpnet-base-v2",
        "multi-qa": "sentence-transformers/multi-qa-mpnet-base-dot-v1"
    }
    
    def __init__(self, model_name: str = "mini"):
        self.model_name = model_name
        self.model = SentenceTransformer(self.MODELS.get(model_name, self.MODELS["mini"]))
    
    def encode(self, texts: List[str], **kwargs) -> np.ndarray:
        """Encode texts to embeddings"""
        return self.model.encode(texts, convert_to_numpy=True, **kwargs)
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity"""
        return util.cos_sim(embedding1, embedding2).item()

class HybridSearchEngine:
    """Enhancement #10: Hybrid Search (Semantic + Keyword)"""
    
    def __init__(self, embedding_service: MultiEmbeddingService):
        self.embedding_service = embedding_service
    
    def search(self, query: str, documents: List[Dict], top_k: int = 5, alpha: float = 0.7) -> List[Dict]:
        """
        Hybrid search combining semantic and keyword matching
        alpha: weight for semantic search (1-alpha for keyword)
        """
        # Semantic search
        query_embedding = self.embedding_service.encode([query])[0]
        doc_embeddings = self.embedding_service.encode([doc["text"] for doc in documents])
        semantic_scores = util.cos_sim(query_embedding, doc_embeddings)[0].tolist()
        
        # Keyword search (BM25-like simplified)
        keyword_scores = self._keyword_score(query, documents)
        
        # Combine scores
        combined_scores = [
            alpha * sem + (1 - alpha) * kw 
            for sem, kw in zip(semantic_scores, keyword_scores)
        ]
        
        # Rank and return
        ranked_indices = np.argsort(combined_scores)[::-1][:top_k]
        results = []
        for idx in ranked_indices:
            doc = documents[idx].copy()
            doc["score"] = combined_scores[idx]
            doc["semantic_score"] = semantic_scores[idx]
            doc["keyword_score"] = keyword_scores[idx]
            results.append(doc)
        
        return results
    
    def _keyword_score(self, query: str, documents: List[Dict]) -> List[float]:
        """Simple keyword overlap scoring"""
        query_words = set(query.lower().split())
        scores = []
        for doc in documents:
            doc_words = set(doc["text"].lower().split())
            overlap = len(query_words & doc_words)
            scores.append(overlap / max(len(query_words), 1))
        return scores

class NERPipeline:
    """Enhancement #11: Named Entity Recognition Pipeline"""
    
    def __init__(self, model: str = "en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            print(f"SpaCy model '{model}' not found. Install with: python -m spacy download {model}")
            self.nlp = None
    
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "description": self._get_label_description(ent.label_)
            })
        return entities
    
    def _get_label_description(self, label: str) -> str:
        """Get description for entity label"""
        descriptions = {
            "PERSON": "People, including fictional",
            "GPE": "Countries, cities, states",
            "ORG": "Companies, agencies, institutions",
            "LOC": "Non-GPE locations",
            "DATE": "Absolute or relative dates",
            "TIME": "Times smaller than a day",
            "EVENT": "Named hurricanes, battles, wars",
            "WORK_OF_ART": "Titles of books, songs",
            "LAW": "Named documents made into laws"
        }
        return descriptions.get(label, "Unknown entity type")

class TextSummarizer:
    """Enhancement #12: Extractive Text Summarization"""
    
    def summarize(self, text: str, max_sentences: int = 3) -> str:
        """Generate extractive summary"""
        sentences = text.split('.')
        if len(sentences) <= max_sentences:
            return text
        
        # Simple frequency-based scoring
        word_freq = Counter(text.lower().split())
        sentence_scores = []
        
        for sentence in sentences:
            if len(sentence.strip()) < 10:
                continue
            score = sum(word_freq.get(word, 0) for word in sentence.lower().split())
            sentence_scores.append((sentence, score / len(sentence.split())))
        
        # Get top sentences
        top_sentences = sorted(sentence_scores, key=lambda x: x[1], reverse=True)[:max_sentences]
        top_sentences.sort(key=lambda x: sentences.index(x[0]))  # Restore order
        
        return '. '.join([s[0] for s in top_sentences]) + '.'

class SentimentAnalyzer:
    """Enhancement #13: Sentiment Analysis"""
    
    POSITIVE_WORDS = {'love', 'joy', 'peace', 'good', 'light', 'hope', 'faith', 'bless', 'grace', 'mercy'}
    NEGATIVE_WORDS = {'sin', 'death', 'evil', 'darkness', 'fear', 'anger', 'judgment', 'wrath', 'curse'}
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in self.POSITIVE_WORDS)
        negative_count = sum(1 for word in words if word in self.NEGATIVE_WORDS)
        
        total = positive_count + negative_count
        if total == 0:
            sentiment = "neutral"
            confidence = 1.0
        else:
            positive_ratio = positive_count / total
            if positive_ratio > 0.6:
                sentiment = "positive"
                confidence = positive_ratio
            elif positive_ratio < 0.4:
                sentiment = "negative"
                confidence = 1 - positive_ratio
            else:
                sentiment = "mixed"
                confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "positive_score": positive_count,
            "negative_score": negative_count
        }

class TopicModeler:
    """Enhancement #14: Simple Topic Modeling"""
    
    def extract_topics(self, documents: List[str], n_topics: int = 5, n_words: int = 10) -> List[Dict]:
        """Extract topics using simple clustering"""
        # This is a simplified version - production would use LDA or BERTopic
        all_words = ' '.join(documents).lower().split()
        word_freq = Counter(all_words)
        
        # Remove common words
        stop_words = {'the', 'and', 'of', 'in', 'to', 'a', 'is', 'that', 'for', 'it', 'with'}
        filtered_words = {k: v for k, v in word_freq.items() if k not in stop_words and len(k) > 3}
        
        top_words = filtered_words.most_common(n_words * n_topics)
        
        topics = []
        for i in range(n_topics):
            start_idx = i * n_words
            topic_words = [word for word, _ in top_words[start_idx:start_idx + n_words]]
            topics.append({
                "topic_id": i,
                "keywords": topic_words,
                "weight": 1.0 / (i + 1)  # Simplified weighting
            })
        
        return topics

class CrossReferenceEngine:
    """Enhancement #15: Intelligent Cross-Referencing"""
    
    def __init__(self, embedding_service: MultiEmbeddingService):
        self.embedding_service = embedding_service
        self.verse_cache = {}
    
    def find_references(self, verse_text: str, all_verses: List[Dict], top_k: int = 5) -> List[Dict]:
        """Find cross-references based on semantic similarity and themes"""
        verse_embedding = self.embedding_service.encode([verse_text])[0]
        
        candidates = []
        for verse in all_verses:
            if verse["reference"] == self._get_reference_from_text(verse_text):
                continue
            
            verse_emb = self.embedding_service.encode([verse["text"]])[0]
            similarity = util.cos_sim(verse_embedding, verse_emb).item()
            
            # Check for thematic keywords
            theme_score = self._calculate_theme_overlap(verse_text, verse["text"])
            
            combined_score = 0.7 * similarity + 0.3 * theme_score
            candidates.append({
                **verse,
                "similarity_score": similarity,
                "theme_score": theme_score,
                "combined_score": combined_score
            })
        
        # Sort by combined score
        candidates.sort(key=lambda x: x["combined_score"], reverse=True)
        return candidates[:top_k]
    
    def _calculate_theme_overlap(self, text1: str, text2: str) -> float:
        """Calculate thematic keyword overlap"""
        themes = {'covenant', 'promise', 'salvation', 'redemption', 'faith', 'grace', 'law', 'prophecy'}
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        overlap = len((words1 | words2) & themes)
        return min(overlap / 5.0, 1.0)
    
    def _get_reference_from_text(self, text: str) -> Optional[str]:
        """Extract reference from text (simplified)"""
        # In production, this would parse structured data
        return None

class SemanticClusterer:
    """Enhancement #16: Semantic Similarity Clustering"""
    
    def __init__(self, embedding_service: MultiEmbeddingService):
        self.embedding_service = embedding_service
    
    def cluster_verses(self, verses: List[Dict], n_clusters: int = 10) -> List[Dict]:
        """Cluster verses by semantic similarity"""
        texts = [v["text"] for v in verses]
        embeddings = self.embedding_service.encode(texts)
        
        # K-Means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings)
        
        # Group verses by cluster
        clusters = {}
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            verse_copy = verses[i].copy()
            verse_copy["cluster_id"] = int(label)
            clusters[label].append(verse_copy)
        
        return [
            {"cluster_id": cid, "verses": cverses, "size": len(cverses)}
            for cid, cverses in clusters.items()
        ]

class QuestionAnswering:
    """Enhancement #17: Simple Question Answering"""
    
    def answer(self, question: str, context_verses: List[Dict]) -> Optional[Dict]:
        """Find best answer from context verses"""
        # Simplified QA - production would use transformer-based QA
        question_words = set(question.lower().split())
        
        best_match = None
        best_score = 0
        
        for verse in context_verses:
            verse_words = set(verse["text"].lower().split())
            overlap = len(question_words & verse_words)
            score = overlap / len(question_words)
            
            if score > best_score:
                best_score = score
                best_match = verse
        
        if best_match and best_score > 0.2:
            return {
                "answer": best_match["text"],
                "reference": best_match["reference"],
                "confidence": best_score
            }
        
        return None

class LanguageDetector:
    """Enhancement #18: Simple Language Detection"""
    
    LANGUAGE_INDICATORS = {
        "en": ["the", "and", "of", "in", "to"],
        "es": ["el", "la", "de", "en", "y"],
        "fr": ["le", "la", "de", "et", "en"],
        "de": ["der", "die", "und", "in", "zu"]
    }
    
    def detect(self, text: str) -> str:
        """Detect language of text"""
        words = text.lower().split()
        scores = {}
        
        for lang, indicators in self.LANGUAGE_INDICATORS.items():
            count = sum(1 for word in words if word in indicators)
            scores[lang] = count / len(indicators)
        
        return max(scores, key=scores.get) if scores else "en"
