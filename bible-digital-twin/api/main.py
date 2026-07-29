"""
API Module

RESTful API for the Bible Digital Twin using FastAPI.
Provides endpoints for verse retrieval, semantic search, entity lookup,
and knowledge graph queries.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

from services.bible_service import get_bible_service, BibleService


app = FastAPI(
    title="Bible Digital Twin API",
    description="State-of-the-Art API for biblical text analysis, semantic search, and knowledge graph queries",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
bible_service: Optional[BibleService] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the Bible service on startup."""
    global bible_service
    bible_service = get_bible_service()
    print("Initializing Bible Digital Twin...")
    # Initialize without loading heavy models by default
    bible_service.initialize(load_models=False)
    print("Loading sample Bible data...")
    bible_service.load_bible_data()
    print("API ready!")


class VerseResponse(BaseModel):
    reference: str
    text: str
    translation: str
    id: Optional[int] = None


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    translation: Optional[str] = "KJV"
    use_semantic: bool = True


class SearchResult(BaseModel):
    reference: str
    text: str
    translation: str
    similarity: Optional[float] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    count: int


class EntityResponse(BaseModel):
    id: str
    name: str
    type: str
    attributes: Dict[str, Any]
    references: List[str]


class EntityCreate(BaseModel):
    name: str
    type: str
    attributes: Optional[Dict[str, Any]] = None
    references: Optional[List[str]] = None


class RelationshipCreate(BaseModel):
    source_id: str
    target_id: str
    type: str
    attributes: Optional[Dict[str, Any]] = None
    references: Optional[List[str]] = None


class CrossReferenceResponse(BaseModel):
    verse_ref: str
    text: str
    references: List[Dict[str, Any]]


@app.get("/", response_class=HTMLResponse)
async def root():
    """API health check and info with HTML response."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bible Digital Twin API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #2c3e50; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .method { display: inline-block; background: #3498db; color: white; padding: 3px 8px; border-radius: 3px; margin-right: 10px; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>📖 Bible Digital Twin API</h1>
        <p>Welcome to the State-of-the-Art Bible Digital Twin API!</p>
        
        <h2>Available Endpoints:</h2>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <strong>/verse/{book}/{chapter}/{verse}</strong><br>
            Retrieve a specific Bible verse
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span>
            <strong>/search</strong><br>
            Semantic search across biblical texts
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <strong>/entities/{entity_id}</strong><br>
            Retrieve an entity from the knowledge graph
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span>
            <strong>/entities</strong><br>
            Create a new entity in the knowledge graph
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <strong>/similar/{verse_ref}</strong><br>
            Find semantically similar verses
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <strong>/cross-reference/{verse_ref}</strong><br>
            Get cross-references for a verse
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <strong>/knowledge-graph/path/{source}/{target}</strong><br>
            Find relationships between entities
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span>
            <strong>/docs</strong><br>
            Interactive API documentation (Swagger UI)
        </div>
        
        <p><a href="/docs">View interactive documentation →</a></p>
    </body>
    </html>
    """


@app.get("/api/verse/{book}/{chapter}/{verse}", response_model=VerseResponse)
async def get_verse(book: str, chapter: int, verse: int, translation: str = "KJV"):
    """Retrieve a specific Bible verse."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    verse_data = bible_service.get_verse(book, chapter, verse, translation)
    if not verse_data:
        raise HTTPException(
            status_code=404, 
            detail=f"Verse {book} {chapter}:{verse} not found"
        )
    
    return VerseResponse(**verse_data)


@app.post("/api/search", response_model=SearchResponse)
async def search_verses(request: SearchRequest):
    """Semantic search across biblical texts."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    results = bible_service.search_verses(
        request.query, 
        top_k=request.top_k,
        use_semantic=request.use_semantic
    )
    
    search_results = [
        SearchResult(
            reference=r['reference'],
            text=r['text'],
            translation=r.get('translation', 'KJV'),
            similarity=r.get('similarity')
        )
        for r in results
    ]
    
    return SearchResponse(
        results=search_results,
        query=request.query,
        count=len(search_results)
    )


