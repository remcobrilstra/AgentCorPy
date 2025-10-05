#!/usr/bin/env python3
"""
Chat with Code Assistant Agent

This script allows you to have an interactive chat session with the Code Assistant agent.
Before starting, you'll be asked to specify a working directory for the agent.

The agent is configured with file reading capabilities to help with coding tasks.

Supported providers: OpenAI, Anthropic, xAI (set PROVIDER environment variable)
Make sure to set the appropriate API key environment variable (e.g., OPENAI_API_KEY)
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentcorp import load_agent_from_file
os.environ["AGENTCORP_VERBOSE"] = "true"

def main():
    print("🤖 Chat with Assistant Agent")
    print("=" * 40)

    try:
        # Load the code assistant agent
        config_path = Path(__file__).parent.parent / "agent_configs" / "researcher_agent.json"
        agent = load_agent_from_file(str(config_path))


        print(f"✅ Loaded agent: {agent.name}")
        print(f"   Description: {agent.description}")
        print(f"   Model: {agent.provider.model}")
        print(f"   Tools: {list(agent.tools.keys())}")
        print("\n💬 Chat session started. Type 'quit' or 'exit' to end the conversation.\n")

        # Chat loop
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break

            if not user_input:
                continue

            try:
                # Get response from agent
                response = agent.handle_complex_query(user_input)
                print(f"Agent: {response}\n")

                # token usage and cost
                total_cost = agent.memory.get_total_cost()
                total_tokens = agent.memory.get_total_tokens_used()
                print(f"💰 Total Cost: ${total_cost:.6f} | Total Tokens: {total_tokens}")
                

            except Exception as e:
                print(f"❌ Error: {e}\n")

    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        print("Make sure you have set the appropriate API key environment variable.")


if __name__ == "__main__":
    main()