import sys
import os
import time
import signal
import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from settings import get_settings
from utils.logger import setup_logging, get_logger
from utils.middleware import (
    TimingMiddleware,
    SecurityMiddleware,
    RateLimitMiddleware
)

# Setup paths
settings = get_settings()
sys.path.append(str(settings.ROOT_DIR))

try:
    from handler import *
    from qanything_kernel.core.local_doc_qa import LocalDocQA
    from qanything_kernel.utils.custom_log import debug_logger, qa_logger
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure QAnything modules are available in the Python path")
    sys.exit(1)


class QAnythingApp:
    """Main application class for QAnything API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.logger = None
        self.local_doc_qa: Optional[LocalDocQA] = None
        self.startup_time = time.time()
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self):
        """Initialize the application components."""
        self.logger = get_logger(__name__)
        self.logger.info("Starting QAnything API server...")
        
        try:
            # Initialize LocalDocQA
            init_start = time.time()
            self.local_doc_qa = LocalDocQA(self.settings.PORT)
            
            # Create a mock args object for backward compatibility
            class MockArgs:
                def __init__(self, settings):
                    self.host = settings.HOST
                    self.port = settings.PORT
                    self.workers = settings.WORKERS
            
            mock_args = MockArgs(self.settings)
            self.local_doc_qa.init_cfg(mock_args)
            
            init_time = time.time() - init_start
            self.logger.info(f"LocalDocQA initialized in {init_time:.2f}s")
            
            startup_time = time.time() - self.startup_time
            self.logger.info(f"Server startup completed in {startup_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize application: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup application resources."""
        self.logger.info("Shutting down QAnything API server...")
        # Add cleanup logic here if needed
        self._shutdown_event.set()


# Global app instance
app_instance = QAnythingApp()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await app_instance.initialize()
    
    yield
    
    # Shutdown
    await app_instance.cleanup()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    # Setup logging
    setup_logging(
        level=settings.LOG_LEVEL,
        log_dir=settings.LOG_DIR,
        format_str=settings.LOG_FORMAT
    )
    
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )
    
    # Add middleware
    add_middleware(app, settings)
    
    # Add routes
    add_routes(app, settings)
    
    # Add exception handlers
    add_exception_handlers(app)
    
    return app


def add_middleware(app: FastAPI, settings):
    """Add middleware to the application."""
    
    # Security middleware
    app.add_middleware(SecurityMiddleware)
    
    # Trusted host middleware
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]  # Configure this properly in production
        )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # Timing middleware
    app.add_middleware(TimingMiddleware)
    
    # Dependency injection middleware
    @app.middleware("http")
    async def inject_dependencies(request: Request, call_next):
        request.state.local_doc_qa = app_instance.local_doc_qa
        request.state.settings = settings
        response = await call_next(request)
        return response


