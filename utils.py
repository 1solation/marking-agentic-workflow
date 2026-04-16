import json
import asyncio
from typing import Dict, Any, List
from main import MarkingWorkflowApp
from schemas import Subject

class MarkingTestRunner:
    """Test runner for the marking workflow"""

    def __init__(self):
        self.app = MarkingWorkflowApp()

    async def run_test_suite(self, sample_data_file: str = "examples/sample_data.json") -> Dict[str, Any]:
        """Run tests on sample data"""
        results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "test_results": []
        }

        try:
            with open(sample_data_file, 'r') as f:
                test_data = json.load(f)

            for subject, data in test_data.items():
                print(f"🧪 Testing {subject} marking...")
                results["total_tests"] += 1

                try:
                    result = await self.app.process_marking_request(data)

                    if "error" in result:
                        print(f"❌ {subject} test failed: {result['error']}")
                        results["failed"] += 1
                        results["test_results"].append({
                            "subject": subject,
                            "status": "failed",
                            "error": result["error"]
                        })
                    else:
                        print(f"✅ {subject} test passed")
                        results["passed"] += 1
                        results["test_results"].append({
                            "subject": subject,
                            "status": "passed",
                            "total_marks": result["marking_output"]["total_marks_awarded"],
                            "max_marks": result["marking_output"]["total_max_marks"],
                            "percentage": result["marking_output"]["percentage"],
                            "validation_score": result["validation"]["consistency_score"]
                        })

                except Exception as e:
                    print(f"❌ {subject} test failed with exception: {str(e)}")
                    results["failed"] += 1
                    results["test_results"].append({
                        "subject": subject,
                        "status": "failed",
                        "error": str(e)
                    })

        except FileNotFoundError:
            print(f"❌ Sample data file not found: {sample_data_file}")
            return {"error": f"File not found: {sample_data_file}"}

        return results

    async def test_individual_subject(self, subject: str) -> Dict[str, Any]:
        """Test marking for a specific subject"""
        sample_data_file = "examples/sample_data.json"

        try:
            with open(sample_data_file, 'r') as f:
                test_data = json.load(f)

            if subject not in test_data:
                return {"error": f"Subject '{subject}' not found in test data"}

            print(f"🧪 Testing {subject} marking workflow...")
            data = test_data[subject]

            result = await self.app.process_marking_request(data)

            if "error" in result:
                return {"status": "failed", "error": result["error"]}

            # Print detailed results
            self._print_detailed_results(result, subject)

            return {"status": "passed", "result": result}

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def _print_detailed_results(self, result: Dict[str, Any], subject: str):
        """Print detailed test results"""
        print(f"\n📊 {subject.upper()} MARKING RESULTS")
        print("=" * 50)

        marking = result["marking_output"]
        print(f"Student: {marking['student_id']}")
        print(f"Subject: {marking['subject']}")
        print(f"Total Score: {marking['total_marks_awarded']}/{marking['total_max_marks']} ({marking['percentage']:.1f}%)")

        print(f"\n📝 Question Details:")
        for i, question_result in enumerate(marking["results"], 1):
            print(f"\nQuestion {i} ({question_result['question_id']}):")
            print(f"  Question: {question_result['question_text'][:80]}...")
            print(f"  Student Answer: {question_result['student_response'][:100]}...")
            print(f"  Marks: {question_result['marks_awarded']}/{question_result['max_marks']}")
            print(f"  Confidence: {question_result['confidence']:.2f}")
            print(f"  Reasoning: {question_result['reasoning'][:120]}...")

        feedback = result["feedback"]
        print(f"\n💬 Feedback Summary:")
        print(f"  Strengths: {len(feedback['strengths'])} identified")
        print(f"  Areas for Improvement: {len(feedback['areas_for_improvement'])} identified")
        print(f"  Next Steps: {len(feedback['next_steps'])} suggested")

        validation = result["validation"]
        print(f"\n✔️ Validation:")
        print(f"  Valid: {validation['is_valid']}")
        print(f"  Consistency Score: {validation['consistency_score']:.2f}")
        print(f"  Notes: {len(validation['validation_notes'])} validation points")

def validate_schema():
    """Validate the data schemas"""
    print("🔍 Validating schemas...")

    try:
        # Test Subject enum
        subjects = ["mathematics", "english", "science", "history"]
        for subject in subjects:
            Subject(subject)
        print("✅ Subject validation passed")

        # Test with sample data structure
        sample = {
            "questions": [{"question_id": "test", "question_text": "Test question", "max_marks": 5, "question_type": "essay"}],
            "answers": [{"question_id": "test", "student_response": "Test answer"}],
            "subject": "mathematics",
            "student_id": "test_student"
        }

        app = MarkingWorkflowApp()
        student_work = app._parse_input(sample)
        print("✅ Input parsing validation passed")

        return True

    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

async def main():
    """Main test runner"""
    print("🚀 Microsoft Agent Framework - Marking Workflow Testing")
    print("=" * 60)

    # Validate schemas first
    if not validate_schema():
        return

    runner = MarkingTestRunner()

    # Run full test suite
    print("\n🧪 Running full test suite...")
    results = await runner.run_test_suite()

    if "error" not in results:
        print(f"\n📊 Test Summary:")
        print(f"Total Tests: {results['total_tests']}")
        print(f"Passed: {results['passed']}")
        print(f"Failed: {results['failed']}")
        print(f"Success Rate: {(results['passed']/results['total_tests']*100):.1f}%")

        # Save test results
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Test results saved to test_results.json")
    else:
        print(f"❌ Test suite failed: {results['error']}")

if __name__ == "__main__":
    asyncio.run(main())