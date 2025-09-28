### Existing AgentCorp Structure for Task Orchestration

Based on the AgentCorp framework, agents are built around providers (e.g., OpenAI, Anthropic), tools (registered in `global_tool_registry`), and a task management system using `TaskManager` and `Task` classes. Key features include:

- **Task Decomposition**: Agents can use `decompose_task()` to break complex queries into subtasks.
- **Hierarchical Tasks**: Complex tasks can contain subtasks via `task.add_subtask()` and `TaskManager.add_complex_task()`.
- **Sequential Execution**: `TaskManager.execute_task_sequentially()` handles ordered subtask execution.
- **Execution Functions**: Custom logic can be attached via `task.set_execution_function(lambda agent, task: ...)`.
- **Memory and State**: `Memory` class for state management across tasks.
- **Agent Configurations**: Loaded from JSON via `AgentConfig`, with secure API key handling.

This provides a foundation for multi-agent collaboration, where agents can share tools, memory, and task contexts.

### Common Patterns for Multi-Agent Orchestration

Multi-agent orchestration involves coordinating multiple agents to achieve a shared goal, often through patterns that manage communication, decision-making, and workflow. Here are some common patterns, adapted to AgentCorp's architecture:

1. **Sequential Pipeline**:
   - Agents execute in a linear sequence, where the output of one agent becomes the input for the next.
   - **Use Case**: Data processing workflows (e.g., one agent analyzes data, another generates a report).
   - **AgentCorp Fit**: Use `TaskManager.execute_task_sequentially()` with subtasks assigned to different agents. Each subtask's execution function can invoke a specific agent via `create_agent_from_config()`.

2. **Parallel Execution**:
   - Agents work concurrently on independent subtasks, then combine results.
   - **Use Case**: Research tasks where agents gather information from different sources simultaneously.
   - **AgentCorp Fit**: Leverage `TaskManager` to create parallel subtasks. Use threading or async execution (if supported) in execution functions, with a final aggregation step.

3. **Hierarchical Supervisor**:
   - A "supervisor" agent decomposes the main task into subtasks, assigns them to "worker" agents, and synthesizes results.
   - **Use Case**: Complex problem-solving (e.g., planning a project with specialized agents for coding, testing, and documentation).
   - **AgentCorp Fit**: The supervisor agent uses `decompose_task()` to create subtasks, each linked to a worker agent via execution functions. Shared `Memory` can store intermediate results.

4. **Consensus-Based Decision Making**:
   - Agents propose solutions, then vote or negotiate to reach agreement.
   - **Use Case**: Collaborative decision-making (e.g., multiple agents reviewing code changes).
   - **AgentCorp Fit**: Implement via a loop in an execution function where agents generate proposals, store them in `Memory`, and a final agent evaluates consensus.

5. **Event-Driven Communication**:
   - Agents communicate via events or shared channels (e.g., publishing/subscribing to task updates).
   - **Use Case**: Real-time collaboration (e.g., agents monitoring and responding to external events).
   - **AgentCorp Fit**: Extend `TaskManager` with event hooks or use `Memory` as a shared bus. Tools can trigger inter-agent messages.

6. **Role-Based Specialization**:
   - Agents have defined roles (e.g., "researcher," "coder," "reviewer") with specific tool subsets.
   - **Use Case**: Team-like workflows (e.g., one agent searches files, another edits code).
   - **AgentCorp Fit**: Use `tool_names` in agent configs to filter tools. Configurations loaded from JSON allow role-specific setups.

### Proposed Approach for AgentCorp

To implement this orchestration system:

- **Orchestrator Class**: Introduce a new `Orchestrator` class that extends `TaskManager`, managing a pool of agents and coordinating their interactions. It could handle agent assignment, result aggregation, and error handling.
- **Agent Pool**: Maintain a registry of agents (similar to `global_tool_registry`) loaded from configs, allowing dynamic selection based on task needs.
- **Communication Layer**: Use `Memory` for shared state, with execution functions facilitating agent-to-agent data passing.
- **Security and Context**: Ensure all agent interactions respect `ToolExecutionContext` settings (e.g., `allowed_base_path`).
- **Patterns Integration**: Start with sequential and hierarchical patterns, as they align closely with existing task decomposition.

This approach minimizes new dependencies, following the guidelines to prefer existing ones (e.g., no new packages unless necessary).

What specific patterns or use cases do you want to prioritize? Do you have preferences for how agents should communicate or handle failures?