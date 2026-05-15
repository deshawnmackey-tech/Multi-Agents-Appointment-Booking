# AI Agents

This directory contains the AI agents that power the Multi-Agent Appointment Booking System.

## Agent Architecture

The system uses a multi-agent architecture where specialized agents handle different aspects of appointment booking:

```
┌─────────────────┐
│   Coordinator   │  ← Orchestrates all agents
│     Agent       │
└────────┬────────┘
         │
    ┌────┴────┬────────┬──────────┬────────────┐
    │         │        │          │            │
┌───▼───┐ ┌──▼──┐ ┌───▼────┐ ┌───▼────┐ ┌────▼─────┐
│  NLP  │ │Sched│ │Conflict│ │ Notif  │ │Preference│
│ Agent │ │Agent│ │Detector│ │ Agent  │ │ Manager  │
└───────┘ └─────┘ └────────┘ └────────┘ └──────────┘
```

## Available Agents

### 1. Base Agent (`base.py`)
Abstract base class for all agents. Provides:
- LangChain integration
- OpenAI LLM initialization
- Message handling
- Error management

**Usage:**
```python
from src.agents.base import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="My Agent",
            system_prompt="You are a helpful assistant..."
        )
    
    def process(self, input_data):
        # Implement agent logic
        pass
```

### 2. Coordinator Agent (`coordinator.py`)
Orchestrates multiple agents to complete complex tasks.

**Features:**
- Agent registry and management
- Task routing
- Result aggregation
- Workflow coordination

**Usage:**
```python
from src.agents.coordinator import CoordinatorAgent, AgentType

coordinator = CoordinatorAgent()

# Register specialized agents
coordinator.register_agent(AgentType.NLP, nlp_agent)
coordinator.register_agent(AgentType.SCHEDULER, scheduler_agent)

# Process a task
result = coordinator.process({
    "task": "book_appointment",
    "data": {...}
})
```

### 3. NLP Agent (`nlp_agent.py`) ✨ NEW
Parses natural language appointment requests into structured data.

**Features:**
- Natural language understanding
- Date/time extraction
- Participant identification
- Ambiguity detection
- Clarification handling
- Alternative suggestions

**Usage:**
```python
from src.agents.nlp_agent import NLPAgent
from datetime import datetime

agent = NLPAgent()

# Parse a request
result = agent.process({
    "request": "Schedule a meeting with john@example.com tomorrow at 2pm",
    "user_timezone": "America/New_York",
    "current_time": datetime.now()
})

# Check result
if result["success"]:
    print(f"Title: {result['title']}")
    print(f"Date: {result['date']}")
    print(f"Time: {result['start_time']}")
    print(f"Confidence: {result['confidence']}")
```

**Example Requests:**
- "Schedule a meeting with john@example.com tomorrow at 2pm for 1 hour"
- "Book a team standup next Monday 9am, 30 minutes"
- "Set up a call with the design team on Friday afternoon"

**Response Format:**
```json
{
    "success": true,
    "title": "Meeting with John",
    "date": "2024-01-16",
    "start_time": "14:00",
    "duration_minutes": 60,
    "participants": ["john@example.com"],
    "location": null,
    "notes": null,
    "confidence": 0.95,
    "ambiguities": [],
    "clarification_needed": false,
    "original_request": "...",
    "processed_at": "2024-01-15T10:00:00"
}
```

## Running the Demo

Try the NLP Agent demo:

```bash
python examples/nlp_agent_demo.py
```

This will demonstrate:
1. Simple appointment parsing
2. Complex request handling
3. Ambiguity detection and clarification
4. Conflict resolution with alternatives

## Testing

Run agent tests:

```bash
# Test all agents
pytest tests/unit/test_agents/

# Test specific agent
pytest tests/unit/test_agents/test_nlp_agent.py

# With verbose output
pytest tests/unit/test_agents/ -v
```

## Configuration

Agents use configuration from `src/config.py`:

```python
# OpenAI settings
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
```

## Creating New Agents

To create a new specialized agent:

1. **Inherit from BaseAgent:**
```python
from src.agents.base import BaseAgent

class MySpecializedAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="My Specialized Agent",
            system_prompt="Your agent's role and instructions...",
            temperature=0.5  # Optional: adjust creativity
        )
```

2. **Implement the process method:**
```python
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input and return results.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Processing results
        """
        # Your agent logic here
        result = self.invoke(
            message=input_data["request"],
            context={"key": "value"}
        )
        
        return {
            "success": True,
            "result": result
        }
```

3. **Register with Coordinator:**
```python
from src.agents.coordinator import AgentType

# Add new agent type to enum if needed
coordinator.register_agent(AgentType.MY_AGENT, my_agent)
```

## Agent Best Practices

1. **Clear System Prompts**: Define the agent's role and capabilities clearly
2. **Structured Output**: Return consistent JSON structures
3. **Error Handling**: Always handle exceptions gracefully
4. **Logging**: Use the logger for debugging and monitoring
5. **Testing**: Write tests for each agent's functionality
6. **Temperature**: Adjust based on task (lower for parsing, higher for creativity)

## Future Agents (Planned)

- **Scheduler Optimizer Agent**: Find optimal meeting times
- **Conflict Detector Agent**: Identify scheduling conflicts
- **Notification Agent**: Send reminders and updates
- **Preference Manager Agent**: Learn and apply user preferences
- **Calendar Sync Agent**: Synchronize with external calendars

## Resources

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

---

**Built with ❤️ by Bob**