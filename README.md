# Microsoft Agent Framework - Academic Marking Workflow

An intelligent multi-agent system built with Microsoft Agent Framework (AutoGen) and OpenAI GPT-4 for automated academic assessment, feedback generation, and validation with **comprehensive metrics tracking**.

## 🎯 Overview

This system implements a comprehensive marking workflow using four specialized AI agents with real-time performance monitoring:

1. **🎭 Orchestrator Agent**: Coordinates the workflow and routes tasks between agents
2. **📝 Dynamic Marking Agent**: Applies subject-specific mark schemes to grade student work
3. **💬 Feedback Agent**: Generates constructive feedback for teachers and students
4. **✅ Validation Agent**: Ensures consistency and quality of marking decisions

## 📊 **NEW: Enhanced Metrics & Monitoring**

### Real-time Performance Tracking
- **⏱️ Duration tracking** for each agent and overall workflow
- **🔗 API request monitoring** with detailed logging
- **🎯 Token usage tracking** (prompt, completion, and total tokens)
- **📈 Performance insights** and optimization suggestions

### Sample Metrics Output
```
============================================================
🔍 AGENT EXECUTION METRICS SUMMARY
============================================================

⏱️  TOTAL WORKFLOW DURATION: 8.734s
🔗 TOTAL API CALLS: 3
🎯 TOTAL TOKENS: 2,847
   └── Prompt tokens: 1,923
   └── Completion tokens: 924

📊 AGENT-BY-AGENT BREAKDOWN:

🤖 MARKING AGENT:
   ⏱️  Duration: 3.245s
   🔗 API Calls: 1
   🎯 Tokens: 1,456 (prompt: 1,102, completion: 354)
   📊 Status: ✅ SUCCESS

🤖 FEEDBACK AGENT:
   ⏱️  Duration: 2.891s
   🔗 API Calls: 1
   🎯 Tokens: 892 (prompt: 543, completion: 349)
   📊 Status: ✅ SUCCESS

🤖 VALIDATION AGENT:
   ⏱️  Duration: 2.598s
   🔗 API Calls: 1
   🎯 Tokens: 499 (prompt: 278, completion: 221)
   📊 Status: ✅ SUCCESS

💡 PERFORMANCE INSIGHTS:
   🐌 Slowest agent: marking_agent (3.245s)
   🔥 Most tokens used: marking_agent (1,456 tokens)
   📈 Average agent duration: 2.911s
```

```
Input (Questions + Answers + Subject)
           ↓
    Orchestrator Agent
           ↓
   Dynamic Marking Agent ← Mark Schemes
           ↓
     Feedback Agent
           ↓
    Validation Agent
           ↓
Output (Marks + Feedback + Validation)
```

## ✨ Features

- **Multi-Subject Support**: Mathematics, English, Science, History, Geography, and more
- **Intelligent Marking**: Context-aware grading with confidence scores
- **Dual Feedback**: Separate feedback for teachers and students
- **Quality Validation**: Consistency checking and bias detection
- **Structured Output**: JSON-based results with detailed reasoning
- **Extensible Design**: Easy to add new subjects and marking criteria
- **📊 Performance Monitoring**: Real-time metrics, timing, and token usage tracking
- **🔗 API Request Logging**: Detailed network request monitoring
- **⚡ Optimization Insights**: Performance analysis and bottleneck identification

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Microsoft AutoGen library
- Pydantic for data validation

## 🚀 Quick Start

### 1. Setup

```bash
# Clone and setup
git clone <repository>
cd marking-agentic-workflow

# Run setup script
python setup.py

# Edit environment file with your OpenAI API key
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

### 2. Basic Usage

```python
from main import MarkingWorkflowApp
import asyncio

# Initialize the application
app = MarkingWorkflowApp()

# Prepare input data
input_data = {
    "questions": [
        {
            "question_id": "q1",
            "question_text": "Explain photosynthesis",
            "max_marks": 10,
            "question_type": "essay"
        }
    ],
    "answers": [
        {
            "question_id": "q1",
            "student_response": "Photosynthesis is the process where..."
        }
    ],
    "subject": "science",
    "student_id": "student_001"
}

# Process marking
result = await app.process_marking_request(input_data)
print(result)
```

### 3. Run Examples

```bash
# Run with sample data
python main.py

# Interactive mode
python main.py --interactive

# Run test suite
python utils.py

