#!/usr/bin/env python3
"""
Complex Task Agent Example

This example demonstrates an agent that can decompose complex tasks into subtasks
and execute them sequentially until the initial query is resolved.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path to import agentcorp
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentcorp import Agent, OpenAIProvider, AnthropicProvider


def create_task_execution_function(task_description: str):
    """Create a simple execution function for demonstration"""
    def execute_task(agent: Agent, task):
        print(f"Executing task: {task.description}")

        # Simulate some work by asking the agent to process this subtask
        prompt = f"Process this subtask and provide a brief result: {task.description}"
        result = agent.chat(prompt)
        print(f"Task result: {result[:100]}...")
        return result

    return execute_task


def setup_complex_task_agent():
    """Set up an agent capable of handling complex tasks"""

    # Choose provider based on environment
    provider_env = os.getenv("PROVIDER", "openai").lower()

    if provider_env == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")
        provider = AnthropicProvider(api_key=api_key)
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
        provider = OpenAIProvider(api_key=api_key)

    # Create agent with system prompt for task management
    system_prompt = """
    You are an intelligent task management agent. You can break down complex problems
    into manageable steps and execute them systematically. When faced with a complex
    task, analyze it thoroughly and provide clear, actionable subtasks.
    """

    agent = Agent(provider=provider, system_prompt=system_prompt)

    return agent


def demonstrate_complex_task_handling():
    """Demonstrate the complex task handling capabilities"""

    print("=== Complex Task Agent Example ===\n")

    agent = setup_complex_task_agent()

    # Example 1: Simple query (should not be decomposed)
    print("1. Testing simple query:")
    simple_query = "What is the capital of France?"
    print(f"Query: {simple_query}")
    response = agent.handle_complex_query(simple_query)
    print(f"Response: {response}\n")

    # Example 2: Complex task (should be decomposed)
    print("2. Testing complex task:")
    complex_query = "Plan a week-long trip to Japan including flights, accommodation, itinerary, and budget"
    print(f"Query: {complex_query}")
    response = agent.handle_complex_query(complex_query)
    print(f"Response: {response}\n")

    # Example 3: Manual task decomposition and execution
    print("3. Manual task decomposition:")
    task_id = agent.decompose_task("Write a research paper on AI ethics")
    print(f"Created complex task with ID: {task_id}")

    # Show the decomposed tasks
    task = agent.task_manager.get_task(task_id)
    print(f"Main task: {task.description}")
    print("Subtasks:")
    for i, subtask in enumerate(task.subtasks, 1):
        print(f"  {i}. {subtask.description}")

    # Execute the tasks sequentially
    print("\nExecuting tasks sequentially...")
    result = agent.execute_task_sequentially(task_id)
    print(f"Final result: {result[:200]}...\n")

    # Show task status
    print("4. Task status overview:")
    tasks = agent.get_tasks()
    print(f"Pending tasks: {len(tasks['pending'])}")
    print(f"In-progress tasks: {len(tasks['in_progress'])}")
    print(f"Completed tasks: {len(tasks['completed'])}")


def demonstrate_custom_execution_functions():
    """Demonstrate using custom execution functions for tasks"""

    print("=== Custom Execution Functions Example ===\n")

    agent = setup_complex_task_agent()

    # Create a complex task with custom execution functions
    main_task_id = agent.add_complex_task(
        "Analyze customer feedback data",
        [
            "Collect customer feedback from multiple sources",
            "Categorize feedback by sentiment and topic",
            "Generate summary report with insights",
            "Create action items based on findings"
        ]
    )

    # Set custom execution functions for subtasks
    main_task = agent.task_manager.get_task(main_task_id)
    for subtask in main_task.subtasks:
        subtask.set_execution_function(create_task_execution_function(subtask.description))

    print("Created complex task with custom execution functions:")
    print(f"Main task: {main_task.description}")
    for i, subtask in enumerate(main_task.subtasks, 1):
        print(f"  {i}. {subtask.description}")

    # Execute with custom functions
    print("\nExecuting with custom functions...")
    result = agent.execute_task_sequentially(main_task_id)
    print("Execution completed.\n")


if __name__ == "__main__":
    try:
        demonstrate_complex_task_handling()
        demonstrate_custom_execution_functions()
        print("=== All examples completed successfully! ===")
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure you have set the appropriate API key environment variables:")
        print("- OPENAI_API_KEY for OpenAI")
        print("- ANTHROPIC_API_KEY for Anthropic")
        print("- Set PROVIDER=anthropic to use Anthropic instead of OpenAI")