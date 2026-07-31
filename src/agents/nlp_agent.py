"""
NLP Agent for parsing natural language appointment requests.

This agent uses LangChain and OpenAI to understand user requests and extract
structured appointment information from natural language.
"""
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import json

from src.agents.base import BaseAgent
from src.utils.logger import get_logger

logger = get_logger(__name__)


class NLPAgent(BaseAgent):
    """
    Natural Language Processing agent for appointment booking.
    
    This agent can:
    - Parse natural language appointment requests
    - Extract date, time, duration, and participants
    - Understand relative dates ("tomorrow", "next week")
    - Handle ambiguous requests with clarification
    """
    
    def __init__(self):
        """Initialize the NLP agent."""
        system_prompt = """You are an expert appointment scheduling assistant with natural language understanding capabilities.

Your role is to parse user requests for appointments and extract structured information.

Extract the following information from user requests:
1. Title/Purpose of the meeting
2. Date (convert relative dates like "tomorrow", "next Monday" to actual dates)
3. Start time
4. Duration or end time
5. Participants (email addresses or names)
6. Location (physical or virtual)
7. Any special requirements or notes

Current date and time context will be provided.

Always respond in valid JSON format with these fields:
{
    "title": "string",
    "date": "YYYY-MM-DD",
    "start_time": "HH:MM",
    "duration_minutes": integer,
    "participants": ["email1", "email2"],
    "location": "string or null",
    "notes": "string or null",
    "confidence": float (0-1),
    "ambiguities": ["list of unclear items"],
    "clarification_needed": boolean
}

If information is missing or ambiguous, set clarification_needed to true and list the ambiguities.

Examples:
- "Schedule a meeting with john@example.com tomorrow at 2pm for 1 hour"
- "Book a team standup next Monday 9am, 30 minutes"
- "Set up a call with the design team on Friday afternoon"
"""
        
        super().__init__(
            name="NLP Agent",
            system_prompt=system_prompt,
            temperature=0.3  # Lower temperature for more consistent parsing
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a natural language appointment request.
        
        Args:
            input_data: Dictionary containing:
                - request: Natural language appointment request
                - user_timezone: User's timezone (optional)
                - current_time: Current datetime (optional)
                
        Returns:
            Dictionary with parsed appointment information
        """
        request = input_data.get("request", "")
        user_timezone = input_data.get("user_timezone", "UTC")
        current_time = input_data.get("current_time", datetime.now())
        
        if not request:
            return {
                "success": False,
                "error": "No request provided"
            }
        
        logger.info(f"Processing NLP request: {request}")
        
        try:
            # Build context with current date/time
            context = {
                "current_date": current_time.strftime("%Y-%m-%d"),
                "current_time": current_time.strftime("%H:%M"),
                "current_day": current_time.strftime("%A"),
                "timezone": user_timezone
            }
            
            # Invoke the LLM
            response = self.invoke(request, context)
            
            # Parse JSON response
            try:
                parsed_data = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from response if it's wrapped in text
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    parsed_data = json.loads(json_match.group())
                else:
                    raise ValueError("Could not parse JSON from response")
            
            # Validate required fields
            required_fields = (
                "microsoft_client_id",
                "microsoft_client_secret",
                "microsoft_tenant_id",
                "microsoft_redirect_uri",
            )
            missing_fields = [f for f in required_fields if f not in parsed_data]
            
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {missing_fields}",
                    "raw_response": response
                }
            
            if not self.settings.microsoft_tenant_id:
                missing["microsoft_tenant_id"] = "Set MICROSOFT_TENANT_ID"
            
            # Add metadata
            parsed_data["success"] = True
            parsed_data["original_request"] = request
            parsed_data["processed_at"] = current_time.isoformat()
            
            logger.info(f"Successfully parsed appointment request with confidence: {parsed_data.get('confidence')}")
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error processing NLP request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "original_request": request
            }
    
    def clarify_request(
        self,
        original_request: str,
        ambiguities: list,
        user_response: str
    ) -> Dict[str, Any]:
        """
        Process clarification from user for ambiguous requests.
        
        Args:
            original_request: Original appointment request
            ambiguities: List of ambiguous items
            user_response: User's clarification response
            
        Returns:
            Updated parsed appointment information
        """
        clarification_prompt = f"""
Original request: {original_request}

Ambiguities identified: {', '.join(ambiguities)}

User's clarification: {user_response}

Please provide the complete appointment information incorporating the clarification.
"""
        
        return self.process({
            "request": clarification_prompt,
            "current_time": datetime.now()
        })
    
    def suggest_alternatives(
        self,
        parsed_request: Dict[str, Any],
        conflicts: list
    ) -> Dict[str, Any]:
        """
        Suggest alternative times when conflicts are detected.
        
        Args:
            parsed_request: Parsed appointment request
            conflicts: List of conflicting appointments
            
        Returns:
            Suggestions for alternative times
        """
        conflict_info = "\n".join([
            f"- {c.get('title')} at {c.get('start_time')} to {c.get('end_time')}"
            for c in conflicts
        ])
        
        suggestion_prompt = f"""
The requested appointment has conflicts:
{conflict_info}

Original request: {parsed_request.get('original_request')}
Requested time: {parsed_request.get('date')} at {parsed_request.get('start_time')}
Duration: {parsed_request.get('duration_minutes')} minutes

Suggest 3 alternative time slots that would work, considering:
1. Same day if possible
2. Similar time of day
3. Avoiding the conflicting appointments

Respond in JSON format:
{{
    "alternatives": [
        {{"date": "YYYY-MM-DD", "start_time": "HH:MM", "reason": "why this works"}},
        ...
    ]
}}
"""
        
        try:
            response = self.invoke(suggestion_prompt)
            suggestions = json.loads(response)
            suggestions["success"] = True
            return suggestions
        except Exception as e:
            logger.error(f"Error generating alternatives: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Made with Bob