# Run a specific subject test util scrip
python run.py test geography
```

## 📊 Input/Output Format

### Input Structure
```json
{
  "questions": [
    {
      "question_id": "string",
      "question_text": "string",
      "max_marks": 10,
      "question_type": "essay|calculation|multiple_choice"
    }
  ],
  "answers": [
    {
      "question_id": "string",
      "student_response": "string"
    }
  ],
  "subject": "mathematics|english|science|history|geography",
  "student_id": "string (optional)"
}
```

### Output Structure
```json
{
  "marking_output": {
    "student_id": "string",
    "subject": "string",
    "results": [
      {
        "question_id": "string",
        "marks_awarded": 8,
        "max_marks": 10,
        "confidence": 0.95,
        "reasoning": "Detailed explanation..."
      }
    ],
    "total_marks_awarded": 85,
    "total_max_marks": 100,
    "percentage": 85.0
  },
  "feedback": {
    "teacher_feedback": "Professional assessment for educators",
    "student_feedback": "Encouraging guidance for learners",
    "strengths": ["Clear explanations", "Good examples"],
    "areas_for_improvement": ["Mathematical notation", "Conclusion"],
    "next_steps": ["Practice more problems", "Review concepts"]
  },
  "validation": {
    "is_valid": true,
    "consistency_score": 0.92,
    "validation_notes": ["Marking consistent with rubric"],
    "suggested_corrections": null
  },
  "processed_timestamp": "2024-01-15T10:30:00"
}
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.1
MAX_ROUNDS=10
TIMEOUT=300
```

### Mark Schemes (mark_schemes.py)
Each subject has customizable marking criteria:
- General assessment criteria
- Grade boundaries
- Specific marking guidelines
- Subject-specific rubrics

## 🧪 Testing

### Comprehensive Test Suite
Run the comprehensive test suite:

```bash
# Full test suite
python utils.py

# Individual subject test
python -c "
import asyncio
from utils import MarkingTestRunner
runner = MarkingTestRunner()
asyncio.run(runner.test_individual_subject('mathematics'))
"
```

### 📊 **NEW: Metrics Testing**
Test the enhanced monitoring system:

```bash
# Test metrics tracking system
python test_metrics.py

# Run with detailed metrics output
python run.py mark              # Sample data with full metrics
python run.py test geography    # Subject-specific testing
```

### Performance Monitoring Output
When you run any workflow, you'll see:
- **Step-by-step progress** with agent execution status
- **Real-time timing** for each agent execution
- **API request logging** with detailed network activity
- **Token usage breakdown** by agent and operation type
- **Performance insights** with optimization suggestions
- **Comprehensive summary** with totals and analysis

## 📁 Project Structure

```
marking-agentic-workflow/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── setup.py                 # Setup script
├── .env.example             # Environment template
├── main.py                  # Main application entry point
├── agents.py                # Agent implementations
├── schemas.py               # Data models and validation
├── config.py                # Configuration management
├── mark_schemes.py          # Subject-specific marking criteria
├── utils.py                 # Testing and utilities
└── examples/
    └── sample_data.json     # Sample input data
```

## 🎨 Customization

### Adding New Subjects

1. **Update schemas.py**: Add subject to `Subject` enum
```python
class Subject(str, Enum):
    NEW_SUBJECT = "new_subject"
```

2. **Update mark_schemes.py**: Add marking criteria
```python
MARK_SCHEMES["new_subject"] = {
    "general_criteria": {...},
    "grade_boundaries": {...},
    "marking_guidelines": [...]
}
```

### Custom Marking Criteria

Edit `mark_schemes.py` to modify:
- Assessment criteria weights
- Grade boundaries
- Marking guidelines
- Subject-specific rubrics

## 🔍 Agent Details

### Orchestrator Agent
- **Role**: Workflow coordination and task routing
- **Input**: Raw student work data
- **Output**: Structured data for downstream agents
- **Features**: Input validation, error handling, workflow management

### Dynamic Marking Agent
- **Role**: Subject-specific academic assessment
- **Input**: Questions, answers, subject, mark scheme
- **Output**: Marks, confidence scores, reasoning
- **Features**: Multi-subject support, partial credit, detailed feedback

### Feedback Agent
- **Role**: Educational guidance generation
- **Input**: Marking results and student performance
- **Output**: Teacher/student feedback, improvement suggestions
- **Features**: Differentiated feedback, constructive guidance, actionable steps

### Validation Agent
- **Role**: Quality assurance and consistency checking
- **Input**: Marks, feedback, mark scheme
- **Output**: Validation status, consistency scores, correction suggestions
- **Features**: Bias detection, consistency analysis, quality metrics

## 🚨 Error Handling

The system includes comprehensive error handling:
- Input validation and sanitization
- Agent communication failure recovery
- OpenAI API error handling
- Timeout and retry mechanisms
- Detailed error reporting

## 📈 Performance Considerations

- **Async Processing**: All agents run asynchronously
- **Configurable Timeouts**: Prevent hanging operations
- **Response Caching**: Optional caching for repeated queries
- **Batch Processing**: Support for multiple student submissions

## 🔒 Security & Privacy

- **API Key Protection**: Environment-based configuration
- **Data Validation**: Strict input/output validation
- **No Data Persistence**: Stateless processing by default
- **Audit Logging**: Optional logging for compliance

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the examples and test files
2. Review configuration settings
3. Validate your OpenAI API key
4. Check Python version compatibility

## 🔄 Version History

- **v1.0.0**: Initial release with four-agent workflow
- Microsoft Agent Framework integration
- Multi-subject marking support
- Comprehensive validation system
- **v1.1.0**: Enhanced Performance Monitoring
- **📊 Real-time metrics tracking** for all agents
- **⏱️ Duration monitoring** with millisecond precision
- **🔗 API request logging** with detailed network monitoring
- **🎯 Token usage tracking** (prompt, completion, total)
- **💡 Performance insights** and optimization suggestions
- **📈 Comprehensive reporting** with visual metrics summary
- AutoGen v0.9.0 compatibility and Pydantic v2 support
