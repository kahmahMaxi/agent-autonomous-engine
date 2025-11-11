# Agent Autonomous Engine

<div align="center">

**Orchestrate autonomous decision cycles for multiple Letta agents**

*Enable true agent autonomy with periodic activation cycles, strategic decision-making, and independent tool execution*

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🌟 Overview

**Agent Autonomous Engine** is a sophisticated orchestration system that enables multiple Letta agents to operate autonomously through periodic decision cycles. Unlike simple schedulers, this engine activates agents with strategic instructions, allowing them to independently assess their environment, make decisions, and execute actions using their registered tools.

### Core Philosophy

**True Autonomy Through Strategic Activation**

The engine doesn't command agents—it activates them for autonomous decision-making. Each agent:
- Receives strategic activation instructions
- Assesses current state using memory and context
- Makes independent decisions about tool usage
- Executes chosen actions autonomously
- Learns from outcomes and adapts

## ✨ Features

- **🔄 Autonomous Decision Cycles** - Agents wake periodically to make strategic decisions
- **🌐 Multi-Agent Orchestration** - Run unlimited agents from a single deployment
- **🧠 Memory-Aware Activation** - Agents leverage Letta's memory systems for context
- **🛠️ Tool Integration** - Agents automatically use registered tools (trading, social, research, etc.)
- **📊 Performance Tracking** - Monitor cycles, activations, and outcomes
- **⚡ Remote Letta Support** - Connect to any Letta server (cloud or self-hosted)
- **🎯 Use Case Agnostic** - Works for trading, social media, research, or any domain

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd agent-autonomous-engine

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\Activate.ps1

# Activate (Linux/WSL)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

**1. Create engine configuration:**

```bash
cp config.yaml.template config.yaml
```

Edit `config.yaml`:
```yaml
letta:
  api_key: "your-letta-api-key"
  base_url: "https://your-letta-server.com"
  timeout: 600

agents:
  - name: "Trading Agent Alpha"
    agent_id: "agent-id-1"
    cycle_interval_minutes: 15
    activation_instruction: |
      Review market conditions and your portfolio.
      Research opportunities, form trading theses, and execute trades strategically.
    enabled: true
```

**2. Register tools with your agents:**

Before running the engine, ensure your agents have tools registered in Letta. For example, with Animus Vibe:

```bash
cd ../animus-vibe
python scripts/register_aster_tools.py --agent-id agent-id-1
```

**3. Set agent credentials:**

In Letta agent settings, configure environment variables per agent:
- Trading agents: `ASTER_API_KEY`, `ASTER_API_SECRET`
- Social agents: Platform-specific credentials
- Research agents: API keys as needed

### Running

```bash
# Start engine (runs all enabled agents)
python engine.py

# Run specific agents only
python engine.py --agents agent-id-1 agent-id-2

# Check status
python engine.py --status

# Debug mode
python engine.py --log-level DEBUG
```

## 📖 Use Cases

### 1. Autonomous Trading Agents

**Scenario:** Multiple trading agents, each with their own Aster account, making independent trading decisions.

```yaml
agents:
  - name: "Conservative Trader"
    agent_id: "agent-conservative"
    cycle_interval_minutes: 30
    activation_instruction: |
      Review portfolio health and market conditions.
      Focus on low-risk opportunities with high confidence.
      Monitor existing positions and manage risk.
    enabled: true

  - name: "Aggressive Trader"
    agent_id: "agent-aggressive"
    cycle_interval_minutes: 10
    activation_instruction: |
      Scan for high-momentum opportunities.
      Execute trades with calculated risk.
      Maximize portfolio growth.
    enabled: true
```

**Benefits:**
- Each agent uses its own Aster credentials (from Letta env vars)
- Independent trading strategies per agent
- Automatic risk management and position monitoring
- Portfolio diversification across multiple agents

### 2. Social Media Agents

**Scenario:** Autonomous social media agents engaging with communities, posting content, and building relationships.

```yaml
agents:
  - name: "Tech Community Agent"
    agent_id: "agent-tech"
    cycle_interval_minutes: 20
    activation_instruction: |
      Check for mentions and interesting conversations.
      Share technical insights and engage authentically.
      Build relationships with the developer community.
    enabled: true
```

**Benefits:**
- Autonomous content creation and engagement
- Community relationship building
- Multi-platform support (Twitter, Bluesky, Discord)
- Natural conversation flow

### 3. Research & Analysis Agents

**Scenario:** Agents that continuously research topics, analyze data, and share insights.

```yaml
agents:
  - name: "Crypto Research Agent"
    agent_id: "agent-research"
    cycle_interval_minutes: 60
    activation_instruction: |
      Discover trending topics and emerging projects.
      Conduct deep research and analysis.
      Share findings and insights with the community.
    enabled: true
```

**Benefits:**
- Continuous knowledge discovery
- Automated research workflows
- Insight generation and sharing
- Multi-source data aggregation

### 4. Multi-Domain Agents

**Scenario:** Agents that operate across multiple domains simultaneously.

```yaml
agents:
  - name: "Omnibus Agent"
    agent_id: "agent-omnibus"
    cycle_interval_minutes: 15
    activation_instruction: |
      Review all your goals across trading, social, and research.
      Prioritize actions based on current opportunities.
      Execute across domains strategically.
    enabled: true
```

