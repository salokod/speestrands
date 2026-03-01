import sys
import uuid
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning, module="strands")

sys.path.append(str(Path(__file__).parent.parent))

from strands import Agent
from strands.session import FileSessionManager
from strands.agent.conversation_manager import SlidingWindowConversationManager
from core.llm_factory import get_model
from src.tools.robot_tools import move_arm, get_arm_status

# --- Slice 2: The Conversation Manager ---
# window_size=10 means: keep the last 10 messages in the rolling context.
# A "message" here is one entry in the conversation list — a user turn,
# an assistant turn, or a tool result each count as one message.
#
# The default (if you don't set this) is 40. That's fine for cloud models
# with 100k+ context windows, but a local 14B model has a much smaller
# window. Setting this explicitly protects your local model from overflow.
#
# When the window fills up, the OLDEST messages get dropped first.
# The agent doesn't "forget" — it just loses the earliest turns.
conversation_manager = SlidingWindowConversationManager(
    window_size=10,
    should_truncate_results=True,
)

# --- Slice 3: The Agent ---
# Two memory systems are working together here — they do different jobs:
#
#   FileSessionManager      → long-term storage (writes to disk, survives restarts)
#   SlidingWindowConversationManager → short-term working memory (what the model sees right now)
#
# FileSessionManager persists the FULL history to disk.
# SlidingWindowConversationManager controls how much of that history
# is loaded into the model's active context window per call.
#
# Analogy: FileSessionManager is your notebook. SlidingWindow is your desk.
# You can't fit the whole notebook on the desk — so you only keep the last
# few pages in front of you while you work.

CURRENT_SESSION_ID = f"session_{str(uuid.uuid4())[:8]}"
db_path = Path(__file__).parent.parent / ".agent_sessions"

session_manager = FileSessionManager(
    session_id=CURRENT_SESSION_ID,
    storage_dir=str(db_path)
)

active_model = get_model()

agent = Agent(
    name="RobotController",
    system_prompt="""You are a helpful robotic arm controller.
    You have tools to move the arm and check its status.""",
    model=active_model,
    tools=[move_arm, get_arm_status],
    session_manager=session_manager,
    conversation_manager=conversation_manager,
)

print(f"\n--- Session: {CURRENT_SESSION_ID} | Window size: 10 messages ---\n")

# --- Slice 4: The Demo ---
# Each tool-using exchange generates ~4 messages in the conversation list:
#   1. user message
#   2. assistant message (with tool_use block)
#   3. tool result message
#   4. assistant final response
#
# With window_size=10, the window fills after ~2 full exchanges.
# By the time we ask about Turn 1 on Turn 4, it will have slid out.
# Watch the message count printed before each call.

def run_turn(prompt: str) -> None:
    print(f"[messages in context: {len(agent.messages)}]")
    print(f"User: {prompt}\n")
    response = agent(prompt, stream=False)
    print(f"Agent: {response}\n")
    print("-" * 50 + "\n")

# Turn 1 — plant a specific fact early (this will slide out of context)
run_turn("This is Step 1 of my tower build. Move the arm to X:1, Y:1, Z:1.")

# Turn 2 — new action, pushes Turn 1 further back
run_turn("Good. Step 2: move the arm to X:5, Y:5, Z:5.")

# Turn 3 — another action, window is now full
run_turn("Step 3: move the arm to X:9, Y:9, Z:9.")

# Turn 4 — the memory test. Turn 1 should now be outside the window.
# The agent cannot recall it from active context — only from the session file.
run_turn("What were the exact coordinates I used for Step 1?")
