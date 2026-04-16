#!/usr/bin/env python3
"""
Microsoft Agent Framework - Marking Workflow Runner
Command-line interface for the marking system
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from main import MarkingWorkflowApp
from utils import MarkingTestRunner, validate_schema

def load_custom_data(file_path: str):
    """Load custom data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {file_path}: {e}")
        return None

async def run_marking(data_source: str):
    """Run marking workflow"""
    app = MarkingWorkflowApp()

    if data_source == "sample":
        # Load sample data
        sample_file = "examples/sample_data.json"
        if not Path(sample_file).exists():
            print(f"❌ Sample data file not found: {sample_file}")
            return

        with open(sample_file, 'r') as f:
            all_samples = json.load(f)

        # Run first sample (science)
        sample_data = all_samples["science"]
        print("🚀 Running marking workflow with science sample data...")

    else:
        # Load custom data file
        custom_data = load_custom_data(data_source)
        if not custom_data:
            return
        sample_data = custom_data
        print(f"🚀 Running marking workflow with data from {data_source}...")

    # Process the data
    result = await app.process_marking_request(sample_data)

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        return

    # Display results
    print("✅ Marking completed successfully!\n")

    marking = result["marking_output"]
    print(f"📊 RESULTS SUMMARY")
    print(f"Student: {marking['student_id']}")
    print(f"Subject: {marking['subject']}")
    print(f"Score: {marking['total_marks_awarded']}/{marking['total_max_marks']} ({marking['percentage']:.1f}%)")

    print(f"\n📝 QUESTION BREAKDOWN:")
    for i, q in enumerate(marking["results"], 1):
        print(f"  Q{i}: {q['marks_awarded']}/{q['max_marks']} (confidence: {q['confidence']:.2f})")

    print(f"\n💡 FEEDBACK PREVIEW:")
    feedback = result["feedback"]
    print(f"  Strengths: {len(feedback['strengths'])} identified")
    print(f"  Areas to improve: {len(feedback['areas_for_improvement'])} identified")
    print(f"  Next steps: {len(feedback['next_steps'])} suggested")

    print(f"\n✅ VALIDATION:")
    validation = result["validation"]
    print(f"  Status: {'PASSED' if validation['is_valid'] else 'NEEDS REVIEW'}")
    print(f"  Consistency: {validation['consistency_score']:.2f}")

    # Save results
    output_file = "marking_results.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Full results saved to {output_file}")

async def run_tests(specific_subject: str = None):
    """Run test suite"""
    print("🧪 Running Marking Workflow Tests")
    print("=" * 40)

    runner = MarkingTestRunner()

    if specific_subject:
        print(f"Testing specific subject: {specific_subject}")
        result = await runner.test_individual_subject(specific_subject)
        if result["status"] == "failed":
            print(f"❌ Test failed: {result['error']}")
        else:
            print("✅ Test completed successfully")
    else:
        print("Running full test suite...")
        results = await runner.run_test_suite()

        if "error" in results:
            print(f"❌ Test suite failed: {results['error']}")
        else:
            print(f"\n📊 TEST SUMMARY:")
            print(f"Total: {results['total_tests']}")
            print(f"Passed: {results['passed']}")
            print(f"Failed: {results['failed']}")
            print(f"Success Rate: {(results['passed']/results['total_tests']*100):.1f}%")

def interactive_mode():
    """Run interactive mode for custom input"""
    print("🎯 Interactive Marking Mode")
    print("Enter your JSON data (or press Enter for example):")
    print("Format: {\"questions\": [...], \"answers\": [...], \"subject\": \"...\", \"student_id\": \"...\"}")

    user_input = input().strip()

    if not user_input:
        print("Using sample data...")
        asyncio.run(run_marking("sample"))
    else:
        try:
            # Save input to temporary file
            temp_file = "temp_input.json"
            with open(temp_file, 'w') as f:
                json.dump(json.loads(user_input), f, indent=2)

            asyncio.run(run_marking(temp_file))

            # Clean up
            Path(temp_file).unlink()

        except json.JSONDecodeError:
            print("❌ Invalid JSON format")
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Microsoft Agent Framework - Academic Marking Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py mark                    # Run with sample data
  python run.py mark custom.json        # Run with custom data file
  python run.py test                    # Run all tests
  python run.py test mathematics        # Test specific subject
  python run.py interactive             # Interactive input mode
  python run.py validate                # Validate schemas only
        """
    )

    parser.add_argument(
        'action',
        choices=['mark', 'test', 'interactive', 'validate'],
        help='Action to perform'
    )

    parser.add_argument(
        'input',
        nargs='?',
        help='Input file for marking or subject name for testing'
    )

    args = parser.parse_args()

    # Validate schemas first (always)
    if not validate_schema():
        print("❌ Schema validation failed")
        sys.exit(1)

    if args.action == 'mark':
        data_source = args.input or "sample"
        asyncio.run(run_marking(data_source))

    elif args.action == 'test':
        specific_subject = args.input
        asyncio.run(run_tests(specific_subject))

    elif args.action == 'interactive':
        interactive_mode()

    elif args.action == 'validate':
        print("✅ All schemas validated successfully")

if __name__ == "__main__":
    main()