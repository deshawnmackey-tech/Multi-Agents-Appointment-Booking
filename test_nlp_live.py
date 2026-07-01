"""
Live test of NLP Agent with real OpenAI API calls.
"""
import os

import pytest
from datetime import datetime
from src.agents.nlp_agent import NLPAgent


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_NLP_TESTS", "0") != "1",
    reason="Set RUN_LIVE_NLP_TESTS=1 and a valid OPENAI_API_KEY to run live NLP tests",
)


def test_simple_request():
    """Test a simple appointment request."""
    print("\n" + "="*70)
    print("TEST 1: Simple Appointment Request")
    print("="*70)
    
    agent = NLPAgent()
    
    request = "Schedule a meeting with john@example.com tomorrow at 2pm for 1 hour"
    print(f"\n📝 Request: {request}")
    print("\n⏳ Processing with GPT-4...")
    
    result = agent.process({
        "request": request,
        "user_timezone": "America/New_York",
        "current_time": datetime(2024, 1, 15, 10, 0)  # Monday, Jan 15, 2024, 10:00 AM
    })
    
    print("\n✅ Result:")
    print(f"  Success: {result.get('success')}")
    
    if result.get('success'):
        print(f"\n  📅 Parsed Information:")
        print(f"    Title: {result.get('title')}")
        print(f"    Date: {result.get('date')}")
        print(f"    Start Time: {result.get('start_time')}")
        print(f"    Duration: {result.get('duration_minutes')} minutes")
        print(f"    Participants: {result.get('participants')}")
        print(f"    Location: {result.get('location')}")
        print(f"    Confidence: {result.get('confidence')}")
        
        if result.get('clarification_needed'):
            print(f"\n  ⚠️  Clarification Needed:")
            print(f"    Ambiguities: {result.get('ambiguities')}")
    else:
        print(f"\n  ❌ Error: {result.get('error')}")
    
    assert isinstance(result, dict)


def test_complex_request():
    """Test a more complex request."""
    print("\n" + "="*70)
    print("TEST 2: Complex Request with Multiple Details")
    print("="*70)
    
    agent = NLPAgent()
    
    request = "Set up a team standup next Monday at 9am for 30 minutes with the engineering team in the main conference room"
    print(f"\n📝 Request: {request}")
    print("\n⏳ Processing with GPT-4...")
    
    result = agent.process({
        "request": request,
        "user_timezone": "UTC",
        "current_time": datetime(2024, 1, 15, 10, 0)
    })
    
    print("\n✅ Result:")
    print(f"  Success: {result.get('success')}")
    
    if result.get('success'):
        print(f"\n  📅 Parsed Information:")
        print(f"    Title: {result.get('title')}")
        print(f"    Date: {result.get('date')}")
        print(f"    Start Time: {result.get('start_time')}")
        print(f"    Duration: {result.get('duration_minutes')} minutes")
        print(f"    Location: {result.get('location')}")
        print(f"    Notes: {result.get('notes')}")
        print(f"    Confidence: {result.get('confidence')}")
    else:
        print(f"\n  ❌ Error: {result.get('error')}")
    
    assert isinstance(result, dict)


def test_ambiguous_request():
    """Test handling of ambiguous request."""
    print("\n" + "="*70)
    print("TEST 3: Ambiguous Request")
    print("="*70)
    
    agent = NLPAgent()
    
    request = "Schedule a meeting tomorrow"
    print(f"\n📝 Request: {request}")
    print("\n⏳ Processing with GPT-4...")
    
    result = agent.process({
        "request": request,
        "current_time": datetime(2024, 1, 15, 10, 0)
    })
    
    print("\n✅ Result:")
    print(f"  Success: {result.get('success')}")
    print(f"  Clarification Needed: {result.get('clarification_needed')}")
    
    if result.get('ambiguities'):
        print(f"\n  ⚠️  Ambiguities Detected:")
        for amb in result.get('ambiguities', []):
            print(f"    - {amb}")
    
    assert isinstance(result, dict)


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🤖 NLP AGENT LIVE TEST")
    print("="*70)
    print("\nTesting the NLP Agent with real OpenAI API calls...")
    print("This will use your OPENAI_API_KEY from .env")
    
    try:
        # Test 1: Simple request
        result1 = test_simple_request()
        
        # Test 2: Complex request
        result2 = test_complex_request()
        
        # Test 3: Ambiguous request
        result3 = test_ambiguous_request()
        
        # Summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        
        tests_passed = sum([
            result1.get('success', False),
            result2.get('success', False),
            result3.get('success', False)
        ])
        
        print(f"\n  Tests Passed: {tests_passed}/3")
        print(f"\n  ✅ Test 1 (Simple): {'PASS' if result1.get('success') else 'FAIL'}")
        print(f"  ✅ Test 2 (Complex): {'PASS' if result2.get('success') else 'FAIL'}")
        print(f"  ✅ Test 3 (Ambiguous): {'PASS' if result3.get('success') else 'FAIL'}")
        
        print("\n" + "="*70)
        print("🎉 TESTING COMPLETE!")
        print("="*70)
        
        if tests_passed == 3:
            print("\n✨ All tests passed! The NLP Agent is working perfectly!")
        else:
            print(f"\n⚠️  {3 - tests_passed} test(s) failed. Check the errors above.")
        
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error running tests: {str(e)}")
        print("\n💡 Make sure you have:")
        print("  1. Set OPENAI_API_KEY in your .env file")
        print("  2. Installed all requirements: pip install -r requirements.txt")
        print("  3. Valid OpenAI API key with credits")
        print("\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

# Made with Bob
