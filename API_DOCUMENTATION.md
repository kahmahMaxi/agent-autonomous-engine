# Agent Autonomous Engine API Documentation

## Overview

The API provides REST endpoints for querying agent activities, statistics, and performance metrics. This enables frontend applications to display real-time agent activities, performance charts, and activity cards.

## Base URL

- **Local**: `http://localhost:8000`
- **Railway**: `https://your-app-name.up.railway.app` (your Railway URL)

## Endpoints

### 1. Get All Activities

**GET** `/api/activities`

Get activities from all agents or filter by specific agent.

**Query Parameters:**
- `agent_id` (optional): Filter by specific agent ID
- `limit` (optional, default: 100): Maximum number of records (1-1000)
- `offset` (optional, default: 0): Pagination offset
- `hours` (optional): Filter activities from last N hours

**Example:**
```bash
# Get last 50 activities from all agents
GET /api/activities?limit=50

# Get activities for specific agent from last 24 hours
GET /api/activities?agent_id=agent-123&hours=24

# Pagination
GET /api/activities?limit=20&offset=40
```

**Response:**
```json
[
  {
    "id": 1,
    "agent_id": "agent-29ae4ac5-e281-4c17-99b9-26c38800216e",  // Always included - identifies which agent
    "agent_name": "Vibe",  // Always included - display name for frontend
    "cycle_number": 5,
    "timestamp": "2024-01-15T10:30:00",
    "response_text": "I've checked your balances...",
    "tool_calls": [
      {
        "name": "check_balance",
        "arguments": {},
        "id": "call_123"
      }
    ],
    "stop_reason": "tool_use",
    "usage": {
      "tokens": 1500,
      "input_tokens": 800,
      "output_tokens": 700
    },
    "status": "success",
    "error_message": null,
    "metadata": {
      "activation_instruction": "Please check my balances and positions."
    }
  }
]
```

**Note:** Every activity response includes `agent_id` and `agent_name`, so your frontend can:
- Display which agent performed each activity
- Group activities by agent
- Filter activities client-side if needed
- Show agent names in activity cards

### 2. Get Agent Activities

**GET** `/api/activities/{agent_id}`

Get activities for a specific agent.

**Path Parameters:**
- `agent_id`: Agent ID

**Query Parameters:**
- `limit` (optional, default: 100): Maximum number of records
- `offset` (optional, default: 0): Pagination offset
- `hours` (optional): Filter activities from last N hours

**Example:**
```bash
GET /api/activities/agent-29ae4ac5-e281-4c17-99b9-26c38800216e?limit=20&hours=12
```

### 3. Get All Agents

**GET** `/api/agents`

Get list of all agents with their latest activity info.

**Example:**
```bash
GET /api/agents
```

**Response:**
```json
[
  {
    "agent_id": "agent-29ae4ac5-e281-4c17-99b9-26c38800216e",
    "agent_name": "Vibe",
    "last_activity": "2024-01-15T10:30:00",
    "total_cycles": 42
  }
]
```

### 4. Get Agent Statistics

**GET** `/api/stats/{agent_id}`

Get performance statistics for an agent over a time period.

**Path Parameters:**
- `agent_id`: Agent ID

**Query Parameters:**
- `days` (optional, default: 7): Number of days to look back (1-365)

**Example:**
```bash
GET /api/stats/agent-29ae4ac5-e281-4c17-99b9-26c38800216e?days=30
```

**Response:**
```json
{
  "agent_id": "agent-29ae4ac5-e281-4c17-99b9-26c38800216e",
  "agent_name": "Vibe",
  "total_cycles": 120,
  "successful_cycles": 115,
  "error_cycles": 3,
  "rate_limit_cycles": 2,
  "total_tool_calls": 450,
  "total_tokens": 180000,
  "avg_tokens_per_cycle": 1500.0,
  "period_days": 7
}
```

### 5. Health Check

**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "storage": "initialized"
}
```

## Frontend Integration Examples

### React Example

```javascript
// Fetch recent activities
const fetchActivities = async (agentId = null, hours = 24) => {
  const url = agentId 
    ? `/api/activities/${agentId}?hours=${hours}`
    : `/api/activities?hours=${hours}`;
  
  const response = await fetch(url);
  return await response.json();
};

// Fetch agent stats for charts
const fetchAgentStats = async (agentId, days = 7) => {
  const response = await fetch(`/api/stats/${agentId}?days=${days}`);
  return await response.json();
};

// Poll for new activities (every 5 seconds)
useEffect(() => {
  const interval = setInterval(async () => {
    const activities = await fetchActivities();
    setActivities(activities);
  }, 5000);
  
  return () => clearInterval(interval);
}, []);
```

### Activity Card Data Structure

Each activity contains:
- **agent_id**: Unique agent identifier (always included)
- **agent_name**: Display name for the agent (always included) - use this in your UI
- **response_text**: What the agent said/did
- **tool_calls**: Array of tools executed (e.g., `check_balance`, `open_trade`)
- **timestamp**: When it happened
- **status**: success, error, or rate_limit
- **usage**: Token consumption metrics
- **cycle_number**: Which cycle this activity belongs to
- **stop_reason**: Why the agent stopped (e.g., "tool_use", "max_tokens")

## Database

- **Local**: SQLite database in `data/activities.db`
- **Railway**: PostgreSQL (set `DATABASE_URL` environment variable)

The database automatically creates tables on first run.

## CORS

The API includes CORS middleware allowing requests from any origin. In production, you may want to restrict this to your frontend domain.

