"""
Tests for Bible Digital Twin
"""

import pytest


def test_imports():
    """Test that core modules can be imported."""
    try:
        from data.loader import BibleDataLoader, TextPreprocessor
        from knowledge_graph.graph import BiblicalKnowledgeGraph, Entity, Relationship
        from models.embeddings import BiblicalEmbeddingModel, CrossReferenceEngine
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_data_loader_initialization():
    """Test BibleDataLoader initialization."""
    from data.loader import BibleDataLoader
    
    loader = BibleDataLoader()
    assert loader.data_dir == "./data"
    assert loader.books == []
    assert isinstance(loader.chapters, dict)
    assert isinstance(loader.verses, dict)


def test_knowledge_graph_basic():
    """Test basic knowledge graph operations."""
    from knowledge_graph.graph import BiblicalKnowledgeGraph, Entity, Relationship
    
    graph = BiblicalKnowledgeGraph()
    
    # Add entities
    entity1 = Entity(
        id="peter",
        name="Peter",
        type="person",
        attributes={"occupation": "fisherman"},
        references=["Matthew 4:18"]
    )
    
    entity2 = Entity(
        id="jesus",
        name="Jesus",
        type="person",
        attributes={},
        references=["Matthew 1:1"]
    )
    
    graph.add_entity(entity1)
    graph.add_entity(entity2)
    
    # Test retrieval
    assert graph.get_entity("peter") is not None
    assert graph.get_entity("peter").name == "Peter"
    
    # Add relationship
    rel = Relationship(
        source="peter",
        target="jesus",
        type="followed",
        attributes={},
        references=["Matthew 4:20"]
    )
    graph.add_relationship(rel)
    
    # Test neighbors
    neighbors = graph.get_neighbors("peter")
    assert "jesus" in neighbors


def test_preprocessor():
    """Test text preprocessing."""
    from data.loader import TextPreprocessor
    
    processor = TextPreprocessor()
    
    # Test cleaning
    messy_text = "  Hello   world  "
    clean = processor.clean_text(messy_text)
    assert clean == "Hello world"
    
    # Test tokenization
    tokens = processor.tokenize("The quick brown fox")
    assert len(tokens) == 4
    assert tokens[0] == "The"
