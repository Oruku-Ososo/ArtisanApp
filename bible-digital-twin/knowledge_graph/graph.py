"""
Knowledge Graph Module

Builds and queries a semantic knowledge graph of biblical entities,
relationships, and concepts.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass


@dataclass
class Entity:
    """Represents an entity in the biblical knowledge graph."""
    id: str
    name: str
    type: str  # person, place, event, concept, object, etc.
    attributes: Dict[str, any]
    references: List[str]  # Bible verse references


@dataclass
class Relationship:
    """Represents a relationship between two entities."""
    source: str
    target: str
    type: str  # born_in, visited, mentioned_in, caused, etc.
    attributes: Dict[str, any]
    references: List[str]


class BiblicalKnowledgeGraph:
    """Knowledge graph for biblical entities and relationships."""
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self.adjacency_list: Dict[str, Set[str]] = {}
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the graph."""
        self.entities[entity.id] = entity
        if entity.id not in self.adjacency_list:
            self.adjacency_list[entity.id] = set()
    
    def add_relationship(self, relationship: Relationship) -> None:
        """Add a relationship between entities."""
        self.relationships.append(relationship)
        self.adjacency_list.setdefault(relationship.source, set()).add(relationship.target)
        self.adjacency_list.setdefault(relationship.target, set()).add(relationship.source)
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve an entity by ID."""
        return self.entities.get(entity_id)
    
    def get_neighbors(self, entity_id: str) -> List[str]:
        """Get all connected entities."""
        return list(self.adjacency_list.get(entity_id, set()))
    
    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find a path between two entities using BFS."""
        if source not in self.entities or target not in self.entities:
            return None
        
        visited = {source}
        queue = [(source, [source])]
        
        while queue:
            current, path = queue.pop(0)
            
            if current == target:
                return path
            
            for neighbor in self.adjacency_list.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def query_by_type(self, entity_type: str) -> List[Entity]:
        """Find all entities of a specific type."""
        return [e for e in self.entities.values() if e.type == entity_type]
    
    def query_by_reference(self, verse_ref: str) -> List[Entity]:
        """Find all entities mentioned in a specific verse."""
        return [e for e in self.entities.values() if verse_ref in e.references]


class OntologyBuilder:
    """Build ontologies for biblical concepts and categories."""
    
    def __init__(self):
        self.hierarchy: Dict[str, List[str]] = {}
    
    def add_concept(self, concept: str, parent: Optional[str] = None) -> None:
        """Add a concept to the ontology hierarchy."""
        if parent is None:
            if concept not in self.hierarchy:
                self.hierarchy[concept] = []
        else:
            self.hierarchy.setdefault(parent, []).append(concept)
    
    def get_children(self, concept: str) -> List[str]:
        """Get child concepts."""
        return self.hierarchy.get(concept, [])
    
    def get_ancestors(self, concept: str) -> List[str]:
        """Get all ancestor concepts."""
        ancestors = []
        for parent, children in self.hierarchy.items():
            if concept in children:
                ancestors.append(parent)
                ancestors.extend(self.get_ancestors(parent))
        return ancestors
