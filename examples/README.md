# AgentCorp Examples

This directory contains example scripts demonstrating various capabilities of the AgentCorp framework.

## Examples

### `logging_example.py`

Demonstrates the AgentCorp logging framework for debugging and monitoring:

- **Verbose Logging**: Enable detailed debug logs for tool calls and task actions
- **Environment Variable Control**: Set `AGENTCORP_VERBOSE=true` for debug output
- **Programmatic Control**: Enable/disable verbose logging in code
- **Structured Logging**: Consistent log format with timestamps and log levels

**Key Features Demonstrated:**
- Task creation and status change logging
- Tool call logging with arguments and results
- Environment variable configuration
- Programmatic logging control

**Usage:**
```bash
# Enable verbose logging
export AGENTCORP_VERBOSE=true

# Run the example
python examples/logging_example.py
```

**What it does:**
1. Enables verbose logging
2. Creates a task and logs the action
3. Updates task status and logs the change
4. Shows debug output for all operations

### `complex_task_agent.py`

Demonstrates advanced task management capabilities including:

- **Automatic Task Decomposition**: The agent can analyze complex queries and break them down into manageable subtasks
- **Sequential Task Execution**: Tasks and subtasks are executed in logical order
- **Custom Execution Functions**: Attach custom logic to specific tasks for specialized processing
- **Task Status Tracking**: Monitor progress of complex multi-step operations

**Key Features Demonstrated:**
- Complex query analysis and decomposition
- Hierarchical task management (tasks with subtasks)
- Sequential execution of dependent tasks
- Integration with different LLM providers
- Custom task execution logic

**Usage:**
```bash
# Set your API key
export OPENAI_API_KEY="your-key-here"

# Run the example
python examples/complex_task_agent.py

# Or use Anthropic
export ANTHROPIC_API_KEY="your-key-here"
export PROVIDER=anthropic
python examples/complex_task_agent.py
```

**What it does:**
1. Tests simple vs complex query detection
2. Demonstrates automatic task decomposition
3. Shows manual task creation and execution
4. Illustrates custom execution functions

### `tool_context_example.py`

Demonstrates the enhanced tool system with context-aware execution:

- **Central Tool Registry**: Global tool registration and management
- **Agent Tool Subsets**: Agents can be configured with specific tool access
- **Tool Execution Context**: Tools receive context with settings and restrictions
- **Security Controls**: Path restrictions, operation limits, and access controls
- **Context Settings**: Configurable behavior based on agent permissions

**Key Features Demonstrated:**
- Tool registration in global registry
- Agent-specific tool assignment by name
- Context-based security restrictions (file paths, operation limits)
- Different agent permission levels
- Manual context creation and tool execution

**Usage:**
```bash
# Set your API key
export OPENAI_API_KEY="your-key-here"

# Run the example
python examples/tool_context_example.py

# Or use Anthropic
export ANTHROPIC_API_KEY="your-key-here"
export PROVIDER=anthropic
python examples/tool_context_example.py
```

### `chat_with_code_assistant.py`

Demonstrates an interactive chat session with the Code Assistant agent:

- **Interactive Chat**: Real-time conversation with the coding assistant
- **Working Directory Setup**: Configure the agent's working directory before starting
- **File Reading Tools**: Access to filesystem tools for code analysis
- **Provider Flexibility**: Works with OpenAI, Anthropic, or xAI providers

**Key Features Demonstrated:**
- Loading agents from configuration files
- Interactive chat interface
- Working directory configuration
- Error handling and user input validation

**Usage:**
```bash
# Set your API key
export OPENAI_API_KEY="your-key-here"

# Run the chat script
python examples/chat_with_code_assistant.py

# Or use Anthropic
export ANTHROPIC_API_KEY="your-key-here"
export PROVIDER=anthropic
python examples/chat_with_code_assistant.py
```

**What it does:**
1. Prompts for working directory (defaults to current)
2. Loads the Code Assistant agent from configuration
3. Starts an interactive chat session
4. Processes user messages and displays agent responses
5. Continues until user types 'quit', 'exit', or 'bye'

### `agent_config_example.py`

Demonstrates loading and saving agent configurations from/to JSON files:

- **Configuration Files**: Load agent configurations from JSON files
- **Programmatic Creation**: Create agents from configuration objects
- **Saving Configurations**: Save agent configurations to files
- **JSON String Support**: Work with configuration as JSON strings
- **Flexible Loading**: Support for different providers and tool sets

**Key Features Demonstrated:**
- Loading agents from `agent_configs/` directory files
- Creating agents programmatically with `AgentConfig`
- Saving agent configurations back to files
- JSON string-based configurations for dynamic agent creation

**Usage:**
```bash
# Set your API key
export OPENAI_API_KEY="your-key-here"

# Run the example
python examples/agent_config_example.py
```

## Running Examples

All examples require API keys for the LLM providers. Make sure to set the appropriate environment variables before running:

- `OPENAI_API_KEY`: For OpenAI GPT models
- `ANTHROPIC_API_KEY`: For Anthropic Claude models
- `PROVIDER`: Set to "anthropic" to use Anthropic instead of OpenAI (defaults to OpenAI)

## Framework Capabilities Showcased

- Provider abstraction (OpenAI, Anthropic, xAI)
- Memory management with conversation history
- Tool integration and function calling
- Task decomposition and sequential execution
- Hierarchical task management
- Custom execution logic for specialized tasks