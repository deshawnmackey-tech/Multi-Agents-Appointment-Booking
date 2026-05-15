"""
Demo script for NLP Agent.

This script demonstrates how to use the NLP Agent to parse
natural language appointment requests.

Usage:
    python examples/nlp_agent_demo.py
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from src.agents.nlp_agent import NLPAgent


def demo_simple_request():
    """Demo: Parse a simple appointment request."""
    print("\n" + "="*60)
    print("DEMO 1: Simple Appointment Request")
    print("="*60)
    
    agent = NLPAgent()
    
    request = "Schedule a meeting with john@example.com tomorrow at 2pm for 1 hour"
    print(f"\nRequest: {request}")
    
    result = agent.process({
        "request": request,
        "user_timezone": "America/New_York",
        "current_time": datetime(2024, 1, 15, 10, 0)
    })
    
    print("\nParsed Result:")
    print(f"  Success: {result.get('success')}")
    if result.get('success'):
        print(f"  Title: {result.get('title')}")
        print(f"  Date: {result.get('date')}")
        print(f"  Start Time: {result.get('start_time')}")
        print(f"  Duration: {result.get('duration_minutes')} minutes")
        print(f"  Participants: {result.get('participants')}")
        print(f"  Confidence: {result.get('confidence')}")
        if result.get('clarification_needed'):
            print(f"  Ambiguities: {result.get('ambiguities')}")
    else:
        print(f"  Error: {result.get('error')}")


def demo_complex_request():
    """Demo: Parse a complex appointment request."""
    print("\n" + "="*60)
    print("DEMO 2: Complex Appointment Request")
    print("="*60)
    
    agent = NLPAgent()
    
    request = "Set up a team standup next Monday at 9am for 30 minutes with the engineering team in the main conference room"
    print(f"\nRequest: {request}")
    
    result = agent.process({
        "request": request,
        "user_timezone": "UTC",
        "current_time": datetime(2024, 1, 15, 10, 0)
    })
    
    print("\nParsed Result:")
    print(f"  Success: {result.get('success')}")
    if result.get('success'):
        print(f"  Title: {result.get('title')}")
        print(f"  Date: {result.get('date')}")
        print(f"  Start Time: {result.get('start_time')}")
        print(f"  Duration: {result.get('duration_minutes')} minutes")
        print(f"  Location: {result.get('location')}")
        print(f"  Confidence: {result.get('confidence')}")


def demo_ambiguous_request():
    """Demo: Handle ambiguous request."""
    print("\n" + "="*60)
    print("DEMO 3: Ambiguous Request")
    print("="*60)
    
    agent = NLPAgent()
    
    request = "Schedule a meeting tomorrow"
    print(f"\nRequest: {request}")
    
    result = agent.process({
        "request": request,
        "current_time": datetime(2024, 1, 15, 10, 0)
    })
    
    print("\nParsed Result:")
    print(f"  Success: {result.get('success')}")
    print(f"  Clarification Needed: {result.get('clarification_needed')}")
    if result.get('ambiguities'):
        print(f"  Ambiguities: {result.get('ambiguities')}")
    
    if result.get('clarification_needed'):
        print("\n  Simulating clarification...")
        clarified = agent.clarify_request(
            original_request=request,
            ambiguities=result.get('ambiguities', []),
            user_response="Make it at 2pm with john@example.com for 1 hour"
        )
        print(f"\n  After Clarification:")
        print(f"    Success: {clarified.get('success')}")
        if clarified.get('success'):
            print(f"    Title: {clarified.get('title')}")
            print(f"    Date: {clarified.get('date')}")
            print(f"    Start Time: {clarified.get('start_time')}")
            print(f"    Participants: {clarified.get('participants')}")


def demo_conflict_alternatives():
    """Demo: Suggest alternatives for conflicts."""
    print("\n" + "="*60)
    print("DEMO 4: Conflict Resolution")
    print("="*60)
    
    agent = NLPAgent()
    
    parsed_request = {
        "original_request": "Meeting tomorrow at 2pm",
        "title": "Team Meeting",
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
    
    print(f"\nOriginal Request: {parsed_request['original_request']}")
    print(f"Requested Time: {parsed_request['date']} at {parsed_request['start_time']}")
    print(f"\nConflict Detected:")
    print(f"  {conflicts[0]['title']} from {conflicts[0]['start_time']} to {conflicts[0]['end_time']}")
    
    print("\n  Generating alternatives...")
    suggestions = agent.suggest_alternatives(parsed_request, conflicts)
    
    if suggestions.get('success') and suggestions.get('alternatives'):
        print("\n  Suggested Alternatives:")
        for i, alt in enumerate(suggestions['alternatives'], 1):
            print(f"    {i}. {alt.get('date')} at {alt.get('start_time')}")
            print(f"       Reason: {alt.get('reason')}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("NLP AGENT DEMONSTRATION")
    print("="*60)
    print("\nThis demo shows how the NLP Agent can parse natural language")
    print("appointment requests and extract structured information.")
    
    try:
        demo_simple_request()
        demo_complex_request()
        demo_ambiguous_request()
        demo_conflict_alternatives()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        print("\nThe NLP Agent successfully:")
        print("  ✓ Parsed simple requests")
        print("  ✓ Handled complex requests")
        print("  ✓ Identified ambiguities")
        print("  ✓ Suggested alternatives for conflicts")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error running demo: {str(e)}")
        print("\nNote: Make sure you have:")
        print("  1. Set OPENAI_API_KEY in your .env file")
        print("  2. Installed all requirements: pip install -r requirements.txt")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

# Made with Bob