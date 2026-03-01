import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning, module="strands")

sys.path.append(str(Path(__file__).parent.parent))

from mcp import stdio_client, StdioServerParameters
from strands import Agent
from strands.tools.mcp import MCPClient
from core.llm_factory import get_model

# --- Slice 2: The MCPClient ---
# MCPClient takes a lambda — a factory function that creates the connection.
# It's a lambda (not a direct call) because the client needs to control
# WHEN the connection opens and closes, not you. It calls the lambda
# itself at the right moment in the lifecycle.
#
# StdioServerParameters describes the subprocess to spawn:
#   command: the executable to run  ("npx")
#   args:    the arguments to pass
#     "-y"   → auto-confirm the npx install prompt, no interactive Y/N
#     "@modelcontextprotocol/server-filesystem" → the MCP server package
#     str(REPO_ROOT) → the directory the server is allowed to read/write
#
# REPO_ROOT points at the root of this repo — the server can only see
# files inside it. This is MCP's built-in safety boundary. You can't
# accidentally expose your home directory or system files.

REPO_ROOT = Path(__file__).parent.parent

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", str(REPO_ROOT)]
    )
))

# --- Slice 3: The Agent inside a context manager ---
# This is the twist compared to every previous example.
#
# The MCPClient must be used as a context manager (with statement).
# This guarantees the subprocess lifecycle:
#   - entering the 'with' block → npx starts, MCP handshake happens
#   - exiting the 'with' block  → npx is killed cleanly, no orphan processes
#
# Without the context manager, the subprocess could keep running after
# your Python script exits, or the connection could be in an undefined
# state when you try to use it.
#
# In Python, 'with X as y' calls X.__enter__() on the way in and
# X.__exit__() on the way out — even if an exception is raised.
# That's exactly the guarantee we need for a subprocess connection.
#
# Notice: mcp_client goes directly into tools=[] just like move_arm did.
# The Agent doesn't know or care that it's an MCP connection — it just
# sees a ToolProvider with a list of available tools.

active_model = get_model()

with mcp_client:
    # list_tools_sync() asks the MCP server "what tools do you have?"
    # and returns them as a plain list. We pass that list to the Agent
    # rather than the client itself — the context manager already started
    # the session, so passing mcp_client directly would try to start it again.
    tools = mcp_client.list_tools_sync()

    agent = Agent(
        name="FilesystemExplorer",
        system_prompt="""You are a helpful assistant that can explore the filesystem.
        When asked about files or directories, use your tools to look them up directly
        rather than guessing. Be concise and specific in your responses. /no_think""",
        model=active_model,
        tools=tools,
    )

    print("\n--- MCP Demo ---\n")

    # Prompt 1: Discovery
    # The agent has never seen this repo. It will use the MCP list_directory
    # tool to explore it — no hardcoded paths, no custom tool code from us.
    print("Prompt 1: What Python files are in the examples/ directory?\n")
    agent("List all the Python files in the examples/ directory.", stream=False)

    print("\n" + "-" * 50 + "\n")

    # Prompt 2: Reading
    # The agent reads an actual file in the repo using the MCP read_file tool.
    # It can summarise code it has never been shown — discovered and read at runtime.
    print("Prompt 2: What does hello_world.py do?\n")
    agent("Read the file examples/hello_world.py and explain what it does in 2 sentences.", stream=False)
