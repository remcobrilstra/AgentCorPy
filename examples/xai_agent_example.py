#!/usr/bin/env python3
"""
XAI Agent Example

This example demonstrates creating a simple agent using xAI's grok-4-fast model.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentcorp import Agent, XAIProvider


def create_xai_agent():
    """Create a simple agent using xAI's grok-4-fast model."""

    # Get xAI API key from environment
    api_key = os.getenv("XAI_API_KEY")
    if not api_key or api_key == "your_xai_api_key_here":
        print("❌ XAI_API_KEY not set in .env file. Please set your xAI API key.")
        return None

    # Create xAI provider with grok-4-fast model
    provider = XAIProvider(api_key=api_key, model="grok-4-fast")

    # Create agent
    agent = Agent(
        provider=provider,
        system_prompt="You are a helpful AI assistant powered by xAI's Grok model.",
        tool_names=[],  # No tools for this simple example
        context_settings={}
    )

    agent.name = "XAI Assistant"
    agent.description = "A simple agent using xAI's grok-4-fast model"

    print("✅ Created XAI agent with grok-4-fast model")
    return agent


def demonstrate_xai_agent():
    """Demonstrate the xAI agent with a simple conversation."""

    print("🚀 XAI Agent Demonstration")
    print("=" * 30)

    # Create the agent
    agent = create_xai_agent()
    if not agent:
        return

    # Simple conversation
    messages = [
        "Hello! Can you tell me about yourself?",
        "What's the weather like today?",
        "Explain quantum computing in simple terms."
    ]

    for i, message in enumerate(messages, 1):
        print(f"\n🤖 User: {message}")
        try:
            response = agent.chat(message)
            print(f"🧠 Grok: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Make sure your XAI_API_KEY is valid and you have internet connection.")

    print("\n✅ XAI agent demonstration completed!")


if __name__ == "__main__":
    demonstrate_xai_agent()