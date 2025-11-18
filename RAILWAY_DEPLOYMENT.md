# Railway Deployment Guide for Agent Autonomous Engine

This guide explains how to deploy the Agent Autonomous Engine on Railway using environment variables instead of committing `config.yaml` to git.

## Overview

Since `config.yaml` contains sensitive credentials and is gitignored, we use a **startup script** (`scripts/generate_config.py`) that generates `config.yaml` from Railway environment variables when the application starts.

## Deployment Steps

### 1. Connect Your Repository to Railway

1. Go to [Railway](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Railway will automatically detect it's a Python project

### 2. Configure Environment Variables

In Railway dashboard, go to your project → **Variables** tab and add all required environment variables:

#### Required Variables (Minimum)

```bash
# Letta Configuration
LETTA_API_KEY=sk-let-...
LETTA_BASE_URL=https://your-letta-server.up.railway.app  # Optional, defaults to https://app.letta.com
LETTA_TIMEOUT=600  # Optional, defaults to 600 seconds

# API Configuration (Optional)
API_ENABLED=true  # Set to "false" to run engine only (no API server). Defaults to "true"

# Agent 1 Configuration (at least one agent required)
AGENT_1_NAME=Vibe
AGENT_1_ID=agent-29ae4ac5-e281-4c17-99b9-26c38800216e
AGENT_1_CYCLE_INTERVAL_MINUTES=4  # Optional, defaults to 15
AGENT_1_ACTIVATION_INSTRUCTION=please i want you to discover candidates, check positions for each, research, form a thesis using my balances and positions, then open the trade with the proposed size, don't tweet it, and no need to monitor it since trade always get executed immediately. make sure you open at least a single trade (buy or sell) every time. and report the portfolio pnl after.
AGENT_1_ENABLED=true  # Optional, defaults to true
```

#### Multiple Agents

To configure multiple agents, use the same pattern with increasing numbers:

```bash
# Agent 1
AGENT_1_NAME=Vibe
AGENT_1_ID=agent-29ae4ac5-e281-4c17-99b9-26c38800216e
AGENT_1_CYCLE_INTERVAL_MINUTES=4
AGENT_1_ACTIVATION_INSTRUCTION=your activation instruction here
AGENT_1_ENABLED=true

# Agent 2
AGENT_2_NAME=Trader
AGENT_2_ID=agent-abc123-def456-ghi789
AGENT_2_CYCLE_INTERVAL_MINUTES=10
AGENT_2_ACTIVATION_INSTRUCTION=your activation instruction here
AGENT_2_ENABLED=true

# Agent 3
AGENT_3_NAME=Analyst
AGENT_3_ID=agent-xyz789-uvw456-rst123
AGENT_3_CYCLE_INTERVAL_MINUTES=30
AGENT_3_ACTIVATION_INSTRUCTION=your activation instruction here
AGENT_3_ENABLED=false  # This agent will be disabled
```

**Note:** The script will automatically detect agents up to 50 (AGENT_1 through AGENT_50). You only need to set the variables for the agents you want to use.

#### Environment Variable Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LETTA_API_KEY` | ✅ Yes | - | Your Letta API key |
| `LETTA_BASE_URL` | ❌ No | `https://app.letta.com` | Your Letta server URL (for self-hosted) |
| `LETTA_TIMEOUT` | ❌ No | `600` | Request timeout in seconds |
| `API_ENABLED` | ❌ No | `true` | Enable API server (`true`/`false`). Set to `false` to run engine only |
| `AGENT_N_NAME` | ✅ Yes* | - | Agent display name |
| `AGENT_N_ID` | ✅ Yes* | - | Letta agent ID |
| `AGENT_N_CYCLE_INTERVAL_MINUTES` | ❌ No | `15` | Decision cycle frequency (minutes) |
| `AGENT_N_ACTIVATION_INSTRUCTION` | ❌ No | Default instruction | Activation prompt for the agent |
| `AGENT_N_ENABLED` | ❌ No | `true` | Whether the agent is enabled (`true`/`false`) |

*At least one agent (AGENT_1) is required.

### 3. Choose Your Deployment Mode

#### Option A: Engine + API Server (Default)
For frontend integration and activity monitoring:
- Set `API_ENABLED=true` (or leave unset, defaults to `true`)
- The API server will run on Railway's `PORT` environment variable
- Access endpoints: `/api/activities`, `/api/agents`, `/api/stats/{agent_id}`

#### Option B: Engine Only
For autonomous agents without frontend:
- Set `API_ENABLED=false`
- Only the engine runs (no API server, no database)
- Lower resource usage, agents run autonomously

### 4. Deploy

Railway will automatically:
1. Run `scripts/generate_config.py` during the release phase (generates `config.yaml`)
2. Start the application with `run_with_api.py` (respects `API_ENABLED` setting)
3. Use the `PORT` environment variable (automatically set by Railway) for the API server (if enabled)

### 5. Verify Deployment

Once deployed, you can verify the deployment by:

1. **Check the logs** in Railway dashboard to see:
   - ✅ Config generation success message
   - ✅ Number of agents configured
   - ✅ API server startup message (if `API_ENABLED=true`)
   - ✅ Engine started message

2. **Test the API endpoints** (only if `API_ENABLED=true`):
   - `https://your-app.up.railway.app/health` - Health check
   - `https://your-app.up.railway.app/api/agents` - List all agents
   - `https://your-app.up.railway.app/api/activities` - List all activities

3. **Check agent activity**:
   - Agents should start running their cycles based on `cycle_interval_minutes`
   - Activities should appear in the `/api/activities` endpoint (if API enabled)
   - Check logs for cycle execution messages

## Configuration Details

### Activation Instructions

The `AGENT_N_ACTIVATION_INSTRUCTION` can be a multi-line string. In Railway, you can:
- Use a single line with `\n` for line breaks
- Or use Railway's multi-line variable support (if available)

Example:
```bash
AGENT_1_ACTIVATION_INSTRUCTION=please i want you to discover candidates, check positions for each, research, form a thesis using my balances and positions, then open the trade with the proposed size, don't tweet it, and no need to monitor it since trade always get executed immediately. make sure you open at least a single trade (buy or sell) every time. and report the portfolio pnl after.
```

### Disabling Agents

To temporarily disable an agent without removing its configuration:
```bash
AGENT_1_ENABLED=false
```

The agent will be loaded but not started by the engine.

### Port Configuration

Railway automatically sets the `PORT` environment variable. The API server will use this port automatically. You don't need to configure it manually.

## Troubleshooting

### Config Not Generated

If you see errors about `config.yaml` not found:
1. Check that `scripts/generate_config.py` ran successfully in the release phase
2. Verify all required environment variables are set
3. Check Railway logs for the release phase output

### Agents Not Starting

1. Verify `AGENT_N_ID` is correct and the agent exists in Letta
2. Check that `AGENT_N_ENABLED=true` (or not set, defaults to true)
3. Verify `LETTA_API_KEY` is valid
4. Check that `LETTA_BASE_URL` points to the correct Letta server

### API Server Not Accessible

1. Verify `API_ENABLED=true` (or not set, defaults to `true`)
2. Verify the `PORT` environment variable is set (Railway sets this automatically)
3. Check that the API server started successfully in logs
4. Verify CORS settings if accessing from a frontend

**Note:** If you set `API_ENABLED=false`, the API server will not start. This is expected behavior for "engine only" mode.

## Local Development

For local development, you can still use `config.yaml` directly. The `generate_config.py` script is only needed for Railway deployment.

To test the Railway configuration locally:
```bash
# Set environment variables
export LETTA_API_KEY=sk-let-...
export AGENT_1_NAME=Vibe
export AGENT_1_ID=agent-...

# Generate config
python scripts/generate_config.py

# Run the engine
python run_with_api.py
```

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Letta Documentation](https://docs.letta.com)
- See `README.md` for more information about the Agent Autonomous Engine

