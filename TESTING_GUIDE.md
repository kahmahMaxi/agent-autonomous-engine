# Testing Guide - Agent Autonomous Engine API

## Quick Start Testing

### Step 1: Start the Engine with API

Open a terminal and run:

```bash
cd agent-autonomous-engine

# Activate virtual environment (if not already active)
# Windows:
venv\Scripts\Activate.ps1
# Linux/WSL:
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Start engine with API server
python run_with_api.py
```

You should see:
```
🌐 API Server running on http://0.0.0.0:8000
   Endpoints: /api/activities, /api/agents, /api/stats/{agent_id}

╔═══════════════════════════════════════════════════════════╗
║  🤖 Agent Autonomous Engine - Activating Agents  ║
╚═══════════════════════════════════════════════════════════╝
```

### Step 2: Wait for Agent Cycle

The engine runs agents at their configured intervals. Wait for at least one cycle to complete (check your `cycle_interval_minutes` in `config.yaml`).

For testing, you can set a short interval like `0.5` minutes (30 seconds) in your config.

### Step 3: Test the API

**Option A: Use the Test Script (Recommended)**

Open a **new terminal** (keep the engine running in the first terminal):

```bash
cd agent-autonomous-engine

# Activate virtual environment
venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate  # Linux/WSL

# Run test script
python tests/test_api.py
```

This will test all endpoints and show you the results.

**Option B: Use Browser**

1. Open your browser and go to:
   - `http://localhost:8000/health` - Health check
   - `http://localhost:8000/api/agents` - List all agents
   - `http://localhost:8000/api/activities` - Get all activities
   - `http://localhost:8000/docs` - **Interactive API documentation** (FastAPI auto-generated)

**Option C: Use curl (Command Line)**

```bash
# Health check
curl http://localhost:8000/health

# Get all agents
curl http://localhost:8000/api/agents

# Get all activities
curl http://localhost:8000/api/activities?limit=5

# Get activities for specific agent (replace with your agent_id)
curl http://localhost:8000/api/activities/agent-29ae4ac5-e281-4c17-99b9-26c38800216e

# Get agent stats
curl http://localhost:8000/api/stats/agent-29ae4ac5-e281-4c17-99b9-26c38800216e
```

**Option D: Use FastAPI Interactive Docs (Best for Testing)**

1. Start the engine with API
2. Open browser: `http://localhost:8000/docs`
3. You'll see an interactive Swagger UI where you can:
   - See all endpoints
   - Test endpoints directly in the browser
   - See request/response schemas
   - Try different parameters

## Expected Results

### 1. Health Check (`/health`)

```json
{
  "status": "healthy",
  "storage": "initialized"
}
```

### 2. Get Agents (`/api/agents`)

```json
[
  {
    "agent_id": "agent-29ae4ac5-e281-4c17-99b9-26c38800216e",
    "agent_name": "Vibe",
    "last_activity": "2024-01-15T10:30:00",
    "total_cycles": 5
  }
]
```

### 3. Get Activities (`/api/activities`)

```json
[
  {
    "id": 1,
    "agent_id": "agent-29ae4ac5-e281-4c17-99b9-26c38800216e",
    "agent_name": "Vibe",
    "cycle_number": 1,
    "timestamp": "2024-01-15T10:30:00",
    "response_text": "I've checked your balances...",
    "tool_calls": [{"name": "check_balance", "arguments": {}}],
    "status": "success",
    ...
  }
]
```

## Troubleshooting

### No Activities Showing?

1. **Wait for agent cycle**: Activities are only created when agents complete a cycle
2. **Check agent is running**: Look at the engine logs to see if agents are activating
3. **Check database**: The database is created in `data/activities.db` (SQLite) - you can verify it exists

### API Server Not Starting?

1. **Check port 8000 is free**: Another app might be using it
2. **Change port**: Use `python run_with_api.py --api-port 8001`
3. **Check dependencies**: Run `pip install -r requirements.txt`

### Database Errors?

1. **SQLite (local)**: Should work automatically - check `data/` folder exists
2. **PostgreSQL (Railway)**: Make sure `DATABASE_URL` env var is set correctly

### No Data in Response?

- This is normal if no agent cycles have completed yet
- Wait for at least one cycle to finish
- Check engine logs to see when cycles complete

## Quick Test Checklist

- [ ] Engine starts without errors
- [ ] API server shows "running on http://0.0.0.0:8000"
- [ ] `/health` returns `{"status": "healthy"}`
- [ ] `/api/agents` returns list (may be empty initially)
- [ ] `/api/activities` returns list (may be empty until first cycle)
- [ ] After agent cycle completes, activities appear
- [ ] `/api/stats/{agent_id}` returns statistics

## Next Steps

Once you see data in the API responses:

1. **Test in your frontend**: Point your frontend to `http://localhost:8000/api/activities`
2. **Deploy to Railway**: Set `DATABASE_URL` and your API will be available at your Railway URL
3. **Monitor**: Use `/api/stats/{agent_id}` for performance charts

