from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config
from dependencies import rpc_client, cache_layer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Snapshot Inteligente",
    description="Bitcoin node state interpretation API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
from routes.health import router as health_router
from routes.mempool import router as mempool_router
from routes.blockchain import router as blockchain_router

app.include_router(health_router, prefix="/api")
app.include_router(mempool_router, prefix="/api")
app.include_router(blockchain_router, prefix="/api")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown."""
    rpc_client.close()
    cache_layer.close()
    logger.info("Application shutdown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        workers=1
    )
