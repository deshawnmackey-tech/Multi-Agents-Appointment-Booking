"""
Tests for NLP Agent.
"""
import pytest
from datetime import datetime
from src.agents.nlp_agent import NLPAgent


@pytest.fixture
def nlp_agent():
    """Create NLP agent instance."""
    return NLPAgent()


def test_nlp_agent_initialization(nlp_agent):
    """Test NLP agent initializes correctly."""
    assert nlp_agent.name == "NLP Agent"
    assert nlp_agent.system_prompt is not None
    assert nlp_agent.llm is not None


def test_process_simple_request(nlp_agent):
    """Test processing a simple appointment request."""
    input_data = {
        "request": "Schedule a meeting with john@example.com tomorrow at 2pm for 1 hour",
        "user_timezone": "America/New_York",
        "current_time": datetime(2024, 1, 15, 10, 0)
    }
    
    result = nlp_agent.process(input_data)
    
    # Check basic structure
    assert "success" in result
    assert "original_request" in result
    
    # If successful, check parsed data
    if result.get("success"):
        assert "title" in result
        assert "confidence" in result
        assert isinstance(result["confidence"], (int, float))


def test_process_empty_request(nlp_agent):
    """Test processing empty request."""
    input_data = {
        "request": "",
        "current_time": datetime.now()
    }
    
    result = nlp_agent.process(input_data)
    
    assert result["success"] is False
    assert "error" in result


def test_process_complex_request(nlp_agent):
    """Test processing a complex appointment request."""
    input_data = {
        "request": "Book a team standup next Monday at 9am for 30 minutes with the engineering team",
        "user_timezone": "UTC",
        "current_time": datetime(2024, 1, 15, 10, 0)
    }
    
    result = nlp_agent.process(input_data)
    
    assert "success" in result
    assert "original_request" in result
    
    if result.get("success"):
        assert "title" in result
        assert "confidence" in result


def test_clarify_request(nlp_agent):
    """Test clarification of ambiguous request."""
    original_request = "Schedule a meeting tomorrow"
    ambiguities = ["time not specified", "participants not specified"]
    user_response = "Make it at 2pm with john@example.com"
    
    result = nlp_agent.clarify_request(
        original_request,
        ambiguities,
        user_response
    )
    
    assert "success" in result


def test_suggest_alternatives(nlp_agent):
    """Test suggesting alternative times."""
    parsed_request = {
        "original_request": "Meeting tomorrow at 2pm",
        "date": "2024-01-16",
        "start_time": "14:00",
        "duration_minutes": 60
    }
    
    conflicts = [
        {
            "title": "Existing Meeting",
            "start_time": "14:00",
            "end_time": "15:00"
        }
    ]
    
    result = nlp_agent.suggest_alternatives(parsed_request, conflicts)
    
    assert "success" in result

# Made with Bob