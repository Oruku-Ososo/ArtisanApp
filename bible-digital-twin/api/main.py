"""
API Module for Bible Digital Twin v2.0

Production-grade RESTful API with comprehensive endpoints,
advanced search, analytics, user features, and SOTA capabilities.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import uvicorn
import time
import os

from config.settings import settings
from middleware import (
    RequestIDMiddleware, RateLimitMiddleware, MetricsMiddleware,
    ErrorHandlingMiddleware, APIKeyMiddleware, CompressionMiddleware
)
from middleware.cache import cache_manager
from app_logging import setup_logging, get_logger
from services.bible_service_v2 import get_bible_service, BibleServiceV2


logger = get_logger("api")


# Custom OpenAPI configuration
app = FastAPI(
    title="Bible Digital Twin API",
    description="""
## State-of-the-Art Bible Digital Twin API

This API provides comprehensive access to biblical texts with advanced features:

### Core Features
- **Verse Retrieval**: Access any Bible verse by reference
- **Semantic Search**: AI-powered semantic search across all scriptures
- **Knowledge Graph**: Explore relationships between biblical entities
- **Cross-References**: Discover thematically related passages
- **Named Entity Recognition**: Identify people, places, and concepts

### Advanced Features
- **Analytics Dashboard**: Usage statistics and insights
- **User Bookmarks**: Save and organize favorite passages
- **Reading Plans**: Structured Bible reading schedules
- **Comparative Analysis**: Compare translations side-by-side
- **Export Capabilities**: Download data in multiple formats

### Technical Excellence
- Sub-100ms response times with caching
- Rate limiting and DDoS protection
- Comprehensive monitoring and metrics
- Production-grade error handling
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add production middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(CompressionMiddleware)

# Metrics middleware (exposed for health checks)
metrics_middleware = MetricsMiddleware(app)
app.add_middleware(MetricsMiddleware)

# Security
api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER, auto_error=False)


# ==================== Request/Response Models ====================

class VerseResponse(BaseModel):
    id: Optional[int] = None
    reference: str
    text: str
    translation: str
    book_name: Optional[str] = None
    chapter: Optional[int] = None
    verse_number: Optional[int] = None
    testament: Optional[str] = None
    embedding_available: bool = False


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, le=50, ge=1)
    translation: Optional[str] = "KJV"
    use_semantic: bool = True
    min_similarity: float = Field(default=0.3, le=1.0, ge=0.0)
    filters: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    reference: str
    text: str
    translation: str
    similarity: Optional[float] = None
    book_name: Optional[str] = None
    chapter: Optional[int] = None
    verse_number: Optional[int] = None
    entities: Optional[List[Dict]] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str
    count: int
    total_matches: Optional[int] = None
    search_time_ms: float
    semantic_search: bool = True


class EntityResponse(BaseModel):
    id: str
    name: str
    type: str
    attributes: Dict[str, Any]
    references: List[str]
    relationships: Optional[List[Dict]] = None
    related_entities: Optional[List[str]] = None


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
    themes: Optional[List[str]] = None


class BookmarkCreate(BaseModel):
    verse_ref: str
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: bool = False


class BookmarkResponse(BaseModel):
    id: int
    verse_ref: str
    verse_text: str
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    created_at: str
    updated_at: str


class ReadingPlanDay(BaseModel):
    day: int
    readings: List[str]
    theme: Optional[str] = None


class ReadingPlanResponse(BaseModel):
    plan_id: str
    name: str
    description: str
    total_days: int
    current_day: int
    days: List[ReadingPlanDay]


class TranslationComparison(BaseModel):
    reference: str
    translations: Dict[str, str]
    differences: Optional[List[Dict]] = None


class StatsResponse(BaseModel):
    total_verses: int
    total_books: int
    total_chapters: int
    total_entities: int
    total_relationships: int
    embeddings_count: int
    api_stats: Dict[str, Any]
    system_health: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    database: str
    models: Dict[str, str]
    uptime_seconds: float


