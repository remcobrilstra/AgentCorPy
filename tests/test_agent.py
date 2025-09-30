#!/usr/bin/env python3
"""
Test agent loading and prompt functionality
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentcorp.config import AgentConfig, load_agent_from_file
from agentcorp.prompt_utils import load_prompt, get_parameters


def test_agent_config_from_dict():
    """Test creating AgentConfig from dictionary with direct prompt"""
    try:
        config_dict = {
            "name": "TestAgent",
            "description": "A test agent",
            "model": "gpt-4",
            "provider": "openai",
            "system_prompt": "You are a test assistant.",
            "tools": ["read_file"],
            "context_settings": {"test": "value"}
        }

        config = AgentConfig.from_dict(config_dict)

        assert config.name == "TestAgent"
        assert config.system_prompt == "You are a test assistant."
        assert config.tools == ["filesys.read_file"]

        print("PASS AgentConfig from dict with direct prompt")
    except Exception as e:
        print(f"FAIL AgentConfig from dict with direct prompt: {e}")
        raise


def test_agent_config_from_dict_with_prompt_file():
    """Test creating AgentConfig from dictionary with prompt file reference"""
    try:
        config_dict = {
            "name": "TestAgent",
            "description": "A test agent",
            "model": "gpt-4",
            "provider": "openai",
            "system_prompt": {
                "file": "system_assistant",
                "params": {
                    "AGENT_NAME": "TestBot",
                    "SPECIALTY": "testing"
                }
            },
            "tools": ["read_file"],
            "context_settings": {"test": "value"}
        }

        config = AgentConfig.from_dict(config_dict)

        assert config.name == "TestAgent"
        assert "TestBot" in config.system_prompt
        assert "testing" in config.system_prompt
        assert "helpful AI assistant" in config.system_prompt

        print("PASS AgentConfig from dict with prompt file reference")
    except Exception as e:
        print(f"FAIL AgentConfig from dict with prompt file reference: {e}")
        raise


def test_agent_config_from_json_file():
    """Test loading AgentConfig from JSON file"""
    try:
        # Test with code_assistant.json (direct prompt)
        config = AgentConfig.from_json_file("agent_configs/code_assistant.json")

        assert config.name == "CodeAssistant"
        assert "coding assistant" in config.system_prompt.lower()
        assert config.tools == ["filesys.read_file"]

        print("PASS AgentConfig from JSON file")
    except Exception as e:
        print(f"FAIL AgentConfig from JSON file: {e}")
        raise


def test_agent_config_from_json_file_with_prompt_ref():
    """Test loading AgentConfig from JSON file with prompt reference"""
    try:
        # Test with data_analyzer.json (prompt file reference)
        config = AgentConfig.from_json_file("agent_configs/data_analyzer.json")

        assert config.name == "DataAnalyzer"
        assert "DataAnalyzer" in config.system_prompt
        assert "statistical and exploratory" in config.system_prompt
        assert "data analyst AI assistant" in config.system_prompt

        print("PASS AgentConfig from JSON file with prompt reference")
    except Exception as e:
        print(f"FAIL AgentConfig from JSON file with prompt reference: {e}")
        raise


def test_prompt_utils_load_prompt():
    """Test prompt_utils.load_prompt function"""
    try:
        # Test loading system_assistant with parameters
        result = load_prompt("system_assistant", AGENT_NAME="TestAgent", SPECIALTY="debugging")

        assert result["type"] == "system"
        assert "description" in result
        assert "TestAgent" in result["content"]
        assert "debugging" in result["content"]
        assert "helpful AI assistant" in result["content"]

        print("PASS prompt_utils.load_prompt")
    except Exception as e:
        print(f"FAIL prompt_utils.load_prompt: {e}")
        raise


def test_prompt_utils_get_parameters():
    """Test prompt_utils.get_parameters function"""
    try:
        # Test getting parameters from system_assistant
        params = get_parameters("system_assistant")

        assert "AGENT_NAME" in params
        assert "SPECIALTY" in params
        assert len(params) == 2

        print("PASS prompt_utils.get_parameters")
    except Exception as e:
        print(f"FAIL prompt_utils.get_parameters: {e}")
        raise


def test_prompt_utils_invalid_file():
    """Test prompt_utils error handling for invalid files"""
    try:
        try:
            load_prompt("nonexistent_file")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected

        try:
            get_parameters("nonexistent_file")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected

        print("PASS prompt_utils error handling")
    except Exception as e:
        print(f"FAIL prompt_utils error handling: {e}")
        raise


def test_agent_config_invalid_prompt_ref():
    """Test AgentConfig error handling for invalid prompt references"""
    try:
        config_dict = {
            "name": "TestAgent",
            "model": "gpt-4",
            "provider": "openai",
            "system_prompt": {
                "file": "nonexistent_file",
                "params": {}
            },
            "tools": []
        }

        try:
            config = AgentConfig.from_dict(config_dict)
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass  # Expected

        print("PASS AgentConfig invalid prompt reference handling")
    except Exception as e:
        print(f"FAIL AgentConfig invalid prompt reference handling: {e}")
        raise


if __name__ == "__main__":
    print("Running agent and prompt tests...\n")

    try:
        test_agent_config_from_dict()
        test_agent_config_from_dict_with_prompt_file()
        test_agent_config_from_json_file()
        test_agent_config_from_json_file_with_prompt_ref()
        test_prompt_utils_load_prompt()
        test_prompt_utils_get_parameters()
        test_prompt_utils_invalid_file()
        test_agent_config_invalid_prompt_ref()

        print("PASS All agent and prompt tests passed!")

    except Exception as e:
        print(f"\nFAIL Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)