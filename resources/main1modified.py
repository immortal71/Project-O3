health_status["redis"] = "not_configured"
    except Exception as e:
        health_status["redis"] = "unhealthy"
        health_status["redis_error"] = str(e)
        health_status["status"] = "unhealthy"
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return health_status


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    
    metrics_data = generate_latest()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to OncoPurpose API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Setup documentation
app = setup_documentation(app)


# Global exception handlers for additional safety
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors"""
    logger.error("Database error occurred", error=str(exc), path=request.url.path)
    return {
        "error": "Database error",
        "detail": "A database error occurred. Please try again later."
    }


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(
        "Unexpected error occurred",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
        method=request.method
    )
    return {
        "error": "Internal server error",
        "detail": "An unexpected error occurred. Please try again later."
    }