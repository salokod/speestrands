import os
import sys
import uuid
import httpx
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from strands import Agent
from strands.tools.mcp import MCPClient
from strands.session import FileSessionManager
from strands.agent.conversation_manager import SlidingWindowConversationManager
from mcp.client.streamable_http import streamablehttp_client

from core.llm_factory import get_model

ASAP_SERVER_URL = os.getenv("ASAP_SERVER_URL", "http://localhost:8001/mcp")

SYSTEM_PROMPT = """
You are a robotic assembly planning assistant. You MUST follow these steps in order. Do not skip steps.

STEP 1: Call subdivide_assembly with assembly_id='00561' to ensure mesh quality before planning.
STEP 2: Call plan_cad_assembly with assembly_id='00561'.
STEP 3: If the result contains 'PLANNING FAILED', try again with max_gripper=5.
STEP 4: Report the final result including the sequence if successful.

Always subdivide before planning. More grippers help when parts fall during disassembly.
""".strip()

# Session memory: persists conversation history across runs so the agent
# can recall previous planning attempts and results.
SESSION_ID = os.getenv("AGENT_SESSION_ID", f"asap_{str(uuid.uuid4())[:8]}")
session_dir = Path(__file__).parent.parent / ".agent_sessions"
session_manager = FileSessionManager(
    session_id=SESSION_ID,
    storage_dir=str(session_dir),
)

print(f"[Agent] Session: {SESSION_ID} (stored in .agent_sessions/)")

def debug_handler(**kwargs):
    """Log every Strands event so we can see exactly what happens after each tool call."""
    if "init_event_loop" in kwargs:
        print("[Strands] Event loop initialized", flush=True)
    elif "start_event_loop" in kwargs:
        print("[Strands] Event loop cycle started", flush=True)
    elif "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        print(f"[Strands] Calling tool: {tool.get('name')} input={tool.get('input')}", flush=True)
    elif "data" in kwargs and kwargs["data"]:
        print(kwargs["data"], end="", flush=True)
    elif "force_stop" in kwargs:
        print(f"\n[Strands] Force stop: {kwargs.get('force_stop_reason')}", flush=True)
    elif "message" in kwargs:
        msg = kwargs["message"]
        role = msg.get("role", "?")
        stop = msg.get("stopReason") or msg.get("stop_reason")
        print(f"\n[Strands] Message complete — role={role} stop_reason={stop}", flush=True)


with MCPClient(lambda: streamablehttp_client(ASAP_SERVER_URL, sse_read_timeout=3600)) as mcp_client:
    tools = mcp_client.list_tools_sync()

    print("[Agent] Tools available:", [t.tool_name for t in tools])

    agent = Agent(
        model=get_model(),
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        session_manager=session_manager,
        conversation_manager=SlidingWindowConversationManager(
            window_size=20,
            per_turn=True,
            should_truncate_results=True,
        ),
        callback_handler=debug_handler,
    )

    print("[Agent] Starting planning task...")
    result = agent("Subdivide and plan the disassembly sequence for assembly 00561 following your instructions.")

    print("[Agent] Final result:")
    print(result)

# Explicitly unload the model now that the session is done.
# keep_alive=0 tells Ollama to release it from memory immediately.
ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
model_id = "qwen3:32b"
try:
    httpx.post(f"{ollama_host}/api/generate", json={"model": model_id, "keep_alive": 0}, timeout=10)
    print(f"[Agent] Model {model_id} unloaded from Ollama.")
except Exception:
    pass  # Best-effort — don't fail the script if unload doesn't work