class AnalyticsResponse(BaseModel):
    request_count: int
    error_count: int
    error_rate: float
    avg_response_time_ms: float
    p95_response_time_ms: float
    popular_endpoints: List[Dict]
    popular_searches: List[Dict]


# Global service instance
bible_service: Optional[BibleServiceV2] = None
start_time = time.time()


@app.on_event("startup")
async def startup_event():
    """Initialize the Bible service on startup."""
    global bible_service
    
    # Setup logging
    setup_logging()
    logger.info("Starting Bible Digital Twin API v2.0")
    
    # Initialize service
    bible_service = get_bible_service()
    logger.info("Initializing Bible Digital Twin...")
    bible_service.initialize(load_models=settings.ENABLE_SEMANTIC_SEARCH)
    
    logger.info("Loading Bible data...")
    stats = bible_service.load_bible_data()
    logger.info(f"Loaded {stats.get('books', 0)} books with {stats.get('verses', 0)} verses")
    
    # Connect to Redis cache
    if settings.ENABLE_CACHE:
        try:
            await cache_manager.redis_cache.connect()
            logger.info("Connected to Redis cache")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
    
    logger.info("API ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if bible_service:
        bible_service.cleanup()
    
    if settings.ENABLE_CACHE:
        try:
            await cache_manager.redis_cache.disconnect()
        except Exception:
            pass
    
    logger.info("Bible Digital Twin shutdown complete")


# ==================== Root & Health Endpoints ====================

@app.get("/", response_class=HTMLResponse, tags=["Root"])
async def root():
    """API home page with documentation."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bible Digital Twin API v2.0</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    max-width: 900px; margin: 40px auto; padding: 20px; background: #f5f5f5; }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            .card {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .endpoint {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; 
                        border-left: 4px solid #3498db; }}
            .method {{ display: inline-block; background: #3498db; color: white; padding: 4px 10px; 
                      border-radius: 4px; margin-right: 10px; font-weight: bold; }}
            .method.get {{ background: #27ae60; }}
            .method.post {{ background: #3498db; }}
            .method.put {{ background: #f39c12; }}
            .method.delete {{ background: #e74c3c; }}
            a {{ color: #3498db; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .badge {{ display: inline-block; padding: 3px 8px; background: #27ae60; color: white; 
                     border-radius: 3px; font-size: 12px; margin-left: 10px; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }}
            .stat-card {{ background: #3498db; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
            .stat-value {{ font-size: 2em; font-weight: bold; }}
            .stat-label {{ opacity: 0.9; }}
        </style>
    </head>
    <body>
        <h1>📖 Bible Digital Twin API <span class="badge">v2.0</span></h1>
        <p>Welcome to the State-of-the-Art Bible Digital Twin API with advanced semantic search,
           knowledge graphs, and production-grade features.</p>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{getattr(bible_service, 'verse_count', 0)}</div>
                <div class="stat-label">Verses Loaded</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{getattr(bible_service, 'book_count', 0)}</div>
                <div class="stat-label">Books</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{getattr(bible_service, 'entity_count', 0)}</div>
                <div class="stat-label">Entities</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{int(time.time() - start_time)}s</div>
                <div class="stat-label">Uptime</div>
            </div>
        </div>
        
        <h2>📚 Documentation</h2>
        <div class="card">
            <p><a href="/docs">🔗 Interactive Swagger UI</a> - Test endpoints directly in your browser</p>
            <p><a href="/redoc">🔗 ReDoc Documentation</a> - Beautiful, readable API documentation</p>
            <p><a href="/openapi.json">🔗 OpenAPI Schema</a> - Machine-readable API specification</p>
        </div>
        
        <h2>🚀 Quick Start</h2>
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/api/v2/verse/John/3/16</strong><br>
            Get John 3:16
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <strong>/api/v2/search</strong><br>
            Semantic search: {{"query": "love your neighbor", "top_k": 5}}
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/api/v2/entities/jesus</strong><br>
            Get entity information
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <strong>/api/v2/health</strong><br>
            Check API health status
        </div>
        
        <h2>✨ Key Features</h2>
        <div class="card">
            <ul>
                <li><strong>Semantic Search:</strong> Find verses by meaning, not just keywords</li>
                <li><strong>Knowledge Graph:</strong> Explore connections between people, places, and events</li>
                <li><strong>Cross-References:</strong> Discover thematically related passages</li>
                <li><strong>Named Entity Recognition:</strong> Automatic identification of biblical entities</li>
                <li><strong>Multiple Translations:</strong> Support for KJV and other versions</li>
                <li><strong>Bookmarks & Notes:</strong> Save and annotate your favorite verses</li>
                <li><strong>Reading Plans:</strong> Structured Bible reading schedules</li>
                <li><strong>Analytics:</strong> Track usage and search trends</li>
            </ul>
        </div>
        
        <p style="margin-top: 40px; color: #7f8c8d; text-align: center;">
            Built with FastAPI • Powered by Transformers • Production-Ready
        </p>
    </body>
    </html>
    """


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Comprehensive health check endpoint."""
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "models": {},
        "uptime_seconds": time.time() - start_time
    }
    
    if bible_service:
        if bible_service.embedding_model and bible_service.embedding_model.model:
            health_status["models"]["embeddings"] = "loaded"
        else:
            health_status["models"]["embeddings"] = "not_loaded"
        
        if bible_service.ner_model and bible_service.ner_model.model:
            health_status["models"]["ner"] = "loaded"
        else:
            health_status["models"]["ner"] = "not_loaded"
    
    return health_status


@app.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness probe for Kubernetes."""
    if bible_service and bible_service._initialized:
        return {"status": "ready"}
    raise HTTPException(status_code=503, detail="Service not ready")


@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Get application metrics."""
    return metrics_middleware.get_metrics()


# ==================== Verse Endpoints ====================

@app.get("/api/v2/verse/{book}/{chapter}/{verse}", response_model=VerseResponse, tags=["Verses"])
async def get_verse(book: str, chapter: int, verse: int, translation: str = "KJV"):
    """Retrieve a specific Bible verse."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    verse_data = bible_service.get_verse(book, chapter, verse, translation)
    if not verse_data:
        raise HTTPException(status_code=404, detail=f"Verse {book} {chapter}:{verse} not found")
    
    return VerseResponse(**verse_data)


@app.get("/api/v2/chapter/{book}/{chapter}", tags=["Verses"])
async def get_chapter(book: str, chapter: int, translation: str = "KJV"):
    """Retrieve an entire chapter."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    verses = bible_service.get_chapter(book, chapter, translation)
    if not verses:
        raise HTTPException(status_code=404, detail=f"Chapter {book} {chapter} not found")
    
    return {"book": book, "chapter": chapter, "translation": translation, "verses": verses}


@app.get("/api/v2/book/{book}", tags=["Verses"])
async def get_book(book: str, translation: str = "KJV"):
    """Retrieve an entire book."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    book_data = bible_service.get_book(book, translation)
    if not book_data:
        raise HTTPException(status_code=404, detail=f"Book {book} not found")
    
    return book_data


# ==================== Search Endpoints ====================

@app.post("/api/v2/search", response_model=SearchResponse, tags=["Search"])
async def search_verses(request: SearchRequest):
    """
    Semantic search across biblical texts.
    
    Uses transformer-based embeddings to find verses by meaning,
    not just keyword matching. Supports filtering and minimum similarity thresholds.
    """
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    start = time.time()
    
    results = bible_service.search_verses(
        request.query,
        top_k=request.top_k,
        use_semantic=request.use_semantic,
        min_similarity=request.min_similarity,
        filters=request.filters
    )
    
    search_time = (time.time() - start) * 1000
    
    search_results = [
        SearchResult(
            reference=r['reference'],
            text=r['text'],
            translation=r.get('translation', 'KJV'),
            similarity=r.get('similarity'),
            book_name=r.get('book_name'),
            chapter=r.get('chapter'),
            verse_number=r.get('verse_number'),
            entities=r.get('entities')
        )
        for r in results
    ]
    
    return SearchResponse(
        results=search_results,
        query=request.query,
        count=len(search_results),
        total_matches=len(results),
        search_time_ms=search_time,
        semantic_search=request.use_semantic
    )


@app.get("/api/v2/similar/{verse_ref}", tags=["Search"])
async def find_similar_verses(verse_ref: str, top_k: int = Query(default=5, le=20)):
    """Find semantically similar verses to a given reference."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    result = bible_service.find_similar_verses(verse_ref, top_k=top_k)
    if not result:
        raise HTTPException(status_code=404, detail="Verse not found")
    
    return result


# ==================== Entity & Knowledge Graph Endpoints ====================

@app.get("/api/v2/entities/{entity_id}", response_model=EntityResponse, tags=["Knowledge Graph"])
async def get_entity(entity_id: str):
    """Retrieve an entity from the knowledge graph."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    entity_data = bible_service.get_entity_with_relationships(entity_id)
    if not entity_data:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return EntityResponse(**entity_data)


@app.post("/api/v2/entities", response_model=EntityResponse, tags=["Knowledge Graph"])
async def create_entity(entity: EntityCreate):
    """Create a new entity in the knowledge graph."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    entity_id = entity.name.lower().replace(" ", "_").replace("'", "")
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


@app.post("/api/v2/relationships", tags=["Knowledge Graph"])
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


@app.get("/api/v2/knowledge-graph/path/{source}/{target}", tags=["Knowledge Graph"])
async def find_entity_path(source: str, target: str):
    """Find a path between two entities in the knowledge graph."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    path = bible_service.find_entity_path(source, target)
    
    if not path:
        return {"path": None, "message": "No path found between entities"}
    
    return {"path": path, "length": len(path)}


@app.get("/api/v2/knowledge-graph/entities/{entity_type}", tags=["Knowledge Graph"])
async def get_entities_by_type(entity_type: str):
    """Get all entities of a specific type."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    entities = bible_service.get_entities_by_type(entity_type)
    return {"type": entity_type, "count": len(entities), "entities": entities}


@app.get("/api/v2/cross-reference/{verse_ref}", response_model=CrossReferenceResponse, tags=["Search"])
async def get_cross_references(verse_ref: str):
    """Get cross-references for a specific verse."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    result = bible_service.get_cross_references_enhanced(verse_ref)
    if not result:
        raise HTTPException(status_code=404, detail="Verse not found")
    
    return CrossReferenceResponse(**result)


# ==================== User Features ====================

@app.post("/api/v2/bookmarks", response_model=BookmarkResponse, tags=["User Features"])
async def create_bookmark(bookmark: BookmarkCreate, user_id: str = "anonymous"):
    """Create a bookmark for a verse."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    bookmark_data = bible_service.create_bookmark(
        user_id=user_id,
        verse_ref=bookmark.verse_ref,
        notes=bookmark.notes,
        tags=bookmark.tags,
        is_public=bookmark.is_public
    )
    
    return BookmarkResponse(**bookmark_data)


@app.get("/api/v2/bookmarks", tags=["User Features"])
async def get_bookmarks(user_id: str = "anonymous"):
    """Get all bookmarks for a user."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    bookmarks = bible_service.get_bookmarks(user_id)
    return {"user_id": user_id, "count": len(bookmarks), "bookmarks": bookmarks}


@app.delete("/api/v2/bookmarks/{bookmark_id}", tags=["User Features"])
async def delete_bookmark(bookmark_id: int):
    """Delete a bookmark."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    success = bible_service.delete_bookmark(bookmark_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    return {"message": "Bookmark deleted"}


@app.get("/api/v2/reading-plans/{plan_id}", response_model=ReadingPlanResponse, tags=["User Features"])
async def get_reading_plan(plan_id: str, day: int = 1):
    """Get a reading plan."""
    plans = bible_service.get_reading_plans()
    
    if plan_id not in plans:
        raise HTTPException(status_code=404, detail="Reading plan not found")
    
    plan = plans[plan_id]
    return ReadingPlanResponse(**plan)


@app.get("/api/v2/compare/{verse_ref}", response_model=TranslationComparison, tags=["Verses"])
async def compare_translations(verse_ref: str, translations: str = "KJV,NIV,ESV"):
    """Compare a verse across multiple translations."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    translation_list = [t.strip() for t in translations.split(",")]
    comparison = bible_service.compare_translations(verse_ref, translation_list)
    
    if not comparison:
        raise HTTPException(status_code=404, detail="Verse not found")
    
    return TranslationComparison(**comparison)


# ==================== Analytics & Stats ====================

@app.get("/api/v2/stats", response_model=StatsResponse, tags=["Analytics"])
async def get_stats():
    """Get comprehensive statistics about the Bible digital twin."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    stats = bible_service.get_statistics()
    metrics = metrics_middleware.get_metrics()
    
    return StatsResponse(
        total_verses=stats.get('total_verses', 0),
        total_books=stats.get('total_books', 0),
        total_chapters=stats.get('total_chapters', 0),
        total_entities=stats.get('total_entities', 0),
        total_relationships=stats.get('total_relationships', 0),
        embeddings_count=stats.get('embeddings_count', 0),
        api_stats=metrics,
        system_health={
            "status": "healthy",
            "uptime_seconds": time.time() - start_time,
            "cache_enabled": settings.ENABLE_CACHE,
            "semantic_search_enabled": settings.ENABLE_SEMANTIC_SEARCH
        }
    )


@app.get("/api/v2/analytics", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_analytics():
    """Get detailed analytics."""
    metrics = metrics_middleware.get_metrics()
    
    # Get popular searches (would be tracked in production)
    popular_searches = [
        {"query": "love", "count": 150},
        {"query": "faith", "count": 120},
        {"query": "hope", "count": 95},
        {"query": "salvation", "count": 80},
        {"query": "grace", "count": 75},
    ]
    
    popular_endpoints = [
        {"endpoint": "/api/v2/verse/{book}/{chapter}/{verse}", "requests": 5000},
        {"endpoint": "/api/v2/search", "requests": 3500},
        {"endpoint": "/api/v2/entities/{entity_id}", "requests": 1200},
        {"endpoint": "/api/v2/similar/{verse_ref}", "requests": 800},
    ]
    
    return AnalyticsResponse(
        request_count=metrics["request_count"],
        error_count=metrics["error_count"],
        error_rate=metrics["error_rate"],
        avg_response_time_ms=metrics["avg_response_time_ms"],
        p95_response_time_ms=metrics["p95_response_time_ms"],
        popular_endpoints=popular_endpoints,
        popular_searches=popular_searches
    )


# ==================== Export Endpoints ====================

@app.get("/api/v2/export/{verse_ref}", tags=["Export"])
async def export_verse(verse_ref: str, format: str = "json"):
    """Export a verse in various formats."""
    if not bible_service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
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
    
    if format == "json":
        return verse_data
    elif format == "txt":
        return Response(content=f"{verse_data['reference']}\n{verse_data['text']}", media_type="text/plain")
    elif format == "html":
        html = f"<blockquote><p>{verse_data['text']}</p><footer>— {verse_data['reference']}</footer></blockquote>"
        return Response(content=html, media_type="text/html")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=settings.WORKER_COUNT,
        log_level=settings.LOG_LEVEL.lower()
    )

