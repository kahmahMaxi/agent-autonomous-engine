"""
Pytest configuration and fixtures.
"""
import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

from engine import AgentConfig, EngineConfig, AgentRunner, AgentAutonomousEngine


@pytest.fixture
def sample_config_dict() -> Dict[str, Any]:
    """Sample configuration dictionary."""
    return {
        "letta": {
            "api_key": "test-api-key",
            "base_url": "https://test-letta.com",
            "timeout": 600,
        },
        "agents": [
            {
                "name": "Test Agent",
                "agent_id": "test-agent-id",
                "cycle_interval_minutes": 15,
                "activation_instruction": "Test instruction",
                "enabled": True,
            }
        ],
    }


@pytest.fixture
def temp_config_file(tmp_path, sample_config_dict):
    """Create a temporary config file."""
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(sample_config_dict, f)
    return str(config_path)


@pytest.fixture
def mock_letta_client():
    """Mock Letta client."""
    client = Mock()
    client.agents = Mock()
    client.agents.messages = Mock()
    client.agents.messages.create = Mock(return_value=Mock())
    client.agents.retrieve = Mock(return_value=Mock(name="Test Agent"))
    return client


@pytest.fixture
def agent_config():
    """Sample agent configuration."""
    return AgentConfig(
        name="Test Agent",
        agent_id="test-agent-id",
        cycle_interval_minutes=15,
        activation_instruction="Test activation instruction",
        enabled=True,
    )


@pytest.fixture
def engine_config(sample_config_dict):
    """Sample engine configuration."""
    return EngineConfig(
        letta_api_key=sample_config_dict["letta"]["api_key"],
        letta_base_url=sample_config_dict["letta"]["base_url"],
        letta_timeout=sample_config_dict["letta"]["timeout"],
        agents=[
            AgentConfig(
                name="Test Agent",
                agent_id="test-agent-id",
                cycle_interval_minutes=15,
                activation_instruction="Test instruction",
                enabled=True,
            )
        ],
    )

