# AgentCorp - Simple Agent Framework

A simple Python framework for building AI agents that abstracts away different LLM provider SDKs.

## TODO: Additional Tools for Programmer Agent

To enhance the Programmer Agent's capabilities for comprehensive software development workflows, the following tool categories are planned for future implementation. These tools will follow the existing security patterns using `ToolExecutionContext` and respect settings like `workingdir`.

### 1. Version Control Tools (Git Integration)
- **git_status**: Check repository status, staged/unstaged changes, branch info.
- **git_diff**: Show differences between commits, working directory, or branches.
- **git_commit**: Stage and commit changes with messages.
- **git_push/pull**: Sync with remote repositories.
- **git_clone**: Clone repositories (with path restrictions).
- **git_log**: View commit history.

### 2. Terminal/Command Execution Tools
- **run_command**: Execute shell commands safely within the working directory, with output capture and timeout limits. ✅ **COMPLETED**
- **run_script**: Execute scripts (Python, shell, etc.) with environment control.

### 3. Code Quality and Analysis Tools
- **lint_code**: Run linters like pylint, flake8, or eslint on files/directories.
- **format_code**: Auto-format code using black, prettier, or similar.
- **analyze_code**: Static analysis for complexity, dependencies, or security issues.
- **grep_search**: Search for patterns within files (complementing `file_search` for content). ✅ **COMPLETED**

### 4. Testing and Debugging Tools
- **run_tests**: Execute unit tests (pytest, unittest) and capture results.
- **debug_code**: Run code with debugging tools or profilers.
- **coverage_report**: Generate test coverage reports.

### 5. Package and Dependency Management Tools
- **install_package**: Install Python packages via pip (with virtual environment awareness).
- **manage_requirements**: Update/create requirements.txt, check for updates/outdated packages.
- **virtualenv_manage**: Create/activate/manage virtual environments.

### 6. Documentation Tools
- **generate_docs**: Create documentation from code (e.g., using Sphinx or pdoc).
- **update_readme**: Auto-update README files based on code changes.

### 7. Build and Deployment Tools
- **build_project**: Run build commands (e.g., setup.py, Makefile).
- **deploy_app**: Basic deployment helpers (e.g., to cloud platforms, with security checks).

### 8. Advanced Code Manipulation Tools
- **refactor_code**: Suggest/apply code refactorings (e.g., rename variables, extract functions).
- **code_review**: Analyze code for best practices, bugs, or improvements.

## Features

- **Provider Abstraction**: Unified interface for OpenAI, Anthropic, and xAI
- **Agent Concept**: Agents with model/provider, tools, system prompts, memory, and task tracking
- **Memory Management**: Conversation history with configurable limits
- **Task Tracking**: Keep track of current tasks for longer running operations
- **Tool Integration**: Support for function calling/tools with compatible providers
- **Complex Task Handling**: Automatic decomposition of complex tasks into subtasks with sequential execution
- **Tool Context System**: Context-aware tool execution with security settings and restrictions
- **Built-in Tools**: Framework includes web scraping and secure filesystem tools for content retrieval and file management
- **Agent Configuration**: Load and save agent configurations from/to JSON files
- **Logging Framework**: Configurable logging with verbose mode for debugging tool calls and task actions

## Logging

AgentCorp includes a simple logging framework for debugging and monitoring agent activities. The logging system provides detailed information about tool calls, task execution, and agent actions.

### Verbose Logging

Enable verbose logging by setting the `AGENTCORP_VERBOSE` environment variable:

```bash
export AGENTCORP_VERBOSE=true
python your_script.py
```

Or programmatically:

```python
from agentcorp import set_verbose_logging

# Enable verbose logging
set_verbose_logging(True)

# Your agent code here...
```

### Log Output

When verbose logging is enabled, you'll see detailed logs including:

- **Tool Calls**: When tools are invoked with their arguments and results
- **Task Actions**: Task creation, status changes, and execution progress
- **Agent Activities**: Task decomposition, sequential execution, and complex query handling

Example log output:
```
2024-01-15 10:30:15,123 - AgentCorp - DEBUG - Tool call: web_fetch({'url': 'https://example.com'})
2024-01-15 10:30:16,456 - AgentCorp - DEBUG - Tool call: web_fetch({'url': 'https://example.com'}) -> Content fetched successfully
2024-01-15 10:30:16,789 - AgentCorp - DEBUG - Task created: [abc123] Analyze data
2024-01-15 10:30:17,012 - AgentCorp - DEBUG - Task execution_started: [abc123] Analyze data
```

### Log Levels

- **INFO**: General information about agent operations
- **DEBUG**: Detailed debugging information including tool calls and task actions (enabled with verbose mode)
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for failures

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the environment: `.venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install openai anthropic xai`

## Testing

The framework includes comprehensive tests organized in the `tests/` directory:

