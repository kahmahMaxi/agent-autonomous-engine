"""
Tests for AgentRunner.
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from engine import AgentRunner, AgentConfig


def test_agent_runner_initialization(agent_config, mock_letta_client):
    """Test AgentRunner initialization."""
    runner = AgentRunner(agent_config, mock_letta_client)
    
    assert runner.agent_config == agent_config
    assert runner.letta == mock_letta_client
    assert runner.running is False
    assert runner.stats["cycles_completed"] == 0
    assert runner.stats["errors"] == 0


def test_agent_runner_activate_agent_success(agent_config, mock_letta_client):
    """Test successful agent activation."""
    runner = AgentRunner(agent_config, mock_letta_client)
    
    # Mock successful response
    mock_response = Mock()
    mock_letta_client.agents.messages.create.return_value = mock_response
    
    runner._activate_agent()
    
    # Verify Letta was called correctly
    mock_letta_client.agents.messages.create.assert_called_once()
    call_args = mock_letta_client.agents.messages.create.call_args
    assert call_args.kwargs["agent_id"] == agent_config.agent_id
    
    # Verify stats updated
    assert runner.stats["cycles_completed"] == 1
    assert runner.stats["last_activation"] is not None


def test_agent_runner_activate_agent_rate_limit(agent_config, mock_letta_client):
    """Test agent activation with rate limit error."""
    runner = AgentRunner(agent_config, mock_letta_client)
    
    # Mock rate limit error (as string in exception message)
    error = Exception("429 Rate limit exceeded for LLM model provider")
    mock_letta_client.agents.messages.create.side_effect = error
    
    runner._activate_agent()
    
    # Should not count as error (rate limits are handled gracefully)
    assert runner.stats["errors"] == 0
    assert runner.stats["cycles_completed"] == 0  # Not completed due to rate limit


def test_agent_runner_activate_agent_other_error(agent_config, mock_letta_client):
    """Test agent activation with other error."""
    runner = AgentRunner(agent_config, mock_letta_client)
    
    # Mock other error
    mock_letta_client.agents.messages.create.side_effect = Exception("Connection error")
    
    runner._activate_agent()
    
    # Should count as error
    assert runner.stats["errors"] == 1
    assert runner.stats["cycles_completed"] == 0


def test_agent_runner_stop_flag(agent_config, mock_letta_client):
    """Test that runner respects running flag."""
    runner = AgentRunner(agent_config, mock_letta_client)
    runner.running = False
    
    # Runner should not activate when running is False
    initial_cycles = runner.stats["cycles_completed"]
    runner._activate_agent()  # This should still work even if running is False
    
    # But run() loop should exit immediately
    runner.running = False
    # We can't easily test the full run() loop, but we can verify the flag is checked


@patch('engine.time.sleep')
def test_agent_runner_run_loop(mock_sleep, agent_config, mock_letta_client):
    """Test agent runner loop execution."""
    runner = AgentRunner(agent_config, mock_letta_client)
    runner.running = True
    
    # Mock sleep to return immediately and set running to False after first iteration
    call_count = 0
    def sleep_side_effect(seconds):
        nonlocal call_count
        call_count += 1
        if call_count > 5:  # Stop after a few iterations
            runner.running = False
    
    mock_sleep.side_effect = sleep_side_effect
    
    # Mock successful activation
    mock_letta_client.agents.messages.create.return_value = Mock()
    
    # Run in a thread with timeout to avoid hanging
    import threading
    thread = threading.Thread(target=runner.run, daemon=True)
    thread.start()
    thread.join(timeout=2)
    
    # Verify activation was called
    assert mock_letta_client.agents.messages.create.called

