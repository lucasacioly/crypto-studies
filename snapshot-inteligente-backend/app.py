from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import config
from dependencies import rpc_client, cache_layer, zmq_listener
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Snapshot Inteligente",
    description="Bitcoin node state interpretation API with real-time event streaming",
    version="2.0.0"
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
from routes.events import router as events_router

app.include_router(health_router)
app.include_router(mempool_router)
app.include_router(blockchain_router)
app.include_router(events_router)

# Background task for ZMQ listener
zmq_task = None

@app.on_event("startup")
async def startup_event():
    """Start ZMQ listener on app startup."""
    global zmq_task
    logger.info("Application startup")
    
    try:
        # Start ZMQ listener in background
        zmq_task = asyncio.create_task(zmq_listener.start())
        logger.info("ZMQ listener started")
    except Exception as e:
        logger.error(f"Failed to start ZMQ listener: {e}")
        # Don't fail the app if ZMQ doesn't work (it's a nice-to-have)

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on app shutdown."""
    global zmq_task
    
    logger.info("Application shutdown")
    
    # Stop ZMQ listener
    try:
        await zmq_listener.stop()
        if zmq_task:
            zmq_task.cancel()
        logger.info("ZMQ listener stopped")
    except Exception as e:
        logger.error(f"Error stopping ZMQ listener: {e}")
    
    # Close other services
    rpc_client.close()
    cache_layer.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT,
        workers=1
    )

