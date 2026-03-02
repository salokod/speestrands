import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from strands import Agent
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

from core.llm_factory import get_model

ASAP_SERVER_URL = os.getenv("ASAP_SERVER_URL", "http://localhost:8001/mcp")

with MCPClient(lambda: streamablehttp_client(ASAP_SERVER_URL)) as mcp_client:
    tools = mcp_client.list_tools_sync()

    agent = Agent(
        model=get_model(),
        tools=tools,
    )

    result = agent(
        "Plan the disassembly sequence for assembly 00000. "
        "Use the plan_cad_assembly tool and report back what you find."
    )

    print(result)