- `tests/test_framework.py` - Core framework functionality tests (tasks, tool context, web tools)
- `tests/test_filesystem_tools.py` - Filesystem tool registration and basic functionality tests
- `tests/test_filesystem_tools_integration.py` - Comprehensive integration tests for filesystem tools

### Running Tests

To run all tests, use the unified test runner:

```bash
python run_tests.py
```

This will execute all test suites and provide a summary of results. The test runner automatically sets the correct Python path and handles test execution.

### Individual Test Execution

You can also run individual test files directly:

```bash
python tests/test_framework.py
python tests/test_filesystem_tools.py
python tests/test_filesystem_tools_integration.py
```

## Usage

```python
from agentcorp import Agent, OpenAIProvider, Tool, ToolRegistry

# Create provider
provider = OpenAIProvider(api_key="your-openai-key")

# Register tools in global registry
from agentcorp import global_tool_registry

tool = Tool(name="my_tool", description="...", function=my_function, parameters={...})
global_tool_registry.register_tool(tool)

# Create agent with specific tools and context
agent = Agent(
    provider=provider,
    system_prompt="You are a helpful assistant.",
    tool_names=["my_tool"],  # Specify which tools this agent can use
    context_settings={
        "allowed_paths": "/safe/path",
        "max_operations": "10"
    }
)

# Chat
response = agent.chat("Hello!")
print(response)

# Manage tasks
task_id = agent.add_task("Analyze data")
tasks = agent.get_tasks()
agent.update_task(task_id, "completed")

# Handle complex tasks automatically
response = agent.handle_complex_query("Plan a complete software development project")
print(response)

# Manual task decomposition and execution
task_id = agent.decompose_task("Write a research paper on AI ethics")
result = agent.execute_task_sequentially(task_id)
print(result)
```

## Development Guidelines

This project uses GitHub Copilot with specific instructions defined in `.github/copilot-instructions.md`. Key guidelines for contributors:

- **Dependencies**: Always prefer existing dependencies over adding new ones
- **Environment**: Always use the virtual environment (`.venv/`) for all Python operations
- **Documentation**: Update this README.md for any changes affecting framework usage

## Agent Configuration Files

Agents can be defined using JSON configuration files. Example structure:

```json
{
  "name": "MyAgent",
  "description": "A helpful assistant",
  "model": "gpt-4",
  "provider": "openai",
  "system_prompt": "You are a helpful assistant.",
  "tools": ["tool1", "tool2"],
  "context_settings": {
    "setting1": "value1"
  }
}
```

### System Prompt Options

The `system_prompt` field supports two formats:

1. **Direct string** (backward compatible):
   ```json
   "system_prompt": "You are a helpful assistant."
   ```

2. **File reference with parameters**:
   ```json
   "system_prompt": {
     "file": "data_analyst",
     "params": {
       "AGENT_NAME": "DataAnalyzer",
       "ANALYSIS_TYPE": "statistical and exploratory"
     }
   }
   ```

   This loads a prompt from `prompts/data_analyst.md` and replaces `{{AGENT_NAME}}` and `{{ANALYSIS_TYPE}}` with the provided values.

See `agent_configs/` directory for example configurations and `examples/agent_config_example.py` for usage.

## Supported Providers

- **OpenAI**: GPT models with tool calling
- **Anthropic**: Claude models with tool calling
- **xAI**: Grok models including grok-4-fast

## Running the Example

Set your API key as an environment variable:

```bash
export OPENAI_API_KEY="your-key-here"
python example.py
```

Or for Anthropic:

```bash
export ANTHROPIC_API_KEY="your-key-here"
export PROVIDER=anthropic
python example.py
```

Or for xAI:

```bash
export XAI_API_KEY="your-key-here"
export PROVIDER=xai
python example.py
```

## XAI Agent Example

A simple example demonstrating an agent using xAI's grok-4-fast model:

```bash
python examples/xai_agent_example.py
```

This example shows:
- Creating an agent with the XAI provider
- Using the grok-4-fast model
- Simple conversation without tools

**Setup:**
1. Add your xAI API key to the `.env` file: `XAI_API_KEY=your_key_here`
2. Run the example

## Built-in Tools

The framework includes several built-in tools that are automatically available:

### Web Fetch Tool

Fetch content from URLs and convert it to markdown format.

```python
# The web_fetch tool is automatically registered
result = agent.chat("Fetch the content from https://example.com")
```

Parameters:
- `url` (string, required): The URL to fetch content from
- `render_js` (boolean, optional): Whether to render JavaScript for client-side content (default: false)

Example usage with JavaScript rendering:
```python
# For sites that require JavaScript execution
result = global_tool_registry.execute_tool({
    "function": {"name": "web_fetch", "arguments": '{"url": "https://example.com", "render_js": true}'}
}, context)
```

### Filesystem Tools

Secure file operations with working directory restrictions. All filesystem operations are restricted to the `workingdir` setting if specified in the agent's context.

#### read_file
Read the contents of a file.

```python
# Using with an agent
response = agent.chat("Read the file config.json")

# Direct tool execution
result = read_tool.execute(context, file_path="config.json", encoding="utf-8")
```

