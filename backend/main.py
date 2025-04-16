# /Users/nileshhanotia/Desktop/Voice AI/backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import users, integrations, knowledge, calls, schedules
from app.core.config import settings
from app.api.deps import get_current_user
from app.core.logging import configure_logging_middleware, get_logger

# Initialize main application logger
logger = get_logger("app")
logger.info("Starting Voice AI Platform API")

app = FastAPI(title="Voice AI Platform API")

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging middleware
configure_logging_middleware(app)

# Include routers
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(
    integrations.router, 
    prefix="/api/integrations", 
    tags=["integrations"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    knowledge.router, 
    prefix="/api/knowledge", 
    tags=["knowledge"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(calls.router, prefix="/api/calls", tags=["calls"])
app.include_router(
    schedules.router, 
    prefix="/api/schedules", 
    tags=["schedules"],
    dependencies=[Depends(get_current_user)]
)

# Twilio webhook endpoint - no auth required as it's called by Twilio
app.include_router(calls.twilio_router, prefix="/webhook/twilio", tags=["webhooks"])

@app.get("/health")
def health_check():
    logger.debug("Health check endpoint called")
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)