#!/usr/bin/env python3
"""
Logging Example

This example demonstrates the AgentCorp logging framework.
Run with AGENTCORP_VERBOSE=true to see debug logs.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentcorp import Agent, OpenAIProvider, set_verbose_logging

def main():
    print("AgentCorp Logging Example")
    print("========================")

    # Enable verbose logging
    set_verbose_logging(True)
    print("Verbose logging enabled")

    # Create a simple agent (without API key for demo)
    try:
        provider = OpenAIProvider(api_key="demo-key")
        agent = Agent(provider=provider, system_prompt="You are a helpful assistant.")

        # Add a simple task
        print("\nAdding a task...")
        task_id = agent.add_task("Test task")

        # Update task status
        print("Updating task status...")
        agent.update_task(task_id, "completed", "Task completed successfully")

        print("\nLogging example completed!")

    except Exception as e:
        print(f"Demo completed (expected error without real API key): {e}")

if __name__ == "__main__":
    main()