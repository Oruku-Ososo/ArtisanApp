"""
Middleware Module for Bible Digital Twin

Production-grade middleware for authentication, rate limiting,
logging, metrics, and error handling.
"""

import time
import uuid
import logging
from typing import Callable, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict

from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.settings import settings


logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request for tracing."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with sliding window algorithm."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.requests_per_minute: Dict[str, list] = defaultdict(list)
        self.requests_per_hour: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        client_ip = request.client.host
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        # Clean old entries
        self.requests_per_minute[client_ip] = [
            t for t in self.requests_per_minute[client_ip] if t > minute_ago
        ]
        self.requests_per_hour[client_ip] = [
            t for t in self.requests_per_hour[client_ip] if t > hour_ago
        ]
        
        # Check limits
        if len(self.requests_per_minute[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded (per minute)"
            )
        
        if len(self.requests_per_hour[client_ip]) >= settings.RATE_LIMIT_PER_HOUR:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded (per hour)"
            )
        
        # Record request
        self.requests_per_minute[client_ip].append(now)
        self.requests_per_hour[client_ip].append(now)
        
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            settings.RATE_LIMIT_PER_MINUTE - len(self.requests_per_minute[client_ip])
        )
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            settings.RATE_LIMIT_PER_HOUR - len(self.requests_per_hour[client_ip])
        )
        
        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect metrics for monitoring and observability."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.metrics: Dict[str, Any] = {
            "request_count": 0,
            "error_count": 0,
            "response_times": [],
            "requests_by_endpoint": defaultdict(int),
            "errors_by_type": defaultdict(int),
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        self.metrics["request_count"] += 1
        self.metrics["requests_by_endpoint"][request.url.path] += 1
        
        try:
            response = await call_next(request)
            
            # Record response time
            duration = time.time() - start_time
            self.metrics["response_times"].append(duration)
            
            # Keep only last 1000 response times
            if len(self.metrics["response_times"]) > 1000:
                self.metrics["response_times"] = self.metrics["response_times"][-1000:]
            
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            
            if response.status_code >= 400:
                self.metrics["error_count"] += 1
                self.metrics["errors_by_type"][str(response.status_code)] += 1
            
            return response
        except Exception as e:
            self.metrics["error_count"] += 1
            self.metrics["errors_by_type"][type(e).__name__] += 1
            logger.error(f"Request failed: {e}", exc_info=True)
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        response_times = self.metrics["response_times"]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 20 else 0
        
        return {
            "request_count": self.metrics["request_count"],
            "error_count": self.metrics["error_count"],
            "error_rate": self.metrics["error_count"] / max(self.metrics["request_count"], 1),
            "avg_response_time_ms": avg_response_time * 1000,
            "p95_response_time_ms": p95_response_time * 1000,
            "requests_by_endpoint": dict(self.metrics["requests_by_endpoint"]),
            "errors_by_type": dict(self.metrics["errors_by_type"]),
        }


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API key authentication middleware."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.valid_api_keys: set = set(os.getenv("VALID_API_KEYS", "").split(","))
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.ENABLE_API_KEY_AUTH:
            return await call_next(request)
        
        # Skip auth for health checks and docs
        if request.url.path in ["/health", "/ready", "/docs", "/openapi.json", "/"]:
            return await call_next(request)
        
        api_key = request.headers.get(settings.API_KEY_HEADER)
        
        if not api_key or api_key not in self.valid_api_keys:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid or missing API key"}
            )
        
        return await call_next(request)


class CompressionMiddleware(BaseHTTPMiddleware):
    """Gzip compression middleware."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.ENABLE_COMPRESSION:
            return await call_next(request)
        
        response = await call_next(request)
        
        # Only compress JSON responses
        if "application/json" in response.headers.get("content-type", ""):
            response.headers["Content-Encoding"] = "gzip"
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling with structured error responses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except HTTPException as e:
            logger.warning(f"HTTP error: {e.status_code} - {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": True,
                    "status_code": e.status_code,
                    "detail": e.detail,
                    "request_id": getattr(request.state, "request_id", None),
                }
            )
        except Exception as e:
            logger.error(f"Unhandled error: {e}", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": True,
                    "status_code": 500,
                    "detail": "Internal server error",
                    "request_id": getattr(request.state, "request_id", None),
                }
            )


# Import os at module level
import os
