import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import autogen
from config import OPENAI_CONFIG, AGENT_CONFIG, SYSTEM_MESSAGES
from schemas import (
    StudentWork, MarkingOutput, MarkingResult, Feedback,
    ValidationResult, FinalOutput, Subject
)
from mark_schemes import MARK_SCHEMES

class MarkingAgentWorkflow:
    def __init__(self):
        self.llm_config = {
            "timeout": AGENT_CONFIG["timeout"],
            "temperature": OPENAI_CONFIG["temperature"],
            "config_list": [{
                "model": OPENAI_CONFIG["model"],
                "api_key": OPENAI_CONFIG["api_key"]
            }]
        }

        # Initialize agents
        self.orchestrator = self._create_orchestrator()
        self.marking_agent = self._create_marking_agent()
        self.feedback_agent = self._create_feedback_agent()
        self.validation_agent = self._create_validation_agent()

    def _create_orchestrator(self) -> autogen.AssistantAgent:
        """Create the orchestrator agent"""
        return autogen.AssistantAgent(
            name="orchestrator",
            system_message=SYSTEM_MESSAGES["orchestrator"],
            llm_config=self.llm_config,
        )

    def _create_marking_agent(self) -> autogen.AssistantAgent:
        """Create the marking agent with subject-specific knowledge"""
        marking_system_message = f"""{SYSTEM_MESSAGES["marking"]}

Available mark schemes: {json.dumps(MARK_SCHEMES, indent=2)}

Use these mark schemes to grade student work according to subject-specific criteria."""

        return autogen.AssistantAgent(
            name="marking_agent",
            system_message=marking_system_message,
            llm_config=self.llm_config,
        )

    def _create_feedback_agent(self) -> autogen.AssistantAgent:
        """Create the feedback agent"""
        return autogen.AssistantAgent(
            name="feedback_agent",
            system_message=SYSTEM_MESSAGES["feedback"],
            llm_config=self.llm_config,
        )

    def _create_validation_agent(self) -> autogen.AssistantAgent:
        """Create the validation agent"""
        validation_system_message = f"""{SYSTEM_MESSAGES["validation"]}

Mark schemes for validation: {json.dumps(MARK_SCHEMES, indent=2)}

Use these mark schemes to validate consistency and accuracy of marking decisions."""

        return autogen.AssistantAgent(
            name="validation_agent",
            system_message=validation_system_message,
            llm_config=self.llm_config,
        )

    async def process_student_work(self, student_work: StudentWork) -> FinalOutput:
        """
        Main workflow to process student work through all agents
        """
        try:
            # Step 1: Orchestrator coordinates the workflow
            orchestrator_input = {
                "questions": [q.model_dump() for q in student_work.questions],
                "answers": [a.model_dump() for a in student_work.answers],
                "subject": student_work.subject.value,
                "student_id": student_work.student_id
            }

            # Step 2: Marking Agent processes the work
            marking_result = await self._get_marking_result(orchestrator_input)

            # Step 3: Feedback Agent generates feedback
            feedback_result = await self._get_feedback_result(marking_result)

            # Step 4: Validation Agent validates the results
            validation_result = await self._get_validation_result(
                marking_result, feedback_result, student_work.subject
            )

            # Combine all results
            final_output = FinalOutput(
                marking_output=marking_result,
                feedback=feedback_result,
                validation=validation_result,
                processed_timestamp=datetime.now().isoformat()
            )

            return final_output

        except Exception as e:
            raise Exception(f"Error processing student work: {str(e)}")

    async def _get_marking_result(self, work_data: Dict[str, Any]) -> MarkingOutput:
        """Get marking results from the marking agent"""

        marking_prompt = f"""
        Please mark the following student work according to the appropriate mark scheme.

        Work to mark: {json.dumps(work_data, indent=2)}

        For each question-answer pair, provide:
        1. Marks awarded (integer)
        2. Confidence level (0.0 to 1.0)
        3. Detailed reasoning for the mark

        Return your response as a JSON object matching this structure:
        {{
            "student_id": "{work_data.get('student_id', '')}",
            "subject": "{work_data['subject']}",
            "results": [
                {{
                    "question_id": "string",
                    "question_text": "string",
                    "student_response": "string",
                    "max_marks": int,
                    "marks_awarded": int,
                    "confidence": float,
                    "reasoning": "string"
                }}
            ],
            "total_marks_awarded": int,
            "total_max_marks": int,
            "percentage": float
        }}
        """

        # Create a temporary user proxy for interaction
        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            code_execution_config=False,
            human_input_mode="NEVER"
        )

        # Get response from marking agent
        user_proxy.initiate_chat(
            self.marking_agent,
            message=marking_prompt,
            max_turns=1
        )

        # Extract the JSON response from the last message
        last_message = user_proxy.last_message()
        response_text = last_message["content"]

        # Parse JSON response
        try:
            marking_data = json.loads(self._extract_json_from_response(response_text))
            return MarkingOutput(**marking_data)
        except (json.JSONDecodeError, KeyError) as e:
            raise Exception(f"Failed to parse marking agent response: {str(e)}")

    async def _get_feedback_result(self, marking_output: MarkingOutput) -> Feedback:
        """Get feedback from the feedback agent"""

        feedback_prompt = f"""
        Please generate educational feedback based on these marking results:

        Marking Results: {marking_output.model_dump_json(indent=2)}

        Provide:
        1. Teacher feedback - analytical summary for educator use
        2. Student feedback - constructive, encouraging message for the student
        3. Strengths - specific areas where student performed well
        4. Areas for improvement - specific areas needing development
        5. Next steps - actionable recommendations for learning

        Return your response as a JSON object:
        {{
            "teacher_feedback": "string",
            "student_feedback": "string",
            "strengths": ["string"],
            "areas_for_improvement": ["string"],
            "next_steps": ["string"]
        }}
        """

        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            code_execution_config=False,
            human_input_mode="NEVER"
        )

        user_proxy.initiate_chat(
            self.feedback_agent,
            message=feedback_prompt,
            max_turns=1
        )

        last_message = user_proxy.last_message()
        response_text = last_message["content"]

        try:
            feedback_data = json.loads(self._extract_json_from_response(response_text))
            return Feedback(**feedback_data)
        except (json.JSONDecodeError, KeyError) as e:
            raise Exception(f"Failed to parse feedback agent response: {str(e)}")

    async def _get_validation_result(
        self,
        marking_output: MarkingOutput,
        feedback: Feedback,
        subject: Subject
    ) -> ValidationResult:
        """Get validation results from the validation agent"""

        validation_prompt = f"""
        Please validate the consistency and accuracy of these marking and feedback results:

        Subject: {subject.value}
        Marking Results: {marking_output.model_dump_json(indent=2)}
        Feedback: {feedback.model_dump_json(indent=2)}

        Check for:
        1. Consistency with mark scheme criteria
        2. Fairness and objectivity in marking
        3. Quality and appropriateness of feedback
        4. Alignment between marks and feedback comments

        Return your validation as a JSON object:
        {{
            "is_valid": boolean,
            "consistency_score": float,
            "validation_notes": ["string"],
            "suggested_corrections": {{}} or null
        }}
        """

        user_proxy = autogen.UserProxyAgent(
            name="user_proxy",
            code_execution_config=False,
            human_input_mode="NEVER"
        )

        user_proxy.initiate_chat(
            self.validation_agent,
            message=validation_prompt,
            max_turns=1
        )

        last_message = user_proxy.last_message()
        response_text = last_message["content"]

        try:
            validation_data = json.loads(self._extract_json_from_response(response_text))
            return ValidationResult(**validation_data)
        except (json.JSONDecodeError, KeyError) as e:
            raise Exception(f"Failed to parse validation agent response: {str(e)}")

    def _extract_json_from_response(self, response: str) -> str:
        """Extract JSON content from agent response"""
        # Find JSON content between ```json and ``` or just find JSON object
        import re

        # Try to find JSON in code block
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            return json_match.group(1).strip()

        # Try to find JSON object directly
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            return json_match.group(0).strip()

        # If no JSON found, return the response as-is and let JSON parsing handle the error
        return response.strip()