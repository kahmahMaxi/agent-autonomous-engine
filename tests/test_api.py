"""
Simple script to test the API endpoints.

Run this after starting the engine with API to verify endpoints are working.
"""
import requests
import json
from datetime import datetime

API_BASE = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("🔍 Testing /health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Health check: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_root():
    """Test root endpoint."""
    print("\n🔍 Testing / endpoint...")
    try:
        response = requests.get(f"{API_BASE}/")
        response.raise_for_status()
        data = response.json()
        print(f"✅ Root endpoint: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False


def test_get_agents():
    """Test /api/agents endpoint."""
    print("\n🔍 Testing /api/agents endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/agents")
        response.raise_for_status()
        agents = response.json()
        print(f"✅ Found {len(agents)} agent(s):")
        for agent in agents:
            print(f"   - {agent['agent_name']} ({agent['agent_id']})")
            print(f"     Last activity: {agent.get('last_activity', 'Never')}")
            print(f"     Total cycles: {agent.get('total_cycles', 0)}")
        return agents
    except Exception as e:
        print(f"❌ Get agents failed: {e}")
        return []


def test_get_activities(agent_id=None, limit=5):
    """Test /api/activities endpoint."""
    print(f"\n🔍 Testing /api/activities endpoint (limit={limit})...")
    try:
        url = f"{API_BASE}/api/activities"
        params = {"limit": limit}
        if agent_id:
            url = f"{API_BASE}/api/activities/{agent_id}"
            params = {"limit": limit}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        activities = response.json()
        print(f"✅ Found {len(activities)} activity/ies:")
        
        for activity in activities:
            print(f"\n   Activity #{activity['id']}:")
            print(f"   - Agent: {activity['agent_name']} ({activity['agent_id']})")
            print(f"   - Cycle: {activity['cycle_number']}")
            print(f"   - Time: {activity['timestamp']}")
            print(f"   - Status: {activity['status']}")
            if activity.get('response_text'):
                text = activity['response_text'][:100] + "..." if len(activity['response_text']) > 100 else activity['response_text']
                print(f"   - Response: {text}")
            if activity.get('tool_calls'):
                print(f"   - Tools used: {[tc.get('name') for tc in activity['tool_calls']]}")
        
        return activities
    except Exception as e:
        print(f"❌ Get activities failed: {e}")
        return []


def test_get_stats(agent_id):
    """Test /api/stats/{agent_id} endpoint."""
    print(f"\n🔍 Testing /api/stats/{agent_id} endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/stats/{agent_id}")
        response.raise_for_status()
        stats = response.json()
        print(f"✅ Statistics for {stats.get('agent_name', 'Unknown')}:")
        print(f"   - Total cycles: {stats['total_cycles']}")
        print(f"   - Successful: {stats['successful_cycles']}")
        print(f"   - Errors: {stats['error_cycles']}")
        print(f"   - Rate limits: {stats['rate_limit_cycles']}")
        print(f"   - Total tool calls: {stats['total_tool_calls']}")
        print(f"   - Total tokens: {stats['total_tokens']:,}")
        print(f"   - Avg tokens/cycle: {stats['avg_tokens_per_cycle']}")
        return stats
    except Exception as e:
        print(f"❌ Get stats failed: {e}")
        return None


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Testing Agent Autonomous Engine API")
    print("=" * 60)
    print(f"\nAPI Base URL: {API_BASE}")
    print("Make sure the engine is running with: python run_with_api.py\n")
    
    # Test health
    if not test_health():
        print("\n❌ API server is not running or not accessible!")
        print("   Start it with: python run_with_api.py")
        return
    
    # Test root
    test_root()
    
    # Test agents
    agents = test_get_agents()
    
    # Test activities
    activities = test_get_activities(limit=5)
    
    # Test stats for first agent if available
    if agents and len(agents) > 0:
        first_agent_id = agents[0]['agent_id']
        test_get_stats(first_agent_id)
    
    # Test agent-specific activities if available
    if agents and len(agents) > 0:
        first_agent_id = agents[0]['agent_id']
        print(f"\n🔍 Testing /api/activities/{first_agent_id} endpoint...")
        test_get_activities(agent_id=first_agent_id, limit=3)
    
    print("\n" + "=" * 60)
    print("✅ API Testing Complete!")
    print("=" * 60)
    print("\n💡 Tips:")
    print("   - If no activities show up, wait for an agent cycle to complete")
    print("   - Check browser: http://localhost:8000/api/activities")
    print("   - View API docs: http://localhost:8000/docs (FastAPI auto-docs)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()

