"""
Database layer for storing agent activities.

Supports both SQLite (local dev) and PostgreSQL (production).
"""
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import sqlalchemy
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

Base = declarative_base()


class AgentActivity(Base):
    """Agent activity record."""
    __tablename__ = "agent_activities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String(255), nullable=False, index=True)
    agent_name = Column(String(255), nullable=False)
    cycle_number = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Response data
    response_text = Column(Text, nullable=True)  # Main agent response text
    tool_calls = Column(JSON, nullable=True)  # List of tool calls made
    stop_reason = Column(String(100), nullable=True)  # Why agent stopped
    
    # Usage statistics
    usage_tokens = Column(Integer, nullable=True)  # Total tokens used
    usage_input_tokens = Column(Integer, nullable=True)
    usage_output_tokens = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="success")  # success, error, rate_limit
    error_message = Column(Text, nullable=True)
    
    # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy reserved word)
    extra_metadata = Column(JSON, nullable=True)  # Extra data (raw response, etc.)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_agent_timestamp', 'agent_id', 'timestamp'),
        Index('idx_timestamp', 'timestamp'),
    )


class ActivityStorage:
    """Handles storage and retrieval of agent activities."""
    
    def __init__(self, database_url: Optional[str] = None):
        """
        Initialize activity storage.
        
        Args:
            database_url: Database URL (if None, auto-detect from env or use SQLite)
        """
        if database_url is None:
            # Auto-detect: use DATABASE_URL env var (Railway PostgreSQL) or default to SQLite
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                # Railway PostgreSQL URLs might need adjustment
                if database_url.startswith('postgres://'):
                    database_url = database_url.replace('postgres://', 'postgresql://', 1)
            else:
                # Default to SQLite in local data directory
                data_dir = Path(__file__).parent / "data"
                data_dir.mkdir(exist_ok=True)
                database_url = f"sqlite:///{data_dir / 'activities.db'}"
        
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        logger.info(f"Activity storage initialized: {database_url.split('@')[-1] if '@' in database_url else database_url}")
    
    def store_activity(
        self,
        agent_id: str,
        agent_name: str,
        cycle_number: int,
        response: Any,
        status: str = "success",
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> int:
        """
        Store an agent activity.
        
        Args:
            agent_id: Agent ID
            agent_name: Agent display name
            cycle_number: Cycle number
            response: Letta response object
            status: Activity status (success, error, rate_limit)
            error_message: Error message if status is error
            metadata: Additional metadata
        
        Returns:
            Activity ID
        """
        session = self.SessionLocal()
        try:
            # Extract response data
            response_text = None
            tool_calls = None
            stop_reason = None
            usage_tokens = None
            usage_input_tokens = None
            usage_output_tokens = None
            
            if response:
                # Extract messages/content
                if hasattr(response, 'messages') and response.messages:
                    # Get the last assistant message (agent response)
                    for msg in reversed(response.messages):
                        if hasattr(msg, 'role') and getattr(msg, 'role', None) == 'assistant':
                            if hasattr(msg, 'content'):
                                response_text = str(msg.content)
                            # Check for tool calls
                            if hasattr(msg, 'tool_calls'):
                                tool_calls = [self._serialize_tool_call(tc) for tc in msg.tool_calls] if msg.tool_calls else None
                            break
                    # If no assistant message, get any content
                    if not response_text:
                        for msg in response.messages:
                            if hasattr(msg, 'content'):
                                response_text = str(msg.content)
                                break
                elif hasattr(response, 'content'):
                    response_text = str(response.content)
                
                # Extract stop reason
                if hasattr(response, 'stop_reason'):
                    stop_reason = str(response.stop_reason)
                
                # Extract usage statistics
                if hasattr(response, 'usage'):
                    usage = response.usage
                    if hasattr(usage, 'total_tokens'):
                        usage_tokens = int(usage.total_tokens) if usage.total_tokens else None
                    if hasattr(usage, 'input_tokens'):
                        usage_input_tokens = int(usage.input_tokens) if usage.input_tokens else None
                    if hasattr(usage, 'output_tokens'):
                        usage_output_tokens = int(usage.output_tokens) if usage.output_tokens else None
            
            # Create activity record
            activity = AgentActivity(
                agent_id=agent_id,
                agent_name=agent_name,
                cycle_number=cycle_number,
                timestamp=datetime.utcnow(),
                response_text=response_text,
                tool_calls=tool_calls,
                stop_reason=stop_reason,
                usage_tokens=usage_tokens,
                usage_input_tokens=usage_input_tokens,
                usage_output_tokens=usage_output_tokens,
                status=status,
                error_message=error_message,
                extra_metadata=metadata or {},
            )
            
            session.add(activity)
            session.commit()
            activity_id = activity.id
            
            logger.debug(f"Stored activity {activity_id} for agent {agent_name} (cycle {cycle_number})")
            return activity_id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to store activity: {e}", exc_info=True)
            raise
        finally:
            session.close()
    
    def _serialize_tool_call(self, tool_call: Any) -> Dict:
        """Serialize a tool call object to dict."""
        try:
            result = {}
            if hasattr(tool_call, 'name'):
                result['name'] = str(tool_call.name)
            if hasattr(tool_call, 'arguments'):
                args = tool_call.arguments
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except:
                        pass
                result['arguments'] = args
            if hasattr(tool_call, 'id'):
                result['id'] = str(tool_call.id)
            return result
        except Exception as e:
            logger.warning(f"Failed to serialize tool call: {e}")
            return {"error": str(e)}
    
    def get_activities(
        self,
        agent_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict]:
        """
        Get agent activities.
        
        Args:
            agent_id: Filter by agent ID (None for all)
            limit: Maximum number of records
            offset: Offset for pagination
            start_time: Filter activities after this time
            end_time: Filter activities before this time
        
        Returns:
            List of activity dictionaries
        """
        session = self.SessionLocal()
        try:
            query = session.query(AgentActivity)
            
            if agent_id:
                query = query.filter(AgentActivity.agent_id == agent_id)
            if start_time:
                query = query.filter(AgentActivity.timestamp >= start_time)
            if end_time:
                query = query.filter(AgentActivity.timestamp <= end_time)
            
            activities = query.order_by(AgentActivity.timestamp.desc()).offset(offset).limit(limit).all()
            
            return [self._activity_to_dict(activity) for activity in activities]
        finally:
            session.close()
    
    def get_agent_stats(self, agent_id: str, days: int = 7) -> Dict:
        """
        Get statistics for an agent.
        
        Args:
            agent_id: Agent ID
            days: Number of days to look back
        
        Returns:
            Statistics dictionary
        """
        session = self.SessionLocal()
        try:
            from datetime import timedelta
            start_time = datetime.utcnow() - timedelta(days=days)
            
            query = session.query(AgentActivity).filter(
                AgentActivity.agent_id == agent_id,
                AgentActivity.timestamp >= start_time
            )
            
            activities = query.all()
            
            if not activities:
                return {
                    "agent_id": agent_id,
                    "total_cycles": 0,
                    "successful_cycles": 0,
                    "error_cycles": 0,
                    "rate_limit_cycles": 0,
                    "total_tool_calls": 0,
                    "total_tokens": 0,
                    "avg_tokens_per_cycle": 0,
                }
            
            total_cycles = len(activities)
            successful_cycles = sum(1 for a in activities if a.status == "success")
            error_cycles = sum(1 for a in activities if a.status == "error")
            rate_limit_cycles = sum(1 for a in activities if a.status == "rate_limit")
            
            total_tool_calls = sum(
                len(a.tool_calls) if a.tool_calls and isinstance(a.tool_calls, list) else 0
                for a in activities
            )
            
            total_tokens = sum(a.usage_tokens or 0 for a in activities)
            avg_tokens = total_tokens / total_cycles if total_cycles > 0 else 0
            
            return {
                "agent_id": agent_id,
                "agent_name": activities[0].agent_name if activities else None,
                "total_cycles": total_cycles,
                "successful_cycles": successful_cycles,
                "error_cycles": error_cycles,
                "rate_limit_cycles": rate_limit_cycles,
                "total_tool_calls": total_tool_calls,
                "total_tokens": total_tokens,
                "avg_tokens_per_cycle": round(avg_tokens, 2),
                "period_days": days,
            }
        finally:
            session.close()
    
    def get_agents(self) -> List[Dict]:
        """Get list of all agents with their latest activity."""
        session = self.SessionLocal()
        try:
            # Get distinct agents with their latest activity
            from sqlalchemy import func
            subquery = session.query(
                AgentActivity.agent_id,
                func.max(AgentActivity.timestamp).label('latest_timestamp')
            ).group_by(AgentActivity.agent_id).subquery()
            
            query = session.query(AgentActivity).join(
                subquery,
                (AgentActivity.agent_id == subquery.c.agent_id) &
                (AgentActivity.timestamp == subquery.c.latest_timestamp)
            )
            
            activities = query.all()
            return [
                {
                    "agent_id": a.agent_id,
                    "agent_name": a.agent_name,
                    "last_activity": a.timestamp.isoformat() if a.timestamp else None,
                    "total_cycles": self._get_agent_cycle_count(session, a.agent_id),
                }
                for a in activities
            ]
        finally:
            session.close()
    
    def _get_agent_cycle_count(self, session: Session, agent_id: str) -> int:
        """Get total cycle count for an agent."""
        return session.query(AgentActivity).filter(AgentActivity.agent_id == agent_id).count()
    
    def _activity_to_dict(self, activity: AgentActivity) -> Dict:
        """Convert activity model to dictionary."""
        return {
            "id": activity.id,
            "agent_id": activity.agent_id,
            "agent_name": activity.agent_name,
            "cycle_number": activity.cycle_number,
            "timestamp": activity.timestamp.isoformat() if activity.timestamp else None,
            "response_text": activity.response_text,
            "tool_calls": activity.tool_calls,
            "stop_reason": activity.stop_reason,
            "usage": {
                "tokens": activity.usage_tokens,
                "input_tokens": activity.usage_input_tokens,
                "output_tokens": activity.usage_output_tokens,
            },
            "status": activity.status,
            "error_message": activity.error_message,
            "metadata": activity.extra_metadata,  # Map extra_metadata back to metadata for API
        }

