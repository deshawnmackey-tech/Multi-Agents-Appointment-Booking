"""
Base agent class for all AI agents in the system.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union
from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, SystemMessage

from src.config import get_settings
from src.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    Provides common functionality for LangChain-based agents including
    LLM initialization, message handling, and error management.
    """
    
    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name for logging and identification
            system_prompt: System prompt defining agent behavior
            model: Optional OpenAI model override
            temperature: Optional temperature override
        """
        self.name = name
        self.system_prompt = system_prompt
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model or settings.openai_model,
            temperature=temperature or settings.openai_temperature,
            max_tokens=settings.openai_max_tokens,
            api_key=settings.openai_api_key.get_secret_value()
        )
        
        logger.info(f"Initialized {self.name} agent")
    
    def _create_messages(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[BaseMessage]:
        """
        Create message list for LLM.
        
        Args:
            user_message: User's message
            context: Optional context dictionary
            
        Returns:
            List of messages for LLM
        """
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add context if provided
        if context:
            context_str = "\n".join(
                f"{key}: {value}" for key, value in context.items()
            )
            messages.append(
                SystemMessage(content=f"Context:\n{context_str}")
            )
        
        messages.append(HumanMessage(content=user_message))
        
        return messages
    
    def invoke(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Invoke the agent with a message.
        
        Args:
            message: User message
            context: Optional context dictionary
            
        Returns:
            Agent's response
        """
        try:
            messages = self._create_messages(message, context)
            response = self.llm.invoke(messages)
            
            logger.info(f"{self.name} processed message successfully")
            # Handle both string and list content
            if isinstance(response.content, str):
                return response.content
            return str(response.content)
            
        except Exception as e:
            logger.error(f"{self.name} error: {str(e)}")
            raise
    
    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return results.
        
        This method must be implemented by all agent subclasses.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Processing results dictionary
        """
        pass
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"

# Made with Bob