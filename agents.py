import json
import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import autogen
from config import OPENAI_CONFIG, AGENT_CONFIG, SYSTEM_MESSAGES
from schemas import (
    StudentWork, MarkingOutput, MarkingResult, Feedback,
    ValidationResult, FinalOutput, Subject
)
from mark_schemes import MARK_SCHEMES

@dataclass
class AgentMetrics:
    """Metrics for individual agent execution"""
    agent_name: str
    start_time: float = 0.0
    end_time: float = 0.0
    duration: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    api_calls: int = 0
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class WorkflowMetrics:
    """Overall workflow execution metrics"""
    total_start_time: float = 0.0
    total_end_time: float = 0.0
    total_duration: float = 0.0
    agent_metrics: Dict[str, AgentMetrics] = field(default_factory=dict)
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_api_calls: int = 0

    def add_agent_metrics(self, metrics: AgentMetrics):
        """Add metrics for an agent execution"""
        self.agent_metrics[metrics.agent_name] = metrics
        self.total_prompt_tokens += metrics.prompt_tokens
        self.total_completion_tokens += metrics.completion_tokens
        self.total_tokens += metrics.total_tokens
        self.total_api_calls += metrics.api_calls

    def print_summary(self):
        """Print comprehensive metrics summary"""
        print("\n" + "="*60)
        print("🔍 AGENT EXECUTION METRICS SUMMARY")
        print("="*60)

        print(f"\n⏱️  TOTAL WORKFLOW DURATION: {self.total_duration:.3f}s")
        print(f"🔗 TOTAL API CALLS: {self.total_api_calls}")
        print(f"🎯 TOTAL TOKENS: {self.total_tokens:,}")
        print(f"   └── Prompt tokens: {self.total_prompt_tokens:,}")
        print(f"   └── Completion tokens: {self.total_completion_tokens:,}")

        print(f"\n📊 AGENT-BY-AGENT BREAKDOWN:")

        for agent_name, metrics in self.agent_metrics.items():
            status = "✅ SUCCESS" if metrics.success else f"❌ FAILED: {metrics.error_message}"
            print(f"\n🤖 {agent_name.upper().replace('_', ' ')}:")
            print(f"   ⏱️  Duration: {metrics.duration:.3f}s")
            print(f"   🔗 API Calls: {metrics.api_calls}")
            print(f"   🎯 Tokens: {metrics.total_tokens:,} (prompt: {metrics.prompt_tokens:,}, completion: {metrics.completion_tokens:,})")
            print(f"   📊 Status: {status}")

        # Performance insights
        print(f"\n💡 PERFORMANCE INSIGHTS:")
        if self.agent_metrics:
            slowest_agent = max(self.agent_metrics.values(), key=lambda x: x.duration)
            print(f"   🐌 Slowest agent: {slowest_agent.agent_name} ({slowest_agent.duration:.3f}s)")

            most_tokens = max(self.agent_metrics.values(), key=lambda x: x.total_tokens)
            print(f"   🔥 Most tokens used: {most_tokens.agent_name} ({most_tokens.total_tokens:,} tokens)")

            avg_duration = sum(m.duration for m in self.agent_metrics.values()) / len(self.agent_metrics)
            print(f"   📈 Average agent duration: {avg_duration:.3f}s")

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

        # Initialize metrics tracking
        self.metrics = WorkflowMetrics()

        # Setup logging for API requests
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

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
        print("\n🚀 Starting Microsoft Agent Framework Marking Workflow...")
        print(f"📝 Processing work for subject: {student_work.subject.value}")
        print(f"📊 Questions to process: {len(student_work.questions)}")

        # Start overall timing
        self.metrics.total_start_time = time.time()

        try:
            # Step 1: Orchestrator coordinates the workflow
            print("\n🎭 Step 1: Orchestrator coordinating workflow...")
            orchestrator_input = {
                "questions": [q.model_dump() for q in student_work.questions],
                "answers": [a.model_dump() for a in student_work.answers],
                "subject": student_work.subject.value,
                "student_id": student_work.student_id
            }

            # Step 2: Marking Agent processes the work
            print("📝 Step 2: Marking Agent grading student work...")
            marking_result = await self._get_marking_result(orchestrator_input)

            # Step 3: Feedback Agent generates feedback
            print("💬 Step 3: Feedback Agent generating educational feedback...")
            feedback_result = await self._get_feedback_result(marking_result)

            # Step 4: Validation Agent validates the results
            print("✅ Step 4: Validation Agent checking consistency...")
            validation_result = await self._get_validation_result(
                marking_result, feedback_result, student_work.subject
            )

            # Calculate total duration
            self.metrics.total_end_time = time.time()
            self.metrics.total_duration = self.metrics.total_end_time - self.metrics.total_start_time

            # Combine all results
            final_output = FinalOutput(
                marking_output=marking_result,
                feedback=feedback_result,
                validation=validation_result,
                processed_timestamp=datetime.now().isoformat()
            )

            # Print comprehensive metrics
            self.metrics.print_summary()

            return final_output

        except Exception as e:
            self.metrics.total_end_time = time.time()
            self.metrics.total_duration = self.metrics.total_end_time - self.metrics.total_start_time
            print(f"\n❌ Workflow failed after {self.metrics.total_duration:.3f}s")
            raise Exception(f"Error processing student work: {str(e)}")

    def _execute_agent_with_metrics(self, agent, user_proxy, prompt: str, agent_name: str) -> str:
        """Execute an agent with comprehensive metrics tracking"""
        metrics = AgentMetrics(agent_name=agent_name)
        metrics.start_time = time.time()

        try:
            print(f"   🔄 Executing {agent_name}...")

            # Reset agent usage before execution
            agent.reset()

            # Execute the agent
            self.logger.info(f"🔗 API Request initiated for {agent_name}")
            user_proxy.initiate_chat(
                agent,
                message=prompt,
                max_turns=1
            )

            metrics.end_time = time.time()
            metrics.duration = metrics.end_time - metrics.start_time
            metrics.api_calls = 1  # Each agent makes one API call
            metrics.success = True

            # Get usage statistics from the agent
            usage_summary = agent.get_actual_usage()
            if usage_summary:
                # AutoGen usage summary format: model -> {prompt_tokens, completion_tokens, total_tokens}
                for model_usage in usage_summary.values():
                    if isinstance(model_usage, dict):
                        metrics.prompt_tokens += model_usage.get('prompt_tokens', 0)
                        metrics.completion_tokens += model_usage.get('completion_tokens', 0)
                        metrics.total_tokens += model_usage.get('total_tokens', 0)

            # Log completion
            self.logger.info(f"✅ {agent_name} completed in {metrics.duration:.3f}s")
            print(f"   ✅ {agent_name} completed ({metrics.duration:.3f}s, {metrics.total_tokens:,} tokens)")

            # Get the response
            last_message = user_proxy.last_message()
            response_text = last_message["content"] if last_message else ""

        except Exception as e:
            metrics.end_time = time.time()
            metrics.duration = metrics.end_time - metrics.start_time
            metrics.success = False
            metrics.error_message = str(e)
            print(f"   ❌ {agent_name} failed after {metrics.duration:.3f}s: {str(e)}")
            raise e
        finally:
            # Always add metrics regardless of success/failure
            self.metrics.add_agent_metrics(metrics)

        return response_text

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

        # Execute agent with metrics tracking
        response_text = self._execute_agent_with_metrics(
            self.marking_agent, user_proxy, marking_prompt, "marking_agent"
        )

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

        # Execute agent with metrics tracking
        response_text = self._execute_agent_with_metrics(
            self.feedback_agent, user_proxy, feedback_prompt, "feedback_agent"
        )

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

        # Execute agent with metrics tracking
        response_text = self._execute_agent_with_metrics(
            self.validation_agent, user_proxy, validation_prompt, "validation_agent"
        )

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