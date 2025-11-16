"""
Run the engine with API server in the background.

This script starts both the engine and the API server so you can:
1. Run agents autonomously
2. Query activities via REST API
"""
import logging
import os
import signal
import sys
import threading
import time
from pathlib import Path

import uvicorn
from rich.console import Console

from engine import AgentAutonomousEngine, load_config
from database import ActivityStorage
from api_server import app

console = Console()
logger = logging.getLogger(__name__)


def run_api_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server."""
    try:
        uvicorn.run(app, host=host, port=port, log_level="info")
    except Exception as e:
        logger.error(f"API server error: {e}", exc_info=True)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Agent Autonomous Engine with API Server",
        epilog="Starts both the engine and REST API for querying activities"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )
    parser.add_argument(
        "--agents",
        nargs="+",
        help="Specific agent IDs to run (default: all enabled)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--api-host",
        default="0.0.0.0",
        help="API server host (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--api-port",
        type=int,
        default=8000,
        help="API server port (default: 8000)",
    )
    parser.add_argument(
        "--no-api",
        action="store_true",
        help="Disable API server (run engine only)",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    from rich.logging import RichHandler
    logging.basicConfig(
        level=args.log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)],
    )
    
    try:
        # Load configuration
        config = load_config(args.config)
        
        # Initialize activity storage
        activity_storage = None
        if not args.no_api:
            try:
                activity_storage = ActivityStorage()
                logger.info("Activity storage initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize activity storage: {e}. API will not be available.")
                activity_storage = None
        
        # Create engine
        engine = AgentAutonomousEngine(config, activity_storage=activity_storage)
        
        # Start API server in background thread (if enabled)
        api_thread = None
        if not args.no_api and activity_storage:
            api_thread = threading.Thread(
                target=run_api_server,
                args=(args.api_host, args.api_port),
                daemon=True,
                name="api-server"
            )
            api_thread.start()
            console.print(f"\n[bold cyan]🌐 API Server running on http://{args.api_host}:{args.api_port}[/bold cyan]")
            console.print(f"[dim]   Endpoints: /api/activities, /api/agents, /api/stats/{{agent_id}}[/dim]\n")
            time.sleep(1)  # Give API server a moment to start
        
        # Start engine (this will block until interrupted)
        engine.start(agent_ids=args.agents)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Keyboard interrupt received[/yellow]")
        try:
            engine.stop()
        except:
            pass
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logging.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()

