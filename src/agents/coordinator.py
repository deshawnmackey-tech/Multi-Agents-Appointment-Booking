"""
Coordinator agent for orchestrating multi-agent workflows.
"""
from typing import Any, Dict, List
from enum import Enum

from src.agents.base import BaseAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AgentType(str, Enum):
    """Types of agents in the system."""
    NLP = "nlp"
    SCHEDULER = "scheduler"
    CONFLICT_DETECTOR = "conflict_detector"
    NOTIFICATION = "notification"
    PREFERENCE_MANAGER = "preference_manager"


class CoordinatorAgent(BaseAgent):
    """
    Coordinator agent that orchestrates multiple specialized agents.
    
    This agent acts as a supervisor, routing tasks to appropriate
    specialized agents and combining their results.
    """
    
    def __init__(self):
        """Initialize the coordinator agent."""
        system_prompt = """You are a coordinator agent for an appointment booking system.
Your role is to:
1. Analyze user requests and determine which specialized agents to invoke
2. Coordinate between multiple agents to complete complex tasks
3. Combine results from different agents into coherent responses
4. Handle errors and fallback scenarios

Available agents:
- NLP Agent: Parse natural language appointment requests
- Scheduler Agent: Find optimal appointment times
- Conflict Detector: Check for scheduling conflicts
- Notification Agent: Send notifications to users
- Preference Manager: Manage user preferences and availability

Always provide clear, actionable responses and explain your reasoning."""
        
        super().__init__(
            name="Coordinator",
            system_prompt=system_prompt
        )
        
        # Registry of available agents
        self.agents: Dict[AgentType, BaseAgent] = {}
    
    def register_agent(self, agent_type: AgentType, agent: BaseAgent) -> None:
        """
        Register a specialized agent.
        
        Args:
            agent_type: Type of agent
            agent: Agent instance
        """
        self.agents[agent_type] = agent
        logger.info(f"Registered {agent_type.value} agent")
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request by coordinating multiple agents.
        
        Args:
            input_data: Request data containing:
                - task: Task type (e.g., "book_appointment", "check_availability")
                - data: Task-specific data
                
        Returns:
            Processing results
        """
        task = input_data.get("task")
        data = input_data.get("data", {})
        
        logger.info(f"Coordinator processing task: {task}")
        
        try:
            if task == "book_appointment":
                return self._handle_booking(data)
            elif task == "check_availability":
                return self._handle_availability_check(data)
            elif task == "resolve_conflict":
                return self._handle_conflict_resolution(data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown task: {task}"
                }
        except Exception as e:
            logger.error(f"Coordinator error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _handle_booking(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle appointment booking workflow.
        
        Args:
            data: Booking request data
            
        Returns:
            Booking result
        """
        # TODO: Implement booking workflow
        # 1. Use NLP agent to parse request
        # 2. Use preference manager to get user preferences
        # 3. Use scheduler to find optimal time
        # 4. Use conflict detector to check for conflicts
        # 5. Create appointment
        # 6. Use notification agent to send confirmations
        
        return {
            "success": True,
            "message": "Booking workflow not yet implemented",
            "data": data
        }
    
    def _handle_availability_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle availability check workflow.
        
        Args:
            data: Availability check data
            
        Returns:
            Availability results
        """
        # TODO: Implement availability check workflow
        # 1. Get user preferences
        # 2. Query existing appointments
        # 3. Calculate available slots
        
        return {
            "success": True,
            "message": "Availability check not yet implemented",
            "data": data
        }
    
    def _handle_conflict_resolution(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle conflict resolution workflow.
        
        Args:
            data: Conflict data
            
        Returns:
            Resolution suggestions
        """
        # TODO: Implement conflict resolution workflow
        # 1. Use conflict detector to identify conflicts
        # 2. Use scheduler to suggest alternatives
        # 3. Consider user preferences
        
        return {
            "success": True,
            "message": "Conflict resolution not yet implemented",
            "data": data
        }
    
    def get_agent(self, agent_type: AgentType) -> BaseAgent:
        """
        Get a registered agent by type.
        
        Args:
            agent_type: Type of agent to retrieve
            
        Returns:
            Agent instance
            
        Raises:
            KeyError: If agent type not registered
        """
        if agent_type not in self.agents:
            raise KeyError(f"Agent type {agent_type.value} not registered")
        
        return self.agents[agent_type]

# Made with Bob