def add_routes(app: FastAPI, settings):
    """Add API routes to the application."""
    
    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": settings.API_VERSION
        }
    
    # API routes with versioning
    api_prefix = settings.API_V1_PREFIX
    
    # Document-related endpoints
    @app.get(f"{api_prefix}/docs", tags=["Documentation"])
    async def api_document(request: Request):
        return await document(request)
    
    @app.get(f"{api_prefix}/health_check", tags=["Health"])
    async def api_health_check(request: Request):
        return await health_check(request)
    
    # Knowledge base endpoints
    @app.post(f"{api_prefix}/knowledge_base/new", tags=["Knowledge Base"])
    async def api_new_knowledge_base(request: Request):
        return await new_knowledge_base(request)
    
    @app.post(f"{api_prefix}/knowledge_base/list", tags=["Knowledge Base"])
    async def api_list_kbs(request: Request):
        return await list_kbs(request)
    
    @app.post(f"{api_prefix}/knowledge_base/delete", tags=["Knowledge Base"])
    async def api_delete_knowledge_base(request: Request):
        return await delete_knowledge_base(request)
    
    @app.post(f"{api_prefix}/knowledge_base/rename", tags=["Knowledge Base"])
    async def api_rename_knowledge_base(request: Request):
        return await rename_knowledge_base(request)
    
    # File upload endpoints
    @app.post(f"{api_prefix}/upload/weblink", tags=["Upload"])
    async def api_upload_weblink(request: Request):
        return await upload_weblink(request)
    
    @app.post(f"{api_prefix}/upload/files", tags=["Upload"])
    async def api_upload_files(request: Request):
        return await upload_files(request)
    
    @app.post(f"{api_prefix}/upload/faqs", tags=["Upload"])
    async def api_upload_faqs(request: Request):
        return await upload_faqs(request)
    
    # Chat and QA endpoints
    @app.post(f"{api_prefix}/chat", tags=["Chat"])
    async def api_local_doc_chat(request: Request):
        return await local_doc_chat(request)
    
    @app.post(f"{api_prefix}/qa/info", tags=["QA"])
    async def api_get_qa_info(request: Request):
        return await get_qa_info(request)
    
    @app.post(f"{api_prefix}/qa/random", tags=["QA"])
    async def api_get_random_qa(request: Request):
        return await get_random_qa(request)
    
    @app.post(f"{api_prefix}/qa/related", tags=["QA"])
    async def api_get_related_qa(request: Request):
        return await get_related_qa(request)
    
    # File management endpoints
    @app.post(f"{api_prefix}/files/list", tags=["Files"])
    async def api_list_docs(request: Request):
        return await list_docs(request)
    
    @app.post(f"{api_prefix}/files/delete", tags=["Files"])
    async def api_delete_docs(request: Request):
        return await delete_docs(request)
    
    @app.post(f"{api_prefix}/files/base64", tags=["Files"])
    async def api_get_file_base64(request: Request):
        return await get_file_base64(request)
    
    # Document processing endpoints
    @app.post(f"{api_prefix}/doc/completed", tags=["Documents"])
    async def api_get_doc_completed(request: Request):
        return await get_doc_completed(request)
    
    @app.post(f"{api_prefix}/doc/content", tags=["Documents"])
    async def api_get_doc(request: Request):
        return await get_doc(request)
    
    # Search and ranking endpoints
    @app.post(f"{api_prefix}/search/rerank", tags=["Search"])
    async def api_get_rerank_results(request: Request):
        return await get_rerank_results(request)
    
    # Status and monitoring endpoints
    @app.post(f"{api_prefix}/status/total", tags=["Status"])
    async def api_get_total_status(request: Request):
        return await get_total_status(request)
    
    @app.post(f"{api_prefix}/status/user", tags=["Status"])
    async def api_get_user_status(request: Request):
        return await get_user_status(request)
    
    @app.post(f"{api_prefix}/user/id", tags=["User"])
    async def api_get_user_id(request: Request):
        return await get_user_id(request)
    
    # Maintenance endpoints
    @app.post(f"{api_prefix}/maintenance/clean", tags=["Maintenance"])
    async def api_clean_files_by_status(request: Request):
        return await clean_files_by_status(request)
    
    @app.post(f"{api_prefix}/chunks/update", tags=["Maintenance"])
    async def api_update_chunks(request: Request):
        return await update_chunks(request)
    
    # Bot management endpoints
    @app.post(f"{api_prefix}/bot/new", tags=["Bot"])
    async def api_new_bot(request: Request):
        return await new_bot(request)
    
    @app.post(f"{api_prefix}/bot/delete", tags=["Bot"])
    async def api_delete_bot(request: Request):
        return await delete_bot(request)
    
    @app.post(f"{api_prefix}/bot/update", tags=["Bot"])
    async def api_update_bot(request: Request):
        return await update_bot(request)
    
    @app.post(f"{api_prefix}/bot/info", tags=["Bot"])
    async def api_get_bot_info(request: Request):
        return await get_bot_info(request)


def add_exception_handlers(app: FastAPI):
    """Add custom exception handlers."""
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "status_code": exc.status_code,
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "details": exc.errors(),
                "status_code": 422,
                "timestamp": time.time()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger = get_logger(__name__)
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "status_code": 500,
                "timestamp": time.time()
            }
        )


def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        logger = get_logger(__name__)
        logger.info(f"Received signal {signum}, shutting down...")
        # Trigger shutdown
        asyncio.create_task(app_instance.cleanup())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


# Create the FastAPI app
app = create_app()


def run_server():
    """Run the server with production settings."""
    settings = get_settings()
    setup_signal_handlers()
    
    config = uvicorn.Config(
        app,
        host=settings.HOST,
        port=settings.PORT,
        workers=1,  # Use 1 worker for development, scale in production
        reload=settings.RELOAD,
        access_log=settings.ACCESS_LOG,
        log_level=settings.LOG_LEVEL.lower(),
        timeout_keep_alive=30,
        timeout_graceful_shutdown=30,
    )
    
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("Shutting down server...")


if __name__ == "__main__":
    run_server()
