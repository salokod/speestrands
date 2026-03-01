import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning, module="strands")

sys.path.append(str(Path(__file__).parent.parent))

from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient
from core.llm_factory import get_model

# --- The MCP Client ---
# The only difference from mcp_agent.py is what we point at.
# Instead of npx running the Anthropic filesystem server,
# we run our own server.py with python3.
#
# From the MCPClient's perspective, it doesn't matter what's on the
# other end — it just speaks MCP over stdio. Our server, the filesystem
# server, an AWS server — all identical from here.
#
# REPO_ROOT lets us use a relative path to server.py regardless of
# where the script is run from.

REPO_ROOT = Path(__file__).parent.parent
SERVER_PATH = REPO_ROOT / "mcp_server" / "server.py"

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="python3",
        args=[str(SERVER_PATH)]
    )
))

active_model = get_model()

with mcp_client:
    tools = mcp_client.list_tools_sync()

    # Print what the server exposed — this is what the agent sees
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
