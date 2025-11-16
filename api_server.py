"""
FastAPI server for exposing agent activities to frontend.

Provides REST API endpoints for querying agent activities, statistics, and real-time updates.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from database import ActivityStorage

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agent Autonomous Engine API",
    description="API for querying agent activities and performance metrics",
    version="1.0.0",
)

# CORS middleware - allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage instance (will be initialized in startup)
storage: Optional[ActivityStorage] = None


class ActivityResponse(BaseModel):
    """Activity response model."""
    id: int
    agent_id: str
    agent_name: str
    cycle_number: int
    timestamp: str
    response_text: Optional[str]
    tool_calls: Optional[List[dict]]
    stop_reason: Optional[str]
    usage: dict
    status: str
    error_message: Optional[str]
    metadata: Optional[dict]


class AgentStatsResponse(BaseModel):
    """Agent statistics response model."""
    agent_id: str
    agent_name: Optional[str]
    total_cycles: int
    successful_cycles: int
    error_cycles: int
    rate_limit_cycles: int
    total_tool_calls: int
    total_tokens: int
    avg_tokens_per_cycle: float
    period_days: int


class AgentInfoResponse(BaseModel):
    """Agent info response model."""
    agent_id: str
    agent_name: str
    last_activity: Optional[str]
    total_cycles: int


@app.on_event("startup")
async def startup_event():
    """Initialize storage on startup."""
    global storage
    try:
        storage = ActivityStorage()
        logger.info("API server started, storage initialized")
    except Exception as e:
        logger.error(f"Failed to initialize storage: {e}", exc_info=True)
        raise


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Agent Autonomous Engine API",
        "version": "1.0.0",
        "endpoints": {
            "activities": "/api/activities",
            "agent_activities": "/api/activities/{agent_id}",
            "agents": "/api/agents",
            "stats": "/api/stats/{agent_id}",
        }
    }


@app.get("/api/activities", response_model=List[ActivityResponse])
async def get_activities(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    hours: Optional[int] = Query(None, ge=1, description="Filter activities from last N hours"),
):
    """
    Get agent activities.
    
    Returns list of activities, optionally filtered by agent and time range.
    """
    if storage is None:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    
    try:
        start_time = None
        if hours:
            start_time = datetime.utcnow() - timedelta(hours=hours)
        
        activities = storage.get_activities(
            agent_id=agent_id,
            limit=limit,
            offset=offset,
            start_time=start_time,
        )
        
        return activities
    except Exception as e:
        logger.error(f"Error getting activities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/activities/{agent_id}", response_model=List[ActivityResponse])
async def get_agent_activities(
    agent_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    hours: Optional[int] = Query(None, ge=1),
):
    """
    Get activities for a specific agent.
    """
    if storage is None:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    
    try:
        start_time = None
        if hours:
            start_time = datetime.utcnow() - timedelta(hours=hours)
        
        activities = storage.get_activities(
            agent_id=agent_id,
            limit=limit,
            offset=offset,
            start_time=start_time,
        )
        
        return activities
    except Exception as e:
        logger.error(f"Error getting agent activities: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents", response_model=List[AgentInfoResponse])
async def get_agents():
    """
    Get list of all agents with their latest activity info.
    """
    if storage is None:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    
    try:
        agents = storage.get_agents()
        return agents
    except Exception as e:
        logger.error(f"Error getting agents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/{agent_id}", response_model=AgentStatsResponse)
async def get_agent_stats(
    agent_id: str,
    days: int = Query(7, ge=1, le=365, description="Number of days to look back"),
):
    """
    Get performance statistics for an agent.
    
    Returns metrics like total cycles, success rate, tool usage, token consumption, etc.
    """
    if storage is None:
        raise HTTPException(status_code=503, detail="Storage not initialized")
    
    try:
        stats = storage.get_agent_stats(agent_id, days=days)
        return stats
    except Exception as e:
        logger.error(f"Error getting agent stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "storage": "initialized" if storage is not None else "not_initialized",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

