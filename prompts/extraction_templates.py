from string import Template

# Template for basic task extraction
BASIC_EXTRACTION_TEMPLATE = Template("""
Analyze these filtered task-related messages and extract structured task information.

For each message, extract:
1. Task title/description (what needs to be done)
2. Assignee (who is responsible)
3. Deadline (when it's due)

Input messages:
$messages

Return a list of structured tasks.
""")

# Enhanced template with more detailed extraction
ENHANCED_EXTRACTION_TEMPLATE = Template("""
Analyze the following task-related messages carefully and extract detailed structured information.

For each message, identify the following components:
1. Task title: A clear, concise description of what needs to be done (5-10 words)
2. Task description: More detailed explanation if available
3. Assignee: The person responsible for completing the task
4. Deadline: When the task should be completed (be precise with dates)
5. Priority: Infer priority (High, Medium, Low) based on language and urgency
6. Status: Default to "To Do" unless otherwise indicated

Input messages:
$messages

Follow these extraction rules:
- If a message mentions someone with "@", they are likely the assignee
- Words like "urgent", "ASAP", "critical" indicate high priority
- Time references like "tomorrow", "next week", "by Friday" determine deadline
- If a deadline is relative (e.g., "tomorrow"), convert it to an actual date based on the current date: $current_date
- If information is missing, use null rather than making assumptions

Respond with a structured list of tasks.
""")

def get_extraction_prompt(template_name="enhanced", **kwargs):
    """Get a task extraction prompt based on the specified template.
    
    Args:
        template_name: Name of the template to use ('basic' or 'enhanced')
        **kwargs: Variables to substitute into the template
        
    Returns:
        Formatted prompt string
    """
    if template_name == "basic":
        template = BASIC_EXTRACTION_TEMPLATE
    else:
        template = ENHANCED_EXTRACTION_TEMPLATE
        
    # Add current date if not provided
    if 'current_date' not in kwargs:
        from datetime import datetime
        kwargs['current_date'] = datetime.now().strftime('%Y-%m-%d')
        
    return template.substitute(**kwargs)
