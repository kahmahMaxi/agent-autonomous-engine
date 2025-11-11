# Use Cases & Examples

## Autonomous Trading with Animus Vibe

### Setup

1. **Register Aster tools with agents:**
   ```bash
   cd animus-vibe
   python scripts/register_aster_tools.py --agent-id agent-id-1
   python scripts/register_aster_tools.py --agent-id agent-id-2
   ```

2. **Set Aster credentials in Letta:**
   - For each agent, add in Letta agent environment variables:
     - `ASTER_API_KEY` = agent's Aster API key
     - `ASTER_API_SECRET` = agent's Aster API secret

3. **Configure engine:**
   ```yaml
   agents:
     - name: "Trading Agent Alpha"
       agent_id: "agent-id-1"
       cycle_interval_minutes: 15
       activation_instruction: |
         Review market conditions and your portfolio status.
         
         Your trading process:
         1. Research trending coins and market opportunities
         2. Form trading theses based on research data
         3. Execute trades when confidence is high (>60%)
         4. Monitor open positions and manage risk
         5. Learn from outcomes and adjust strategy
         
         Be strategic, risk-aware, and goal-oriented.
         Don't trade impulsively - make data-driven decisions.
       enabled: true
   ```

4. **Run engine:**
   ```bash
   python engine.py
   ```

### How It Works

- **Every 15 minutes**, the agent receives the activation instruction
- Agent uses `research_coin` to analyze markets
- Agent uses `propose_thesis` to form trading strategies
- Agent uses `open_trade` to execute when confident
- Agent uses `monitor_trade` to track positions
- All decisions are autonomous - no manual intervention needed

### Multi-Agent Trading Network

Run multiple agents with different strategies:

```yaml
agents:
  - name: "Conservative Trader"
    cycle_interval_minutes: 30
    activation_instruction: |
      Focus on low-risk, high-confidence trades.
      Require >75% confidence before executing.
      Limit position size to 3% of portfolio.
  
  - name: "Momentum Trader"
    cycle_interval_minutes: 10
    activation_instruction: |
      Scan for high-momentum opportunities.
      Execute quickly on trending coins.
      Take calculated risks for higher returns.
  
  - name: "Portfolio Manager"
    cycle_interval_minutes: 60
    activation_instruction: |
      Monitor all positions across the network.
      Rebalance portfolio as needed.
      Generate performance reports.
```

## Social Media Agents

### Twitter/Bluesky Agents

```yaml
agents:
  - name: "Community Builder"
    cycle_interval_minutes: 20
    activation_instruction: |
      Check for mentions and interesting conversations.
      Engage authentically with your community.
      Share valuable insights and build relationships.
      Post updates when you have something meaningful to say.
```

### Discord Agents

```yaml
agents:
  - name: "Discord Moderator"
    cycle_interval_minutes: 5
    activation_instruction: |
      Monitor server activity and conversations.
      Answer questions and provide support.
      Maintain community guidelines.
      Foster positive engagement.
```

## Research & Analysis Agents

```yaml
agents:
  - name: "Crypto Researcher"
    cycle_interval_minutes: 60
    activation_instruction: |
      Discover trending topics and emerging projects.
      Conduct deep research and analysis.
      Share findings and insights.
      Build knowledge base over time.
```

## Multi-Domain Agents

```yaml
agents:
  - name: "Omnibus Agent"
    cycle_interval_minutes: 15
    activation_instruction: |
      Review all your goals across trading, social, and research.
      Prioritize actions based on current opportunities.
      Execute strategically across domains.
      Balance time and resources effectively.
```

## Custom Workflows

### Discovery → Research → Action Pipeline

```yaml
agents:
  - name: "Opportunity Scout"
    cycle_interval_minutes: 5
    activation_instruction: "Discover new opportunities and trends"
  
  - name: "Deep Researcher"
    cycle_interval_minutes: 15
    activation_instruction: "Research opportunities discovered by scout"
  
  - name: "Action Executor"
    cycle_interval_minutes: 30
    activation_instruction: "Execute on researched opportunities"
```

### Monitoring & Alerting

```yaml
agents:
  - name: "Market Monitor"
    cycle_interval_minutes: 5
    activation_instruction: |
      Monitor market conditions continuously.
      Alert on significant changes or opportunities.
      Track key metrics and trends.
```

## Best Practices

1. **Start Conservative** - Begin with longer intervals (30-60min)
2. **Monitor Performance** - Use `--status` to track agent activity
3. **Adjust Instructions** - Refine activation instructions based on results
4. **Test Tools** - Ensure tools are registered and working before running
5. **Set Credentials** - Verify agent credentials in Letta env vars

## Tips

- Use descriptive agent names
- Craft clear, actionable activation instructions
- Match cycle intervals to use case (trading: 10-30min, research: 60min+)
- Monitor logs to understand agent behavior
- Adjust instructions based on agent performance

