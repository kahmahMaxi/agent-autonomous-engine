"""
Agent Autonomous Engine

Autonomous decision cycle orchestrator for Letta agents.

Enables true agent autonomy by periodically activating agents to make independent
decisions using their registered tools and memory systems.

Author: Kamal
License: MIT
"""
import logging
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from letta_client import Letta, MessageCreate
from rich.console import Console
from rich.table import Table

logger = logging.getLogger(__name__)
console = Console()


class AgentConfig:
    """Configuration for a single agent."""
    
    def __init__(self, name: str, agent_id: str, cycle_interval_minutes: int, activation_instruction: str, enabled: bool = True):
        self.name = name
        self.agent_id = agent_id
        self.cycle_interval_minutes = cycle_interval_minutes
        self.activation_instruction = activation_instruction
        self.enabled = enabled


class EngineConfig:
    """Engine configuration."""
    
    def __init__(self, letta_api_key: str, letta_base_url: str, letta_timeout: int, agents: List[AgentConfig]):
        self.letta_api_key = letta_api_key
        self.letta_base_url = letta_base_url
        self.letta_timeout = letta_timeout
        self.agents = agents


class AgentRunner:
    """Orchestrates autonomous decision cycles for a single agent."""
    
    def __init__(self, agent_config: AgentConfig, letta_client: Letta, activity_storage=None):
        """
        Initialize agent runner.
        
        Args:
            agent_config: Agent configuration
            letta_client: Letta client instance
            activity_storage: Optional ActivityStorage instance for logging activities
        """
        self.agent_config = agent_config
        self.letta = letta_client
        self.activity_storage = activity_storage
        self.running = False
        self.stats = {
            "cycles_completed": 0,
            "errors": 0,
            "last_activation": None,
            "started_at": None,
        }
    
    def run(self):
        """Run autonomous decision cycle loop."""
        logger.info(f"Activating autonomous agent: {self.agent_config.name}")
        self.running = True
        self.stats["started_at"] = datetime.now()
        
        # Run first activation cycle immediately
        self._activate_agent()
        
        while self.running:
            try:
                # Sleep in smaller chunks to check running flag more frequently
                sleep_seconds = self.agent_config.cycle_interval_minutes * 60
                chunk_size = 1.0  # Check every second
                
                for _ in range(int(sleep_seconds / chunk_size)):
                    if not self.running:
                        break
                    time.sleep(chunk_size)
                
                if not self.running:
                    break
                
                # Activate agent for decision cycle
                self._activate_agent()
                
            except KeyboardInterrupt:
                logger.info(f"Interrupted: stopping agent runner {self.agent_config.name}")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in agent runner {self.agent_config.name}: {e}", exc_info=True)
                self.stats["errors"] += 1
                # Sleep in chunks to allow interruption
                for _ in range(10):
                    if not self.running:
                        break
                    time.sleep(1)
        
        logger.info(f"Agent runner stopped: {self.agent_config.name}")
    
    def _activate_agent(self):
        """Activate agent for autonomous decision cycle."""
        response = None
        status = "success"
        error_message = None
        
        try:
            logger.info(f"[{self.agent_config.name}] Activating autonomous decision cycle...")
            
            # Activate agent with instruction for decision-making
            # Letta handles tool execution, memory retrieval, and strategic planning
            message_data = [MessageCreate(role="user", content=self.agent_config.activation_instruction)]
            
            response = self.letta.agents.messages.create(
                agent_id=self.agent_config.agent_id,
                messages=message_data
            )
            
            self.stats["cycles_completed"] += 1
            self.stats["last_activation"] = datetime.now().isoformat()
            
            logger.info(f"[{self.agent_config.name}] ✓ Decision cycle completed (total: {self.stats['cycles_completed']})")
            
        except Exception as e:
            # Handle rate limit errors gracefully
            error_str = str(e)
            if "429" in error_str or "rate_limit" in error_str.lower() or "quota" in error_str.lower():
                status = "rate_limit"
                error_message = str(e)
                logger.warning(
                    f"[{self.agent_config.name}] Rate limit/quota exceeded. "
                    f"Skipping this cycle. Check your OpenAI/LLM provider quota."
                )
                # Don't count rate limits as errors - they're expected
                # The agent will try again on next cycle
            else:
                status = "error"
                error_message = str(e)
                logger.error(f"[{self.agent_config.name}] Decision cycle failed: {e}", exc_info=True)
                self.stats["errors"] += 1
        
        finally:
            # Store activity in database if storage is available
            if self.activity_storage:
                try:
                    cycle_number = self.stats["cycles_completed"]
                    self.activity_storage.store_activity(
                        agent_id=self.agent_config.agent_id,
                        agent_name=self.agent_config.name,
                        cycle_number=cycle_number,
                        response=response,
                        status=status,
                        error_message=error_message,
                        metadata={
                            "activation_instruction": self.agent_config.activation_instruction,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to store activity: {e}", exc_info=True)


class AgentAutonomousEngine:
    """Main engine that runs multiple agents."""
    
    def __init__(self, config: EngineConfig, activity_storage=None):
        """
        Initialize engine.
        
        Args:
            config: Engine configuration
            activity_storage: Optional ActivityStorage instance for logging activities
        """
        self.config = config
        self.running = False
        self.agent_runners: Dict[str, AgentRunner] = {}
        self.agent_threads: Dict[str, threading.Thread] = {}
        self.activity_storage = activity_storage
        
        # Initialize Letta client
        client_params = {
            'token': config.letta_api_key,
            'timeout': config.letta_timeout,
        }
        if config.letta_base_url:
            client_params['base_url'] = config.letta_base_url
        
        self.letta = Letta(**client_params)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        console.print(f"\n[yellow]Received signal {signum}, shutting down...[/yellow]")
        self.stop()
        # Give threads a moment to stop
        time.sleep(1)
        sys.exit(0)
    
    def start(self, agent_ids: Optional[List[str]] = None):
        """
        Start engine and run all enabled agents.
        
        Args:
            agent_ids: Optional list of specific agent IDs to run
        """
        console.print("[bold cyan]╔═══════════════════════════════════════════════════════════╗[/bold cyan]")
        console.print("[bold cyan]║[/bold cyan]  [bold white]🤖 Agent Autonomous Engine - Activating Agents[/bold white]  [bold cyan]║[/bold cyan]")
        console.print("[bold cyan]╚═══════════════════════════════════════════════════════════╝[/bold cyan]\n")
        
        # Get agents to run
        agents_to_run = [
            a for a in self.config.agents
            if a.enabled and (not agent_ids or a.agent_id in agent_ids)
        ]
        
        if not agents_to_run:
            console.print("[red]No agents to run![/red]")
            return
        
        console.print(f"[cyan]Found {len(agents_to_run)} agent(s):[/cyan]")
        for agent in agents_to_run:
            console.print(f"  • {agent.name} (cycle: {agent.cycle_interval_minutes}min)")
        console.print()
        
        # Start each agent in its own thread
        self.running = True
        
        for agent_config in agents_to_run:
            try:
                runner = AgentRunner(agent_config, self.letta, self.activity_storage)
                self.agent_runners[agent_config.agent_id] = runner
                
                # Start agent in separate thread
                thread = threading.Thread(
                    target=runner.run,
                    name=f"agent-{agent_config.name}",
                    daemon=True,
                )
                thread.start()
                self.agent_threads[agent_config.agent_id] = thread
                
                console.print(f"[green]✓ Started: {agent_config.name}[/green]")
                
            except Exception as e:
                console.print(f"[red]✗ Failed to start {agent_config.name}: {e}[/red]")
                logger.error(f"Failed to start agent {agent_config.name}: {e}", exc_info=True)
        
        console.print(f"\n[bold green]✅ Autonomous Engine Active[/bold green]")
        console.print(f"[cyan]   {len(self.agent_runners)} agent(s) operating autonomously[/cyan]")
        console.print(f"[dim]   Press Ctrl+C to deactivate[/dim]\n")
        
        # Wait for all threads with timeout to allow interruption
        try:
            while any(t.is_alive() for t in self.agent_threads.values()):
                time.sleep(0.5)
                if not self.running:
                    break
        except KeyboardInterrupt:
            console.print("\n[yellow]Keyboard interrupt received, shutting down...[/yellow]")
            self.stop()
    
    def stop(self):
        """Stop all agents and engine."""
        console.print("\n[yellow]Stopping engine...[/yellow]")
        self.running = False
        
        for agent_id, runner in self.agent_runners.items():
            runner.running = False
            console.print(f"[yellow]Stopped: {runner.agent_config.name}[/yellow]")
        
        console.print("[green]Engine stopped[/green]")
    
    def print_status(self):
        """Print status table."""
        table = Table(title="Engine Status")
        table.add_column("Agent", style="cyan")
        table.add_column("Cycle Interval", style="blue")
        table.add_column("Cycles", style="green")
        table.add_column("Last Activation", style="yellow")
        table.add_column("Errors", style="red")
        
        for agent_id, runner in self.agent_runners.items():
            stats = runner.stats
            last_activation = stats.get("last_activation", "Never")
            if last_activation and last_activation != "Never":
                try:
                    dt = datetime.fromisoformat(last_activation)
                    last_activation = dt.strftime("%H:%M:%S")
                except:
                    pass
            
            table.add_row(
                runner.agent_config.name,
                f"{runner.agent_config.cycle_interval_minutes}min",
                str(stats.get("cycles_completed", 0)),
                last_activation,
                str(stats.get("errors", 0)),
            )
        
        console.print(table)


def load_config(config_path: str = "config.yaml") -> EngineConfig:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file
    
    Returns:
        EngineConfig object
    """
    import os
    
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"Please copy config.yaml.template to config.yaml and fill in your values."
        )
    
    with open(config_file, 'r') as f:
        config_dict = yaml.safe_load(f) or {}
    
    # Get Letta config (support env vars)
    letta_dict = config_dict.get('letta', {})
    letta_api_key = letta_dict.get('api_key') or os.getenv('LETTA_API_KEY', '')
    letta_base_url = letta_dict.get('base_url') or os.getenv('LETTA_BASE_URL', 'https://app.letta.com')
    letta_timeout = letta_dict.get('timeout', 600)
    
    if not letta_api_key:
        raise ValueError("Letta API key required (set in config.yaml or LETTA_API_KEY env var)")
    
    # Load agents
    agents = []
    for agent_dict in config_dict.get('agents', []):
        agent = AgentConfig(
            name=agent_dict.get('name', ''),
            agent_id=agent_dict.get('agent_id', ''),
            cycle_interval_minutes=agent_dict.get('cycle_interval_minutes', agent_dict.get('interval_minutes', 15)),  # Support both for backward compat
            activation_instruction=agent_dict.get('activation_instruction', agent_dict.get('prompt', 'What should you do now?')),  # Support both
            enabled=agent_dict.get('enabled', True),
        )
        
        if agent.agent_id:
            agents.append(agent)
        else:
            logger.warning(f"Agent {agent.name} missing agent_id, skipping")
    
    return EngineConfig(
        letta_api_key=letta_api_key,
        letta_base_url=letta_base_url,
        letta_timeout=letta_timeout,
        agents=agents,
    )


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Agent Autonomous Engine - Orchestrate autonomous decision cycles for Letta agents",
        epilog="For more information, see https://github.com/your-org/agent-autonomous-engine"
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
        "--status",
        action="store_true",
        help="Show status and exit",
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
        
        # Initialize activity storage (optional - only if API is enabled)
        activity_storage = None
        if os.getenv('ENABLE_ACTIVITY_STORAGE', 'true').lower() == 'true':
            try:
                from database import ActivityStorage
                activity_storage = ActivityStorage()
                logger.info("Activity storage enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize activity storage: {e}. Activities will not be stored.")
        
        # Create engine
        engine = AgentAutonomousEngine(config, activity_storage=activity_storage)
        
        if args.status:
            engine.print_status()
            return
        
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

