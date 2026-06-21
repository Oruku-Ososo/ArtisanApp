import time
import uuid
import logging
from typing import List, Dict, Any, Optional
from pythonjsonlogger import jsonlogger
from fastapi import FastAPI, HTTPException, Request, Response, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from prometheus_fastapi_instrumentator import Instrumentator
import core

# --- Structured JSON Logging Setup ---
logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(message)s %(request_id)s')
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
# Disable uvicorn default handlers to prevent duplicate plain text logs
logging.getLogger("uvicorn.access").handlers = []

# --- App Initialization & Limiter ---
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Greeting & Computation Service Pro",
    description="A highly scalable, observable, and feature-rich API service.",
    version="2.0.0",
    contact={"name": "Engineering Team", "email": "eng@example.com"}
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Middlewares ---

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request ID, Security Headers & Timing Middleware
@app.middleware("http")
async def add_process_time_and_security_headers(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Inject request_id into logger via a simple filter-like approach or adapter (for simplicity, we'll log it directly here)
    logger.info("Request started", extra={"request_id": request_id, "path": request.url.path, "method": request.method})

    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", extra={"request_id": request_id})
        response = JSONResponse(
            status_code=500,
            content={"status": "error", "detail": "Internal Server Error"}
        )
    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    logger.info("Request finished", extra={"request_id": request_id, "status_code": response.status_code, "process_time": process_time})
    return response

# --- Observability ---
Instrumentator().instrument(app).expose(app)

# --- Models ---

class StandardResponse(BaseModel):
    status: str = "success"
    data: Any

class GreetRequest(BaseModel):
    name: str = Field(..., max_length=100, min_length=1)

class BinaryMathRequest(BaseModel):
    a: float
    b: float

class UnaryMathRequest(BaseModel):
    a: float

class IntMathRequest(BaseModel):
    n: int = Field(..., ge=0, le=1000)

class StatsRequest(BaseModel):
    numbers: List[float] = Field(..., max_items=1000)

class TextRequest(BaseModel):
    text: str = Field(..., max_length=10000)

class TransformRequest(BaseModel):
    text: str = Field(..., max_length=10000)
    operation: str = Field(..., pattern="^(uppercase|lowercase|reverse)$")

# --- Routers ---

system_router = APIRouter(tags=["System"])
math_router = APIRouter(prefix="/math", tags=["Math"])
text_router = APIRouter(prefix="/text", tags=["Text"])
utils_router = APIRouter(prefix="/utils", tags=["Utilities"])

# --- System Endpoints ---

@system_router.get("/")
@limiter.limit("50/minute")
async def root(request: Request):
    return StandardResponse(data={"message": "Welcome to the Greeting & Computation Service Pro!"})

@system_router.get("/health")
async def health_check():
    return StandardResponse(data={"status": "healthy"})

@system_router.post("/greet")
@limiter.limit("20/minute")
async def create_greeting(request: Request, payload: GreetRequest):
    try:
        message = core.greet(payload.name)
        return StandardResponse(data={"greeting": message})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Math Endpoints ---

@math_router.post("/add")
async def compute_addition(payload: BinaryMathRequest):
    return StandardResponse(data={"result": core.add_numbers(payload.a, payload.b)})

@math_router.post("/subtract")
async def compute_subtraction(payload: BinaryMathRequest):
    return StandardResponse(data={"result": core.subtract(payload.a, payload.b)})

@math_router.post("/multiply")
async def compute_multiplication(payload: BinaryMathRequest):
    return StandardResponse(data={"result": core.multiply(payload.a, payload.b)})

@math_router.post("/divide")
async def compute_division(payload: BinaryMathRequest):
    try:
        return StandardResponse(data={"result": core.divide(payload.a, payload.b)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@math_router.post("/power")
async def compute_power(payload: BinaryMathRequest):
    try:
        return StandardResponse(data={"result": core.power(payload.a, payload.b)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@math_router.post("/sqrt")
async def compute_sqrt(payload: UnaryMathRequest):
    try:
        return StandardResponse(data={"result": core.sqrt(payload.a)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@math_router.post("/factorial")
async def compute_factorial(payload: IntMathRequest):
    try:
        return StandardResponse(data={"result": core.factorial(payload.n)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@math_router.post("/statistics/mean")
async def compute_mean(payload: StatsRequest):
    try:
        return StandardResponse(data={"result": core.statistics_mean(payload.numbers)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@math_router.post("/statistics/variance")
async def compute_variance(payload: StatsRequest):
    try:
        return StandardResponse(data={"result": core.statistics_variance(payload.numbers)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Text Endpoints ---

@text_router.post("/analyze")
async def analyze_text(payload: TextRequest):
    return StandardResponse(data={"result": core.analyze_text(payload.text)})

@text_router.post("/transform")
async def transform_text(payload: TransformRequest):
    try:
        return StandardResponse(data={"result": core.transform_text(payload.text, payload.operation)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Util Endpoints ---

@utils_router.get("/random-string")
async def random_string(length: int = 16):
    try:
        return StandardResponse(data={"result": core.generate_random_string(length)})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Register Routers
app.include_router(system_router)
app.include_router(math_router)
app.include_router(text_router)
app.include_router(utils_router)
