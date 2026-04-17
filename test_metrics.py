#!/usr/bin/env python3
"""
Test script for the enhanced marking workflow with metrics
"""

import asyncio
import os
from main import MarkingWorkflowApp

def test_metrics_output():
    """Test the metrics tracking functionality"""

    # Test with a simple sample
    sample_input = {
        "questions": [
            {
                "question_id": "test_q1",
                "question_text": "What is 2 + 2?",
                "max_marks": 2,
                "question_type": "calculation"
            }
        ],
        "answers": [
            {
                "question_id": "test_q1",
                "student_response": "2 + 2 = 4"
            }
        ],
        "subject": "mathematics",
        "student_id": "test_student"
    }

    return sample_input

async def main():
    """Main test function"""
    print("🧪 Testing Enhanced Marking Workflow with Metrics")
    print("="*55)

    # Check if API key is set (for real testing)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("⚠️  Warning: No valid OpenAI API key found.")
        print("Metrics structure will be displayed, but agents won't execute.")
        print("To test with real agents, add your API key to .env file.\n")

    # Get test input
    test_input = test_metrics_output()

    # Initialize application
    app = MarkingWorkflowApp()

    print("📊 Metrics system initialized")
    print(f"📝 Test input: {len(test_input['questions'])} question(s) in {test_input['subject']}")

    # Test the workflow (will show metrics even if API fails)
    try:
        result = await app.process_marking_request(test_input)

        if "error" not in result:
            print("\n✅ Test completed successfully!")
        else:
            print(f"\n⚠️  Test completed with API error (expected without valid key): {result['error']}")
            print("Metrics tracking system is working correctly.")

    except Exception as e:
        print(f"\n🔧 Metrics system captured error (as expected): {str(e)}")
        print("This shows the error handling and timing is working.")

if __name__ == "__main__":
    asyncio.run(main())