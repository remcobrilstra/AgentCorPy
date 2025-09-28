# GitHub Copilot Instructions for AgentCorp

## Dependency Management
- **Always prefer existing dependencies**: Before suggesting to install new packages, check if the functionality can be implemented using the current dependencies (openai, anthropic, xai).
- **Minimize new dependencies**: Only suggest adding new packages when absolutely necessary and no existing solution works.
- **Check requirements.txt**: Always review the current requirements.txt before proposing changes.

## Environment Management
- **Always use the virtual environment**: All Python commands, installations, and executions must use the project's virtual environment located at `.venv/`.
- **Virtual environment path**: Use `D:/Development/Projects/AgentCorp/.venv/Scripts/python.exe` for Windows or the appropriate path for other systems.
- **Activation**: When running commands, ensure the virtual environment is activated first.

## Documentation Updates
- **Update README.md**: For any changes that affect how users interact with or use the framework, immediately update the README.md file.
- **Usage changes**: If new features, API changes, or configuration requirements are added, document them in README.md.
- **Examples**: Keep examples in README.md current and functional.

## Code Quality
- **Follow existing patterns**: Maintain consistency with the current codebase structure and coding style.
- **Error handling**: Implement proper error handling, especially for API calls and external dependencies.
- **Testing**: Suggest adding tests for new functionality using the existing test patterns.

## Framework-Specific Guidelines
- **Provider abstraction**: When adding new providers, follow the existing Provider base class pattern in `agentcorp/providers/base.py`.
- **Tool integration**: Use the existing Tool and ToolRegistry classes for function calling. Register tools in `global_tool_registry` and specify `tool_names` when creating agents.
- **Tool Context System**: Use `ToolExecutionContext` for all tool operations, passing context with security settings and restrictions. Tools receive context as first parameter.
- **Security Settings**: Include appropriate `context_settings` when creating agents to control tool behavior (e.g., `allowed_base_path`, `max_operations`).
- **Complex task handling**: Use the task decomposition and sequential execution capabilities for multi-step operations. Set execution functions on tasks using `task.set_execution_function()`.
- **Agent Configurations**: Use `AgentConfig` and related functions (`load_agent_from_file`, `save_agent_config`) for loading/saving agent configurations from JSON files.
- **Configuration Security**: Never store API keys in configuration files; use environment variables or secure key management.
- **Memory and tasks**: Leverage the existing Memory and TaskManager classes for state management and task tracking.
- **Import handling**: Handle optional imports gracefully (like xAI) to avoid breaking the framework.

## File Organization
- **Keep structure**: Maintain the current package structure under `agentcorp/`.
- **New modules**: Place new functionality in appropriate modules or create new ones if needed.
- **Examples**: Update `example.py` to demonstrate new features, and add comprehensive examples to the `examples/` directory.

## Architecture Patterns

### Provider System
- **Base abstraction**: All providers inherit from `Provider` base class with `chat()` and `chat_with_tools()` methods.
- **Tool format conversion**: Use `tool.to_openai_format()` and `tool.to_anthropic_format()` for provider-specific tool schemas.
- **Environment selection**: Choose providers based on environment variables (e.g., `PROVIDER=openai|anthropic`).

### Tool System Architecture
- **Global registry**: Tools registered in singleton `global_tool_registry` are available framework-wide.
- **Agent subsets**: Agents filter tools using `tool_names` parameter to get specific tool subsets.
- **Context-aware execution**: Tools receive `ToolExecutionContext` with settings like `allowed_base_path` for security.
- **Security patterns**: Use `context.get_setting()` to access security restrictions, `Path.resolve()` for path validation.

### Task Management System
- **Hierarchical tasks**: Complex tasks contain subtasks via `task.add_subtask()` and `TaskManager.add_complex_task()`.
- **Sequential execution**: Use `TaskManager.execute_task_sequentially()` for ordered subtask execution.
- **LLM decomposition**: Use agent methods like `decompose_task()` to break complex queries into subtasks.
- **Execution functions**: Attach custom logic via `task.set_execution_function(lambda agent, task: ...)`.

### Configuration System
- **JSON serialization**: Use `AgentConfig` dataclass with `from_json_file()`/`to_json_file()` methods.
- **Secure key handling**: API keys loaded from environment variables, never stored in config files.
- **Provider instantiation**: `create_agent_from_config()` handles provider creation and agent setup.

## Development Workflow
- **Testing**: Run `python test_framework.py` to validate framework functionality.
- **Virtual environment**: Always use `.venv/` - activate with `.venv/Scripts/Activate.ps1` on Windows.
- **Provider testing**: Set environment variables like `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for testing.
- **Tool development**: Register tools in global registry, test with `ToolExecutionContext` containing security settings.