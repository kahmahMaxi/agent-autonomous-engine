"""
Integration tests for Agent Autonomous Engine.
"""
import pytest
import yaml
import time
from pathlib import Path
from unittest.mock import Mock, patch

from engine import load_config, AgentAutonomousEngine


@pytest.fixture
def integration_config(tmp_path):
    """Create integration test configuration."""
    config_dict = {
        "letta": {
            "api_key": "test-integration-key",
            "base_url": "https://test-letta.com",
            "timeout": 600,
        },
        "agents": [
            {
                "name": "Integration Test Agent",
                "agent_id": "integration-test-id",
                "cycle_interval_minutes": 0.1,  # Very short for testing
                "activation_instruction": "Test activation for integration",
                "enabled": True,
            }
        ],
    }
    
    config_path = tmp_path / "integration_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_dict, f)
    
    return str(config_path)


@patch('engine.Letta')
def test_full_engine_cycle(mock_letta_class, integration_config):
    """Test full engine cycle from config to execution."""
    # Setup mock Letta client
    mock_letta = Mock()
    mock_letta.agents = Mock()
    mock_letta.agents.messages = Mock()
    mock_letta.agents.messages.create = Mock(return_value=Mock())
    mock_letta.agents.retrieve = Mock(return_value=Mock(name="Integration Test Agent"))
    mock_letta_class.return_value = mock_letta
    
    # Load config
    config = load_config(integration_config)
    
    # Create and start engine
    engine = AgentAutonomousEngine(config)
    
    # Start in background thread
    import threading
    thread = threading.Thread(target=engine.start, daemon=True)
    thread.start()
    
    # Wait a moment for activation
    time.sleep(1)
    
    # Stop engine
    engine.stop()
    thread.join(timeout=2)
    
    # Verify Letta was called
    assert mock_letta.agents.messages.create.called


def test_config_validation_missing_agent_id(tmp_path):
    """Test that agents without agent_id are skipped."""
    config_dict = {
        "letta": {
            "api_key": "test-key",
        },
        "agents": [
            {
                "name": "Valid Agent",
                "agent_id": "valid-id",
                "cycle_interval_minutes": 15,
                "activation_instruction": "Test",
            },
            {
                "name": "Invalid Agent",
                # Missing agent_id
                "cycle_interval_minutes": 15,
                "activation_instruction": "Test",
            },
        ],
    }
    
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_dict, f)
    
    config = load_config(str(config_path))
    
    # Should only load valid agent
    assert len(config.agents) == 1
    assert config.agents[0].name == "Valid Agent"


def test_multiple_agents_config(tmp_path):
    """Test configuration with multiple agents."""
    config_dict = {
        "letta": {
            "api_key": "test-key",
        },
        "agents": [
            {
                "name": "Agent 1",
                "agent_id": "agent-1",
                "cycle_interval_minutes": 15,
                "activation_instruction": "Agent 1 instruction",
            },
            {
                "name": "Agent 2",
                "agent_id": "agent-2",
                "cycle_interval_minutes": 30,
                "activation_instruction": "Agent 2 instruction",
            },
            {
                "name": "Agent 3",
                "agent_id": "agent-3",
                "cycle_interval_minutes": 60,
                "activation_instruction": "Agent 3 instruction",
                "enabled": False,  # Disabled
            },
        ],
    }
    
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_dict, f)
    
    config = load_config(str(config_path))
    
    assert len(config.agents) == 3
    assert config.agents[0].name == "Agent 1"
    assert config.agents[1].name == "Agent 2"
    assert config.agents[2].name == "Agent 3"
    assert config.agents[2].enabled is False

