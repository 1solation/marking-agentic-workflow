"""
Mark schemes for different subjects
Each subject has detailed marking criteria and rubrics
"""

MARK_SCHEMES = {
    "mathematics": {
        "general_criteria": {
            "accuracy": "Correct mathematical procedures and calculations",
            "method": "Appropriate mathematical methods and reasoning",
            "communication": "Clear mathematical communication and notation",
            "interpretation": "Correct interpretation of results"
        },
        "grade_boundaries": {
            "A": 0.8,  # 80% and above
            "B": 0.7,  # 70-79%
            "C": 0.6,  # 60-69%
            "D": 0.5,  # 50-59%
            "E": 0.4   # 40-49%
        },
        "marking_guidelines": [
            "Award full marks for complete correct solutions",
            "Award partial marks for correct method with minor errors",
            "Award method marks even if final answer is incorrect",
            "Deduct marks for poor mathematical communication"
        ]
    },
    "english": {
        "general_criteria": {
            "content": "Relevance, depth of understanding, and insight",
            "structure": "Organization, coherence, and logical flow",
            "language": "Grammar, vocabulary, and style",
            "analysis": "Critical analysis and evaluation skills"
        },
        "grade_boundaries": {
            "A": 0.8,
            "B": 0.7,
            "C": 0.6,
            "D": 0.5,
            "E": 0.4
        },
        "marking_guidelines": [
            "Assess understanding of text and context",
            "Evaluate quality of argument and evidence",
            "Consider technical accuracy in language use",
            "Reward original thinking and insight"
        ]
    },
    "science": {
        "general_criteria": {
            "knowledge": "Factual accuracy and understanding",
            "application": "Application of scientific principles",
            "analysis": "Data analysis and interpretation",
            "evaluation": "Critical evaluation of evidence"
        },
        "grade_boundaries": {
            "A": 0.8,
            "B": 0.7,
            "C": 0.6,
            "D": 0.5,
            "E": 0.4
        },
        "marking_guidelines": [
            "Award marks for scientific accuracy",
            "Consider quality of explanations",
            "Assess practical understanding",
            "Evaluate experimental design and analysis"
        ]
    },
    "history": {
        "general_criteria": {
            "knowledge": "Historical knowledge and understanding",
            "analysis": "Analysis of sources and evidence",
            "evaluation": "Evaluation of different interpretations",
            "communication": "Clear historical argument"
        },
        "grade_boundaries": {
            "A": 0.8,
            "B": 0.7,
            "C": 0.6,
            "D": 0.5,
            "E": 0.4
        },
        "marking_guidelines": [
            "Assess historical knowledge and understanding",
            "Evaluate use of sources and evidence",
            "Consider different historical interpretations",
            "Reward clear historical argument"
        ]
    },
    "geography": {
        "general_criteria": {
            "knowledge": "Geographical knowledge and understanding of places, processes and concepts",
            "application": "Application of geographical skills and techniques",
            "analysis": "Analysis and interpretation of data, maps and sources",
            "evaluation": "Evaluation of issues and decision-making"
        },
        "grade_boundaries": {
            "A": 0.8,
            "B": 0.7,
            "C": 0.6,
            "D": 0.5,
            "E": 0.4
        },
        "marking_guidelines": [
            "Assess geographical knowledge and understanding",
            "Evaluate use of geographical terminology",
            "Consider quality of case study examples",
            "Assess map skills and data interpretation",
            "Reward analysis of geographical processes and patterns"
        ]
    }
}