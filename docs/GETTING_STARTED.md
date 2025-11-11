# Getting Started

Complete guide to setting up and running Agent Autonomous Engine.

## Prerequisites

- Python 3.10 or higher
- Letta server (remote or self-hosted)
- Letta agents with registered tools
- API credentials for your use case (trading, social, etc.)

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/kahmahMaxi/agent-autonomous-engine.git
cd agent-autonomous-engine
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
venv\Scripts\Activate.ps1

# Activate (Linux/WSL)
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Step 1: Create Config File

```bash
cp config.yaml.template config.yaml
```

### Step 2: Configure Letta Connection

Edit `config.yaml`:

```yaml
letta:
  api_key: "your-letta-api-key"
  base_url: "https://your-letta-server.com"  # Your Letta server URL
  timeout: 600
```

### Step 3: Configure Agents

Add your agents:

```yaml
agents:
  - name: "My Agent"
    agent_id: "your-letta-agent-id"
    cycle_interval_minutes: 15
    activation_instruction: |
      Your strategic instruction for the agent...
    enabled: true
```

## Register Tools

Before running, ensure your agents have tools registered. For example, with Animus Vibe:

```bash
cd ../animus-vibe
python scripts/register_aster_tools.py --agent-id your-agent-id
```

## Set Agent Credentials

In Letta agent settings, configure environment variables per agent:
- Trading: `ASTER_API_KEY`, `ASTER_API_SECRET`
- Social: Platform-specific credentials
- Research: API keys as needed

## Running

```bash
# Start engine
python engine.py

# Check status
python engine.py --status

# Run specific agents
python engine.py --agents agent-id-1 agent-id-2
```

## Next Steps

- See [USE_CASES.md](USE_CASES.md) for detailed examples
- Check [README.md](../README.md) for full documentation
- Customize activation instructions for your use case

