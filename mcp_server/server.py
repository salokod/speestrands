import sys
from pathlib import Path

# Add repo root to path so we can import from src/tools/
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

# --- Slice 1: The FastMCP Instance ---
# FastMCP is the high-level Python framework for building MCP servers.
# It's included in the mcp package you already have installed.
#
# The string you pass ("robot-tools") is the server's name — this is
# what shows up in MCP client logs and tool listings to identify
# which server a tool came from. In production this would be something
# descriptive like "acme-robot-controller-v2".
#
# This single line is equivalent to what the filesystem server does
# internally — it creates an MCP-compliant server ready to expose tools.

import os
_host = os.getenv("MCP_HOST", "127.0.0.1")
mcp = FastMCP("robot-tools", host=_host)

# --- Slice 2: Exposing the tools ---
# We import the raw implementations from src/tools/ and re-expose them
# using @mcp.tool(). The logic lives in one place — the MCP server is
# just a new front door to the same code.
#
# @mcp.tool() reads the function's:
#   - name       → becomes the tool identifier in the MCP protocol
#   - docstring  → becomes the tool description agents read to decide when to use it
#   - type hints → become the tool's input schema (auto-validated)
#   - return type → tells the client what format to expect back
#
# This is identical in spirit to how Strands' @tool decorator works —
# the docstring is the contract. A bad docstring here means the agent
# won't know when or how to call it.

from src.tools.robot_tools import move_arm as _move_arm
from src.tools.robot_tools import get_arm_status as _get_arm_status

@mcp.tool()
def move_arm(x: float, y: float, z: float) -> str:
    """
    Moves the robotic arm to the specified X, Y, and Z coordinates.
    Use this tool when you need to physically position the arm at a location.
    Example: move_arm(x=1.0, y=2.0, z=3.0)
    """
    return _move_arm(x, y, z)

@mcp.tool()
def get_arm_status() -> str:
    """
    Returns the current status and diagnostics of the robotic arm.
    Use this tool to check if the arm is online and operational before moving it.
    """
    return _get_arm_status()

# --- The entrypoint ---
# mcp.run() starts the server on stdio transport by default.
# This is what the MCPClient's subprocess will talk to.
# In production you'd pass transport="sse" or transport="streamable-http"
# and point it at a port — zero other changes needed.

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()
