#!/usr/bin/env python3
"""
Filesystem Tools Example

This example demonstrates how to use the new filesystem tools
with proper working directory restrictions for security.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentcorp import Agent, OpenAIProvider, AnthropicProvider, ToolExecutionContext, global_tool_registry


def demonstrate_filesystem_tools():
    """Demonstrate filesystem tools with different security contexts"""
    
    print("=== Filesystem Tools Demonstration ===\n")
    
    # Create a temporary working directory for this demo
    work_dir = Path(tempfile.mkdtemp(prefix="agentcorp_filesystem_demo_"))
    print(f"Demo working directory: {work_dir}")
    
    try:
        # Set up provider
        provider_name = os.getenv("PROVIDER", "openai")
        
        if provider_name == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("⚠️  OPENAI_API_KEY not set - using mock responses")
                return demonstrate_filesystem_tools_without_llm(work_dir)
            provider = OpenAIProvider(api_key, model="gpt-3.5-turbo")
        elif provider_name == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("⚠️  ANTHROPIC_API_KEY not set - using mock responses")
                return demonstrate_filesystem_tools_without_llm(work_dir)
            provider = AnthropicProvider(api_key)
        else:
            print("⚠️  No valid provider - using mock responses")
            return demonstrate_filesystem_tools_without_llm(work_dir)
        
        # Create agent with filesystem tools and working directory restriction
        agent = Agent(
            provider=provider,
            system_prompt="""You are a file management assistant with access to filesystem tools.