Parameters:
- `file_path` (string, required): Path to the file to read
- `encoding` (string, optional): File encoding (default: utf-8)

#### write_file
Write content to a file. Creates parent directories if needed.

```python
# Using with an agent
response = agent.chat("Create a file called 'data.txt' with the content 'Hello World'")

# Direct tool execution
result = write_tool.execute(context, 
                          file_path="data.txt", 
                          content="Hello World",
                          encoding="utf-8",
                          create_dirs=True)
```

Parameters:
- `file_path` (string, required): Path to the file to write
- `content` (string, required): Content to write to the file
- `encoding` (string, optional): File encoding (default: utf-8)
- `create_dirs` (boolean, optional): Whether to create parent directories if they don't exist (default: true)

#### replace_in_file
Replace text in a file.

```python
# Using with an agent
response = agent.chat("Replace 'old_value' with 'new_value' in config.json")

# Direct tool execution
result = replace_tool.execute(context,
                            file_path="config.json",
                            old_text="old_value",
                            new_text="new_value",
                            count=1)  # Replace only first occurrence
```

Parameters:
- `file_path` (string, required): Path to the file to modify
- `old_text` (string, required): Text to search for and replace
- `new_text` (string, required): Text to replace with
- `encoding` (string, optional): File encoding (default: utf-8)
- `count` (integer, optional): Maximum number of replacements (-1 for all occurrences, default: -1)

#### file_search
Search for files in the workspace by glob pattern. Returns paths of matching files, limited to 20 results.

```python
# Using with an agent
response = agent.chat("Find all Python files in the project")
# or more specific:
response = agent.chat("Search for files matching '**/*.py' pattern")

# Direct tool execution
result = search_tool.execute(context, query="**/*.py", max_results=20)
```

Parameters:
- `query` (string, required): Search for files with names or paths matching this glob pattern
- `max_results` (integer, optional): Maximum number of results to return (default: 20)

Glob pattern examples:
- `**/*.{js,ts}` - Match all JavaScript and TypeScript files
- `src/**` - Match all files under the src directory
- `**/test/**/*.py` - Match all Python files in any test directory
- `*.json` - Match JSON files in the root directory

#### grep_search
Search for text patterns within files using grep-like functionality. Supports both plain text and regular expressions.

```python
# Using with an agent
response = agent.chat("Search for all TODO comments in Python files")

# Direct tool execution
result = grep_tool.execute(context, 
                         query="TODO", 
                         include_pattern="**/*.py",
                         is_regexp=False,
                         max_results=20)
```

Parameters:
- `query` (string, required): The pattern to search for (plain text or regex)
- `include_pattern` (string, optional): Glob pattern to limit search to specific files (default: "**/*")
- `is_regexp` (boolean, optional): Whether the query is a regular expression (default: false)
- `max_results` (integer, optional): Maximum number of matches to return (default: 20)

#### delete_file
Delete a file.

```python
# Using with an agent
response = agent.chat("Delete the temporary file temp.txt")

# Direct tool execution
result = delete_tool.execute(context, file_path="temp.txt")
```

Parameters:
- `file_path` (string, required): Path to the file to delete

#### Security Features
All filesystem tools implement security restrictions:

- **Working Directory Restriction**: Operations are limited to the `workingdir` setting in the agent's context
- **Path Validation**: Uses `Path.resolve()` to prevent directory traversal attacks
- **Error Handling**: Comprehensive error handling for file permissions, encoding issues, and missing files

Example of creating an agent with filesystem tools and security restrictions:

```python
from agentcorp import Agent, OpenAIProvider

agent = Agent(
    provider=OpenAIProvider(api_key="your-key"),
    system_prompt="You are a file management assistant.",
    tool_names=["read_file", "write_file", "replace_in_file", "delete_file", "file_search"],
    context_settings={
        "workingdir": "/safe/working/directory",  # Restrict file operations to this directory
        "security_level": "restricted"
    }
)

# All file operations will be restricted to /safe/working/directory
response = agent.chat("Create a configuration file with default settings")
```

See `tests/test_filesystem_tools_integration.py` for comprehensive tests and examples.

### Programmer Agent Example

A comprehensive example showing a programmer agent that works on complex software development tasks:

```bash
python examples/programmer_agent_example.py
```

This example demonstrates:
- Loading agent configuration from `programmer_agent_config.json`
- Loading API keys from `.env` file (copy `.env.example` to `.env` and add your keys)
- Setting up a workspace from a simulated git repository
- Task decomposition and iterative execution
- Code analysis and modification using filesystem tools
- Automated testing and documentation updates
- Progress tracking and result verification

The agent improves a calculator application by fixing bugs, adding features, updating tests, and maintaining documentation.

**Setup:**
1. Copy `.env.example` to `.env`
2. Add your OpenAI API key to the `.env` file: `OPENAI_API_KEY=your_key_here`
3. Run the example