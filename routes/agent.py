"""
Agent Routes — AI agent endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from schemas import AgentQuery, AgentResponse
from agent.ai_agent import APIAgent

router = APIRouter(prefix="/api", tags=["Agent"])


@router.post("/agent")
async def agent_query(request: AgentQuery, db: Session = Depends(get_db)):
    """
    🤖 AI Agent Mode — intelligent API discovery with verification and integration.

    The agent will:
    1. Analyze your query
    2. Discover relevant APIs
    3. Verify top recommendations (live health check)
    4. Optionally generate integration code
    """
    agent = APIAgent(db)
    result = await agent.process_query(
        query=request.query,
        auto_integrate=request.auto_integrate,
    )
    return result
