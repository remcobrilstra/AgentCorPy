"""
Models configuration for AgentCorp framework
Contains model information for different providers including costs and context sizes.
Costs are in USD per million tokens.
"""

models = {
    "openai": {
        "gpt-3.5-turbo": {
            "input_cost": 1.5,  # USD per million input tokens
            "output_cost": 2.0,  # USD per million output tokens
            "context_size": 16385  # Maximum context tokens
        },
        "gpt-4": {
            "input_cost": 30.0,
            "output_cost": 60.0,
            "context_size": 8192
        },
        "gpt-4-turbo": {
            "input_cost": 10.0,
            "output_cost": 30.0,
            "context_size": 128000
        }
    },
    "anthropic": {
        "claude-3-haiku": {
            "input_cost": 0.25,
            "output_cost": 1.25,
            "context_size": 200000
        },
        "claude-3-sonnet": {
            "input_cost": 3.0,
            "output_cost": 15.0,
            "context_size": 200000
        },
        "claude-3-opus": {
            "input_cost": 15.0,
            "output_cost": 75.0,
            "context_size": 200000
        }
    },
    "xai": {
        "grok-4-fast-reasoning": {
            "input_cost": 0.20,  
            "output_cost": 0.50,
            "context_size": 2_000_000
        },
            "grok-code-fast-1": {
            "input_cost": 0.20, 
            "output_cost": 1.50,
            "context_size": 256_000
        }
    }
}


def get_model_info(provider: str, model: str) -> dict:
    """
    Get model information for a specific provider and model.

    Args:
        provider: The provider name (e.g., 'openai')
        model: The model name (e.g., 'gpt-3.5-turbo')

    Returns:
        dict: Model info with input_cost, output_cost, context_size

    Raises:
        ValueError: If provider or model not found
    """
    if provider not in models:
        raise ValueError(f"Provider '{provider}' not found")
    if model not in models[provider]:
        raise ValueError(f"Model '{model}' not found for provider '{provider}'")
    return models[provider][model]