You can read, write, modify, and delete files, but only within the designated working directory.
Always be careful when performing file operations and provide clear feedback about what you've done.""",
            tool_names=["read_file", "write_file", "replace_in_file", "delete_file", "file_search", "grep_search"],  # All filesystem tools  # All filesystem tools
            context_settings={
                "workingdir": str(work_dir),  # Restrict operations to this directory
                "security_level": "filesystem_restricted"
            }
        )
        
        print("1. Creating a sample configuration file...")
        response = agent.chat(f"""
Create a configuration file called 'app_config.json' in the working directory with the following content:
{{
    "app_name": "AgentCorp Demo",
    "version": "1.0.0",
    "database": {{
        "host": "localhost",
        "port": 5432,
        "name": "demo_db"
    }},
    "features": {{
        "logging": true,
        "analytics": false
    }}
}}
""")
        print(f"Agent response: {response}\n")
        
        print("2. Reading the configuration file...")
        response = agent.chat("Read the contents of the app_config.json file and show me what's in it.")
        print(f"Agent response: {response}\n")
        
        print("3. Updating configuration...")
        response = agent.chat("""
Update the app_config.json file to:
1. Change the version to "1.1.0"
2. Enable analytics (set to true)
3. Add a new section called "cache" with "enabled": true and "ttl": 300
""")
        print(f"Agent response: {response}\n")
        
        print("4. Creating a log file...")
        response = agent.chat("""
Create a log file called 'app.log' with some sample log entries:
2024-01-01 10:00:00 INFO Application started
2024-01-01 10:01:00 INFO Database connection established
2024-01-01 10:02:00 WARN Cache miss for key 'user_123'
2024-01-01 10:03:00 ERROR Failed to process request: timeout
""")
        print(f"Agent response: {response}\n")
        
        print("5. Creating additional files for search demo...")
        response = agent.chat("""
Create the following files to demonstrate file search:
1. A Python script called 'main.py' with some basic code
2. A README.md file with project documentation
3. Create a 'src' directory and put a 'utils.py' file inside it
""")
        print(f"Agent response: {response}\n")
        
        print("6. Demonstrating file search...")
        response = agent.chat("Search for all Python files (*.py) in the working directory using file_search")
        print(f"Agent response: {response}\n")
        
        print("7. Search for configuration files...")
        response = agent.chat("Search for all JSON files using the pattern '*.json'")
        print(f"Agent response: {response}\n")
        
        print("8. Testing security restrictions...")
        response = agent.chat("Try to read the file C:\\Windows\\System32\\hosts (or /etc/hosts on Linux/Mac)")
        print(f"Agent response: {response}\n")
        
        print("9. File management summary...")
        response = agent.chat("Use file_search to find all files we've created, then list their purposes.")
        print(f"Agent response: {response}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        import shutil
        if work_dir.exists():
            shutil.rmtree(work_dir)
            print(f"Cleaned up demo directory: {work_dir}")


def demonstrate_filesystem_tools_without_llm(work_dir: Path):
    """Demonstrate filesystem tools directly without LLM interaction"""
    
    print("Demonstrating filesystem tools directly (without LLM)...\n")
    
    # Create a restricted context
    context = ToolExecutionContext(
        settings={"workingdir": str(work_dir)},
        agent_id="demo-agent",
        session_id="demo-session"
    )
    
    # Get tools
    write_tool = global_tool_registry.get_tool("write_file")
    read_tool = global_tool_registry.get_tool("read_file")
    replace_tool = global_tool_registry.get_tool("replace_in_file")
    delete_tool = global_tool_registry.get_tool("delete_file")
    search_tool = global_tool_registry.get_tool("file_search")
    grep_tool = global_tool_registry.get_tool("grep_search")
    
    try:
        # 1. Create a sample file
        print("1. Creating a sample file...")
        config_content = """{
    "app_name": "AgentCorp Demo",
    "version": "1.0.0",
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "demo_db"
    },
    "features": {
        "logging": true,
        "analytics": false
    }
}"""
        
        result = write_tool.execute(context, 
                                  file_path=str(work_dir / "app_config.json"),
                                  content=config_content)
        print(f"Write result: {result}")
        
        # 2. Read the file
        print("\n2. Reading the file...")
        result = read_tool.execute(context, file_path=str(work_dir / "app_config.json"))
        print(f"Read result:\n{result}")
        
        # 3. Replace some content
        print("\n3. Updating version number...")
        result = replace_tool.execute(context,
                                    file_path=str(work_dir / "app_config.json"),
                                    old_text='"version": "1.0.0"',
                                    new_text='"version": "1.1.0"')
        print(f"Replace result: {result}")
        
        # 4. Test security restriction
        print("\n4. Testing security restriction...")
        result = write_tool.execute(context,
                                  file_path="C:\\temp\\unauthorized.txt",
                                  content="This should fail")
        print(f"Unauthorized write result: {result}")
        
        # 5. Create another file
        print("\n5. Creating a log file...")
        log_content = """2024-01-01 10:00:00 INFO Application started
2024-01-01 10:01:00 INFO Database connection established
2024-01-01 10:02:00 WARN Cache miss for key 'user_123'
2024-01-01 10:03:00 ERROR Failed to process request: timeout"""
        
        result = write_tool.execute(context,
                                  file_path=str(work_dir / "app.log"),
                                  content=log_content)
        print(f"Log file creation result: {result}")
        
        # 5.1. Create additional files for search demo
        print("\n5.1. Creating additional files for search demo...")
        (work_dir / "src").mkdir(exist_ok=True)
        
        # Create some Python files
        write_tool.execute(context, file_path=str(work_dir / "main.py"), content="#!/usr/bin/env python3\nprint('Hello World')")
        write_tool.execute(context, file_path=str(work_dir / "src" / "utils.py"), content="def helper():\n    pass")
        write_tool.execute(context, file_path=str(work_dir / "README.md"), content="# Project README")
        print("Created additional demo files")
        
        # 5.2. Demonstrate file_search
        print("\n5.2. Testing file_search - find all Python files:")
        result = search_tool.execute(context, query="**/*.py")
        print(f"Python files: {result}")
        
        print("\n5.3. Testing file_search - find JSON files:")
        result = search_tool.execute(context, query="*.json")
        print(f"JSON files: {result}")
        
        print("\n5.4. Testing file_search - find all files in src directory:")
        result = search_tool.execute(context, query="src/**/*")
        print(f"Src directory files: {result}")
        
        # 5.5. Demonstrate grep_search
        print("\n5.5. Testing grep_search - find text patterns in files:")
        result = grep_tool.execute(context, query="#", include_pattern="**/*.py")
        print(f"Grep search for comments: {result}")
        
        print("\n5.6. Testing grep_search - regex search:")
        result = grep_tool.execute(context, query="def.*helper", include_pattern="**/*.py", is_regexp=True)
        print(f"Regex grep search: {result}")
        
        # 6. Show final directory contents
        print(f"\n6. Final directory contents:")
        for file_path in work_dir.glob("*"):
            print(f"  - {file_path.name}")
        
        print("\n✅ Filesystem tools demonstration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        import shutil
        if work_dir.exists():
            shutil.rmtree(work_dir)
            print(f"Cleaned up demo directory: {work_dir}")


def show_available_tools():
    """Show all available tools including the new filesystem tools"""
    print("=== Available Tools ===")
    
    tools = list(global_tool_registry.tools.keys())
    print(f"Total tools registered: {len(tools)}")
    
    for tool_name in sorted(tools):
        tool = global_tool_registry.get_tool(tool_name)
        print(f"  • {tool_name}: {tool.description}")
    
    print("\n📁 Filesystem tools are now available for secure file operations!")


if __name__ == "__main__":
    # Import tools to ensure they're registered
    import agentcorp.tools
    
    show_available_tools()
    print("\n" + "="*60 + "\n")
    demonstrate_filesystem_tools()