@app.get("/api/entities/{entity_id}", response_model=EntityResponse)
async def get_entity(entity_id: str):
    """Retrieve an entity from the knowledge graph."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    entity_data = bible_service.get_entity(entity_id)
    if not entity_data:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return EntityResponse(**entity_data)


@app.post("/api/entities", response_model=EntityResponse)
async def create_entity(entity: EntityCreate):
    """Create a new entity in the knowledge graph."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    entity_id = entity.name.lower().replace(" ", "_")
    bible_service.add_entity_to_graph(
        entity_id=entity_id,
        name=entity.name,
        type=entity.type,
        attributes=entity.attributes or {},
        references=entity.references or []
    )
    
    return EntityResponse(
        id=entity_id,
        name=entity.name,
        type=entity.type,
        attributes=entity.attributes or {},
        references=entity.references or []
    )


@app.post("/api/relationships")
async def create_relationship(relationship: RelationshipCreate):
    """Create a relationship between two entities."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    bible_service.add_relationship(
        source_id=relationship.source_id,
        target_id=relationship.target_id,
        rel_type=relationship.type,
        attributes=relationship.attributes,
        references=relationship.references
    )
    
    return {"message": "Relationship created successfully"}


@app.get("/api/similar/{verse_ref}")
async def find_similar_verses(verse_ref: str, top_k: int = Query(default=5, le=20)):
    """Find semantically similar verses to a given reference."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Get the original verse
    parts = verse_ref.split()
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid verse reference format")
    
    book = parts[0]
    ch_vs = parts[1].split(':')
    
    if len(ch_vs) != 2:
        raise HTTPException(status_code=400, detail="Invalid verse reference format")
    
    verse_data = bible_service.get_verse(book, int(ch_vs[0]), int(ch_vs[1]))
    if not verse_data:
        raise HTTPException(status_code=404, detail="Verse not found")
    
    # Find similar verses
    similar = bible_service.search_verses(verse_data['text'], top_k=top_k + 1)
    
    # Filter out the original verse
    results = [
        {**r, 'similarity': r.get('similarity', 0.0)}
        for r in similar 
        if r['reference'] != verse_ref
    ][:top_k]
    
    return {
        "verse_ref": verse_ref,
        "text": verse_data['text'],
        "similar_verses": results
    }


@app.get("/api/cross-reference/{verse_ref}", response_model=CrossReferenceResponse)
async def get_cross_references(verse_ref: str):
    """Get cross-references for a specific verse."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Parse verse reference
    parts = verse_ref.split()
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid verse reference format")
    
    book = parts[0]
    ch_vs = parts[1].split(':')
    
    if len(ch_vs) != 2:
        raise HTTPException(status_code=400, detail="Invalid verse reference format")
    
    verse_data = bible_service.get_verse(book, int(ch_vs[0]), int(ch_vs[1]))
    if not verse_data:
        raise HTTPException(status_code=404, detail="Verse not found")
    
    references = bible_service.get_cross_references(verse_ref)
    
    return CrossReferenceResponse(
        verse_ref=verse_ref,
        text=verse_data['text'],
        references=references
    )


@app.get("/api/knowledge-graph/path/{source}/{target}")
async def find_entity_path(source: str, target: str):
    """Find a path between two entities in the knowledge graph."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    path = bible_service.find_entity_path(source, target)
    
    if not path:
        return {"path": None, "message": "No path found between entities"}
    
    return {"path": path, "length": len(path)}


@app.get("/api/knowledge-graph/entities/{entity_type}")
async def get_entities_by_type(entity_type: str):
    """Get all entities of a specific type."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    entities = bible_service.db.get_entities_by_type(entity_type)
    return {"type": entity_type, "count": len(entities), "entities": entities}


@app.get("/api/stats")
async def get_stats():
    """Get statistics about the Bible digital twin."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    # Simple stats - can be enhanced with database queries
    return {
        "status": "active",
        "features": [
            "Verse retrieval",
            "Semantic search",
            "Named entity recognition",
            "Knowledge graph",
            "Cross-referencing"
        ]
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

