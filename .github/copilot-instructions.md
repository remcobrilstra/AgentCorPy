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
- **Provider abstraction**: When adding new providers, follow the existing Provider base class pattern.
- **Tool integration**: Use the existing Tool and ToolRegistry classes for function calling.
- **Memory and tasks**: Leverage the existing Memory and TaskManager classes for state management.
- **Import handling**: Handle optional imports gracefully (like xAI) to avoid breaking the framework.

## File Organization
- **Keep structure**: Maintain the current package structure under `agentcorp/`.
- **New modules**: Place new functionality in appropriate modules or create new ones if needed.
- **Examples**: Update `example.py` to demonstrate new features.