**Benefits:**
- Unified agent operating across domains
- Strategic prioritization
- Cross-domain learning
- Comprehensive automation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         Agent Autonomous Engine                 │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   Agent 1   │  │   Agent 2   │  │ Agent N │ │
│  │   Thread    │  │   Thread    │  │ Thread  │ │
│  └──────┬──────┘  └──────┬──────┘  └────┬────┘ │
│         │                 │               │      │
│         └─────────────────┴───────────────┘      │
│                    │                             │
└────────────────────┼─────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Letta Server       │
         │  (Remote/Cloud)      │
         └───────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                      │
    ┌────▼────┐          ┌─────▼─────┐
    │ Agent 1 │          │  Agent 2  │
    │ Memory  │          │  Memory   │
    │ Tools   │          │  Tools    │
    └─────────┘          └───────────┘
```

### How It Works

1. **Engine Initialization**
   - Loads configuration (Letta connection + agent list)
   - Connects to Letta server
   - Validates agent IDs

2. **Agent Activation Cycles**
   - Each agent runs in its own thread
   - At configured intervals, agent receives activation instruction
   - Agent assesses state using Letta memory
   - Agent makes autonomous decisions
   - Agent executes actions via registered tools
   - Results stored in Letta memory

3. **Autonomous Decision Making**
   - Agents use Letta's reasoning capabilities
   - Memory informs decisions
   - Tools executed automatically
   - Outcomes learned and adapted

## 📋 Configuration Reference

### Engine Configuration

```yaml
# Letta Server Connection
letta:
  api_key: "your-letta-api-key"          # Required
  base_url: "https://app.letta.com"      # Your Letta server URL
  timeout: 600                            # Request timeout (seconds)

# Agent Configurations
agents:
  - name: "Agent Name"                    # Display name
    agent_id: "letta-agent-id"            # Required: Letta agent ID
    cycle_interval_minutes: 15            # Decision cycle frequency
    activation_instruction: |             # Strategic instruction for agent
      Your custom instruction here...
    enabled: true                         # Enable/disable this agent
```

### Environment Variables (Alternative)

```bash
LETTA_API_KEY=your-key
LETTA_BASE_URL=https://your-server.com
```

## 🎯 Benefits

### For Developers

- **Simple Integration** - Just configure and run
- **No Code Required** - All behavior via configuration
- **Extensible** - Works with any Letta tools
- **Observable** - Built-in status and logging

### For Organizations

- **Scalable** - Run unlimited agents from one deployment
- **Cost-Effective** - Single process, multiple agents
- **Flexible** - Different strategies per agent
- **Reliable** - Graceful error handling and recovery

### For Agents

- **True Autonomy** - Independent decision-making
- **Memory-Aware** - Learn from past actions
- **Tool-Rich** - Access to all registered capabilities
- **Strategic** - Make decisions based on goals and context

## 🔧 Advanced Usage

### Custom Activation Instructions

Craft sophisticated instructions for different agent personalities:

```yaml
# Conservative Trading Agent
activation_instruction: |
  You are a risk-averse trading agent. Before any trade:
  1. Research thoroughly (minimum 3 data points)
  2. Require >70% confidence
  3. Limit position size to 5% of portfolio
  4. Always set stop-loss

# Aggressive Research Agent
activation_instruction: |
  You are an aggressive research agent. Your goals:
  1. Discover 5+ new opportunities per cycle
  2. Share insights immediately
  3. Engage with trending topics
  4. Build thought leadership
```

### Multi-Agent Strategies

Run complementary agents with different strategies:

```yaml
agents:
  # Scout agent - finds opportunities
  - name: "Scout"
    cycle_interval_minutes: 5
    activation_instruction: "Discover and research new opportunities"
  
  # Executor agent - acts on opportunities
  - name: "Executor"
    cycle_interval_minutes: 15
    activation_instruction: "Review discovered opportunities and execute"
  
  # Monitor agent - tracks performance
  - name: "Monitor"
    cycle_interval_minutes: 30
    activation_instruction: "Monitor all positions and performance"
```

## 📊 Monitoring

### Status Command

```bash
python engine.py --status
```

Shows:
- Agent names and cycle intervals
- Total cycles completed
- Last activation time
- Error counts

### Logs

Engine logs all activations, decisions, and outcomes:
- Cycle start/completion
- Agent decisions
- Tool executions
- Errors and warnings

## 🚢 Deployment

### Local Development

```bash
python engine.py
```

### Production (Railway/Any Platform)

```bash
# Set environment variables
export LETTA_API_KEY=your-key
export LETTA_BASE_URL=https://your-server.com

# Run engine
python engine.py
```

### Docker (Coming Soon)

```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "engine.py"]
```

## 🔒 Security

- **Credentials in Letta** - Agent credentials stored in Letta env vars (not in config)
- **No Hardcoded Secrets** - All sensitive data via environment variables
- **Isolated Agents** - Each agent has separate credentials and memory
- **Secure Connections** - HTTPS to Letta server

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author

**Kamal** - Creator and maintainer

*Building the future of autonomous agent systems*

## 🙏 Acknowledgments

- Built for the [Letta](https://letta.com) agent platform
- Inspired by autonomous agent research
- Designed for the Animus ecosystem

## 📚 Related Projects

- **[Animus Vibe](https://github.com/your-org/animus-vibe)** - Trading tools for Letta agents
- **[Animus Social](https://github.com/your-org/animus-social)** - Social media tools for Letta agents
- **[Letta](https://letta.com)** - Agent orchestration platform

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=engine --cov-report=html

# Run specific test file
pytest tests/test_config.py
```

See [tests/README.md](tests/README.md) for detailed testing documentation.

## 🆘 Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Open an issue on GitHub
- **Discussions**: Join our community discussions

---

<div align="center">

**Enable true agent autonomy. Build the future of autonomous systems.**

Made with ❤️ for the autonomous agent community

</div>
