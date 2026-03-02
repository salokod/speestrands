import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning, module="strands")

sys.path.append(str(Path(__file__).parent.parent))

from mcp import stdio_client, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from strands import Agent
from strands.tools.mcp import MCPClient
from core.llm_factory import get_model

REPO_ROOT = Path(__file__).parent.parent
SERVER_PATH = REPO_ROOT / "mcp_server" / "server.py"

# Switch between stdio (local) and HTTP (Docker) via environment variable.
# Locally: python3 examples/robot_mcp_agent.py  → stdio, spawns server as subprocess
# In Docker: MCP_SERVER_URL is set → HTTP, connects to robot-mcp container
mcp_server_url = os.getenv("MCP_SERVER_URL")

if mcp_server_url:
    mcp_client = MCPClient(lambda: streamablehttp_client(mcp_server_url))
else:
    mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(command="python3", args=[str(SERVER_PATH)])
    ))

active_model = get_model()

with mcp_client:
    tools = mcp_client.list_tools_sync()

    print("\n--- Tools discovered from robot-tools MCP server ---")
    for t in tools:
        print(f"  · {t.tool_name}")
    print()

    agent = Agent(
        name="RobotMCPController",
        system_prompt="""You are a robotic arm controller connected via MCP.
        Check the arm status first, then carry out any movement instructions.
        Be brief — confirm what you did and the final coordinates. /no_think""",
        model=active_model,
        tools=tools,
    )

    print("--- Robot MCP Demo ---\n")
    agent("Check the arm status, then move it to X:3, Y:6, Z:9.", stream=False)
