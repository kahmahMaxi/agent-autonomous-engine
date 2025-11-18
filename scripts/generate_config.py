#!/usr/bin/env python3
"""
Generate config.yaml from environment variables for Railway deployment.

This script reads all configuration from Railway environment variables and
creates a config.yaml file that the application can use.

Supports multiple agents using the pattern:
- AGENT_1_NAME, AGENT_1_ID, AGENT_1_CYCLE_INTERVAL_MINUTES, AGENT_1_ACTIVATION_INSTRUCTION, AGENT_1_ENABLED
- AGENT_2_NAME, AGENT_2_ID, etc.
"""
import os
import yaml
from pathlib import Path


def generate_config_from_env():
    """Generate config.yaml from environment variables."""
    
    # Letta configuration
    letta_config = {
        "api_key": os.getenv("LETTA_API_KEY", ""),
        "base_url": os.getenv("LETTA_BASE_URL", "https://app.letta.com"),
        "timeout": int(os.getenv("LETTA_TIMEOUT", "600"))
    }
    
    # Load agents from environment variables
    # Pattern: AGENT_1_NAME, AGENT_1_ID, AGENT_1_CYCLE_INTERVAL_MINUTES, etc.
    agents = []
    agent_index = 1
    
    while True:
        name_key = f"AGENT_{agent_index}_NAME"
        id_key = f"AGENT_{agent_index}_ID"
        
        agent_name = os.getenv(name_key)
        agent_id = os.getenv(id_key)
        
        # Stop if we don't find an agent at this index
        if not agent_name and not agent_id:
            break
        
        # If we have at least name or ID, create the agent
        if agent_name or agent_id:
            cycle_interval = int(os.getenv(f"AGENT_{agent_index}_CYCLE_INTERVAL_MINUTES", "15"))
            activation_instruction = os.getenv(
                f"AGENT_{agent_index}_ACTIVATION_INSTRUCTION",
                "You are an autonomous agent. Review your goals and available tools. Assess your current situation and make strategic decisions. Execute actions using your registered tools."
            )
            enabled = os.getenv(f"AGENT_{agent_index}_ENABLED", "true").lower() == "true"
            
            agent = {
                "name": agent_name or f"Agent {agent_index}",
                "agent_id": agent_id or "",
                "cycle_interval_minutes": cycle_interval,
                "activation_instruction": activation_instruction,
                "enabled": enabled
            }
            
            agents.append(agent)
        
        agent_index += 1
        
        # Safety limit: don't check beyond 50 agents
        if agent_index > 50:
            break
    
    # Build complete config
    config = {
        "letta": letta_config,
        "agents": agents
    }
    
    # Write config.yaml
    config_path = Path("config.yaml")
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"✅ Generated config.yaml from environment variables")
    print(f"   Letta Base URL: {letta_config['base_url']}")
    print(f"   Agents configured: {len(agents)}")
    
    for i, agent in enumerate(agents, 1):
        status = "✅ enabled" if agent["enabled"] else "❌ disabled"
        print(f"   Agent {i}: {agent['name']} ({agent['agent_id'][:20]}...) - {status}")
    
    # Validate required fields
    required_fields = []
    if not letta_config["api_key"]:
        required_fields.append("LETTA_API_KEY")
    
    if not agents:
        required_fields.append("AGENT_1_NAME and AGENT_1_ID (at least one agent required)")
    else:
        for i, agent in enumerate(agents, 1):
            if not agent["agent_id"]:
                required_fields.append(f"AGENT_{i}_ID")
    
    if required_fields:
        print(f"\n⚠️  Warning: Missing required environment variables:")
        for field in required_fields:
            print(f"   - {field}")
        print("\n   The application may not work correctly without these.")
    else:
        print("\n✅ All required configuration fields are set")
    
    return config_path


if __name__ == "__main__":
    generate_config_from_env()

