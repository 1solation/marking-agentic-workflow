#!/usr/bin/env python3
"""
Microsoft Agent Framework - Academic Marking Workflow
Main application entry point for the multi-agent marking system
"""

import asyncio
import json
import sys
from typing import Dict, Any
from agents import MarkingAgentWorkflow
from schemas import StudentWork, Question, Answer, Subject

class MarkingWorkflowApp:
    def __init__(self):
        self.workflow = MarkingAgentWorkflow()

    async def process_marking_request(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a marking request through the complete agent workflow

        Args:
            input_data: Dictionary containing:
                - questions: List of question dictionaries
                - answers: List of answer dictionaries
                - subject: Subject string
                - student_id: Optional student identifier

        Returns:
            Dictionary with complete marking results, feedback, and validation
        """
        try:
            # Validate and parse input
            student_work = self._parse_input(input_data)

            # Process through agent workflow
            result = await self.workflow.process_student_work(student_work)

            return result.model_dump()

        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }

    def _parse_input(self, input_data: Dict[str, Any]) -> StudentWork:
        """Parse and validate input data"""
        try:
            # Parse questions
            questions = []
            for q_data in input_data["questions"]:
                questions.append(Question(
                    question_id=q_data["question_id"],
                    question_text=q_data["question_text"],
                    max_marks=q_data["max_marks"],
                    question_type=q_data.get("question_type", "essay")
                ))

            # Parse answers
            answers = []
            for a_data in input_data["answers"]:
                answers.append(Answer(
                    question_id=a_data["question_id"],
                    student_response=a_data["student_response"]
                ))

            # Parse subject
            subject = Subject(input_data["subject"])

            return StudentWork(
                questions=questions,
                answers=answers,
                subject=subject,
                student_id=input_data.get("student_id")
            )

        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid input data: {e}")

async def main():
    """Main application entry point with example usage"""

    # Example input data
    sample_input = {
        "questions": [
            {
                "question_id": "q1",
                "question_text": "Explain the concept of photosynthesis and its importance in the ecosystem.",
                "max_marks": 10,
                "question_type": "essay"
            },
            {
                "question_id": "q2",
                "question_text": "Calculate the area of a circle with radius 5 units.",
                "max_marks": 5,
                "question_type": "calculation"
            }
        ],
        "answers": [
            {
                "question_id": "q1",
                "student_response": "Photosynthesis is a process where plants use sunlight to make food. It involves chlorophyll in leaves capturing light energy and converting carbon dioxide and water into glucose and oxygen. This is important because it produces oxygen for animals to breathe and forms the base of most food chains."
            },
            {
                "question_id": "q2",
                "student_response": "Area = π × r² = 3.14 × 5² = 3.14 × 25 = 78.5 square units"
            }
        ],
        "subject": "science",
        "student_id": "student_001"
    }

    print("🤖 Starting Microsoft Agent Framework Marking Workflow...")
    print(f"📝 Processing {len(sample_input['questions'])} questions in {sample_input['subject']}")

    # Initialize application
    app = MarkingWorkflowApp()

    # Process the marking request
    result = await app.process_marking_request(sample_input)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    print("✅ Marking workflow completed successfully!")
    print("\n📊 Results Summary:")
    print(f"Student ID: {result['marking_output']['student_id']}")
    print(f"Subject: {result['marking_output']['subject']}")
    print(f"Total Score: {result['marking_output']['total_marks_awarded']}/{result['marking_output']['total_max_marks']} ({result['marking_output']['percentage']:.1f}%)")

    print("\n📋 Detailed Results:")
    for i, question_result in enumerate(result['marking_output']['results'], 1):
        print(f"\nQuestion {i}:")
        print(f"  Marks: {question_result['marks_awarded']}/{question_result['max_marks']}")
        print(f"  Confidence: {question_result['confidence']:.2f}")
        print(f"  Reasoning: {question_result['reasoning'][:100]}...")

    print(f"\n💬 Student Feedback Preview:")
    print(f"  {result['feedback']['student_feedback'][:150]}...")

    print(f"\n✔️ Validation Status: {'PASSED' if result['validation']['is_valid'] else 'NEEDS REVIEW'}")
    print(f"  Consistency Score: {result['validation']['consistency_score']:.2f}")

    # Save full results to file
    with open("marking_results.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Full results saved to marking_results.json")

def run_interactive_mode():
    """Run interactive mode for custom input"""
    print("🎯 Interactive Marking Mode")
    print("Enter your marking request as JSON or press Enter for example:")

    user_input = input().strip()

    if not user_input:
        # Run with example data
        asyncio.run(main())
    else:
        try:
            input_data = json.loads(user_input)
            app = MarkingWorkflowApp()
            result = asyncio.run(app.process_marking_request(input_data))
            print(json.dumps(result, indent=2))
        except json.JSONDecodeError:
            print("❌ Invalid JSON input")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        run_interactive_mode()
    else:
        asyncio.run(main())