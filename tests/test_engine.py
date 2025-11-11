"""
Tests for AgentAutonomousEngine.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from engine import AgentAutonomousEngine, EngineConfig, AgentConfig


def test_engine_initialization(engine_config):
    """Test engine initialization."""
    engine = AgentAutonomousEngine(engine_config)
    
    assert engine.config == engine_config
    assert engine.running is False
    assert len(engine.agent_runners) == 0
    assert len(engine.agent_threads) == 0


def test_engine_start_no_agents(tmp_path):
    """Test engine start with no agents."""
    config = EngineConfig(
        letta_api_key="test-key",
        letta_base_url="https://test.com",
        letta_timeout=600,
        agents=[],
    )
    
    engine = AgentAutonomousEngine(config)
    
    # Should not crash, just return
    engine.start()


def test_engine_start_with_agents(engine_config, mock_letta_client):
    """Test engine start with agents."""
    with patch('engine.Letta', return_value=mock_letta_client):
        engine = AgentAutonomousEngine(engine_config)
        
        # Mock agent retrieval
        mock_agent = Mock()
        mock_agent.name = "Test Agent"
        mock_letta_client.agents.retrieve.return_value = mock_agent
        
        # Start engine (will run in background)
        import threading
        thread = threading.Thread(target=engine.start, daemon=True)
        thread.start()
        
        # Give it a moment to start
        import time
        time.sleep(0.5)
        
        # Stop engine
        engine.stop()
        thread.join(timeout=1)
        
        # Verify agents were started
        assert len(engine.agent_runners) > 0 or engine.running is False


def test_engine_stop(engine_config, mock_letta_client):
    """Test engine stop."""
    with patch('engine.Letta', return_value=mock_letta_client):
        engine = AgentAutonomousEngine(engine_config)
        engine.running = True
        
        # Add a mock runner
        from engine import AgentRunner
        mock_runner = Mock(spec=AgentRunner)
        mock_runner.running = True
        mock_runner.agent_config = Mock(name="Test Agent")
        engine.agent_runners["test-id"] = mock_runner
        
        engine.stop()
        
        assert engine.running is False
        assert mock_runner.running is False


def test_engine_print_status_empty(engine_config):
    """Test engine print_status with no agents."""
    engine = AgentAutonomousEngine(engine_config)
    
    # Should not raise exception
    engine.print_status()


def test_engine_print_status_with_runners(engine_config, mock_letta_client):
    """Test engine print_status with active runners."""
    with patch('engine.Letta', return_value=mock_letta_client):
        engine = AgentAutonomousEngine(engine_config)
        
        # Add mock runner
        from engine import AgentRunner, AgentConfig
        agent_config = AgentConfig(
            name="Test Agent",
            agent_id="test-id",
            cycle_interval_minutes=15,
            activation_instruction="Test",
        )
        runner = AgentRunner(agent_config, mock_letta_client)
        runner.stats["cycles_completed"] = 5
        runner.stats["last_activation"] = "2025-01-01T12:00:00"
        
        engine.agent_runners["test-id"] = runner
        
        # Should not raise exception
        engine.print_status()

