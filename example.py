#!/usr/bin/env python3
"""
Example usage of the AgentCorp framework
"""

import os
from agentcorp import Agent, OpenAIProvider, AnthropicProvider, Tool, global_tool_registry, ToolExecutionContext

# Example tool with context
def get_weather(context: ToolExecutionContext, city: str) -> str:
    """Get the weather for a city"""
    # Use context to limit access or add settings
    allowed_cities = context.get_setting("allowed_cities", "").split(",") if context.get_setting("allowed_cities") else None

    if allowed_cities and city not in allowed_cities:
        return f"Access denied: {city} is not in the allowed cities list"

    # Mock implementation
    return f"The weather in {city} is sunny and 25°C (Agent: {context.agent_id})"

def main():
    # Choose provider - you need to set API keys
    provider_name = os.getenv("PROVIDER", "openai")

    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Please set OPENAI_API_KEY environment variable")
            return
        provider = OpenAIProvider(api_key, model="gpt-3.5-turbo")
    elif provider_name == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Please set ANTHROPIC_API_KEY environment variable")
            return
        provider = AnthropicProvider(api_key)
    else:
        print("Unsupported provider")
        return

    # Register tool in global registry
    weather_tool = Tool(
        name="get_weather",
        description="Get the current weather for a city",
        function=get_weather,
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "The city name"}
            },
            "required": ["city"]
        }
    )
    global_tool_registry.register_tool(weather_tool)

    # Create agent with specific tools and context settings
    agent = Agent(
        provider=provider,
        system_prompt="You are a helpful assistant that can use tools to answer questions.",
        tool_names=["get_weather"],  # Specify which tools this agent can use
        context_settings={
            "allowed_cities": "Paris,London,Tokyo",  # Example context setting
            "max_requests_per_hour": "10"
        }
    )

    # Add some tasks
    task1 = agent.add_task("Research weather patterns")
    task2 = agent.add_task("Analyze user queries")

    print("Agent created with tasks:", agent.get_tasks())

    # Chat with the agent
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit']:
            break

        response = agent.chat(user_input)
        print(f"Agent: {response}")

        # Update a task as completed
        agent.update_task(task2, "completed")

if __name__ == "__main__":
    main()