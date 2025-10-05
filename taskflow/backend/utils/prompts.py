
import json
from langchain_core.prompts import ChatPromptTemplate

"""
Prompt templates for LLM-based task extraction from conversation messages.
"""

# System prompt: sets the model's behavior and instructions
TASK_EXTRACTION_SYSTEM_PROMPT = '''
You are an expert assistant that extracts actionable tasks from conversation messages.
Given a message, identify all actionable tasks and return them as a JSON array.

Each task should include:
- title: a concise summary of the task
- description: details about the task
- priority: one of [high, medium, low]
- due_date: if mentioned, in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS), else null
- assigned_to: the person responsible, if mentioned, else null
- labels: any relevant tags or labels

If no tasks are found, return an empty array.
'''

# # Few-shot examples for task extraction
# TASK_EXTRACTION_FEWSHOTS = [
#     {
#         "input": "We need to fix the login bug by Friday. @john please update the documentation ASAP.",
#         "output": [
#             {
#                 "title": "Fix the login bug",
#                 "description": "Resolve the login issue mentioned in the conversation.",
#                 "priority": "high",
#                 "due_date": "2025-10-03",
#                 "assigned_to": None,
#                 "labels": ["bugfix"]
#             },
#             {
#                 "title": "Update the documentation",
#                 "description": "@john should update the documentation as soon as possible.",
#                 "priority": "high",
#                 "due_date": None,
#                 "assigned_to": "john",
#                 "labels": ["documentation"]
#             }
#         ]
#     }
# ]

TASK_EXTRACTION_USER_PROMPT = "Message:\n{message}\n\nExtracted tasks:"

def build_extraction_prompt_with_few_shots() -> ChatPromptTemplate:
    prompt = ChatPromptTemplate.from_messages([
        ("system", TASK_EXTRACTION_SYSTEM_PROMPT),
        ("user", TASK_EXTRACTION_USER_PROMPT)
    ])
    return prompt