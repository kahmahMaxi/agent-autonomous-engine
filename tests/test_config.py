"""
Tests for configuration loading.
"""
import pytest
import yaml
from pathlib import Path
from engine import load_config, AgentConfig, EngineConfig


def test_load_config_success(temp_config_file):
    """Test successful config loading."""
    config = load_config(temp_config_file)
    
    assert config.letta_api_key == "test-api-key"
    assert config.letta_base_url == "https://test-letta.com"
    assert config.letta_timeout == 600
    assert len(config.agents) == 1
    assert config.agents[0].name == "Test Agent"
    assert config.agents[0].agent_id == "test-agent-id"


def test_load_config_missing_file():
    """Test config loading with missing file."""
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent_config.yaml")


def test_load_config_missing_api_key(tmp_path):
    """Test config loading with missing API key."""
    config_dict = {
        "letta": {
            "base_url": "https://test.com",
        },
        "agents": [],
    }
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_dict, f)
    
    with pytest.raises(ValueError, match="Letta API key required"):
        load_config(str(config_path))


def test_load_config_env_var_override(tmp_path, monkeypatch):
    """Test config loading with environment variable override."""
    monkeypatch.setenv("LETTA_API_KEY", "env-api-key")
    monkeypatch.setenv("LETTA_BASE_URL", "https://env-server.com")
    
    config_dict = {
        "letta": {
            "api_key": "",  # Empty, should use env var
            "base_url": "",  # Empty, should use env var
        },
        "agents": [],
    }
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_dict, f)
    
    config = load_config(str(config_path))
    assert config.letta_api_key == "env-api-key"
    assert config.letta_base_url == "https://env-server.com"


def test_load_config_backward_compat_interval(tmp_path):
    """Test backward compatibility with 'interval_minutes'."""
    config_dict = {
        "letta": {
            "api_key": "test-key",
        },
        "agents": [
            {
                "name": "Test",
                "agent_id": "test-id",
                "interval_minutes": 30,  # Old format
                "prompt": "Test prompt",  # Old format
            }
        ],
    }
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, "w") as f:
        yaml.dump(config_dict, f)
    
    config = load_config(str(config_path))
    agent = config.agents[0]
    assert agent.cycle_interval_minutes == 30
    assert agent.activation_instruction == "Test prompt"


def test_agent_config_defaults():
    """Test AgentConfig with defaults."""
    agent = AgentConfig(
        name="Test",
        agent_id="test-id",
        cycle_interval_minutes=15,
        activation_instruction="Test",
    )
    
    assert agent.name == "Test"
    assert agent.agent_id == "test-id"
    assert agent.cycle_interval_minutes == 15
    assert agent.activation_instruction == "Test"
    assert agent.enabled is True  # Default


def test_agent_config_disabled():
    """Test AgentConfig with enabled=False."""
    agent = AgentConfig(
        name="Test",
        agent_id="test-id",
        cycle_interval_minutes=15,
        activation_instruction="Test",
        enabled=False,
    )
    
    assert agent.enabled is False

