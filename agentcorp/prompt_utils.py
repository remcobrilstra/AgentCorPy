import os
import re

def load_prompt(name, **params):
    """
    Load a prompt from a markdown file in the prompts folder.
    
    Args:
        name (str): The name of the prompt file (without .md extension)
        **params: Keyword arguments for parameter replacement
    
    Returns:
        dict: A dictionary with 'type', 'description', and 'content' keys
    """
    path = os.path.join('prompts', f'{name}.md')
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file '{name}.md' not found in prompts folder")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse frontmatter
    lines = content.split('\n')
    metadata = {}
    body_start = 0
    
    if lines and lines[0].strip() == '---':
        try:
            frontmatter_end = lines.index('---', 1)
            frontmatter_lines = lines[1:frontmatter_end]
            body_start = frontmatter_end + 1
            
            for line in frontmatter_lines:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()
        except (ValueError, IndexError):
            # Malformed frontmatter, treat as body
            body_start = 0
    
    body = '\n'.join(lines[body_start:]).strip()
    
    # Replace parameters
    for param, value in params.items():
        body = body.replace(f'{{{{{param}}}}}', str(value))
    
    return {
        'type': metadata.get('type', 'system'),
        'description': metadata.get('description', ''),
        'content': body
    }

def get_parameters(name):
    """
    Get a list of all parameters in a prompt.
    
    Args:
        name (str): The name of the prompt file (without .md extension)
    
    Returns:
        list: List of parameter names found in the prompt
    """
    path = os.path.join('prompts', f'{name}.md')
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt file '{name}.md' not found in prompts folder")
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find body content (skip frontmatter)
    lines = content.split('\n')
    body_start = 0
    if lines and lines[0].strip() == '---':
        try:
            frontmatter_end = lines.index('---', 1)
            body_start = frontmatter_end + 1
        except (ValueError, IndexError):
            pass
    
    body = '\n'.join(lines[body_start:])
    
    # Find all {{PARAM}} patterns
    pattern = r'\{\{(\w+)\}\}'
    matches = re.findall(pattern, body)
    return list(set(matches))  # Return unique parameters