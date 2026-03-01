import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning, module="strands")

sys.path.append(str(Path(__file__).parent.parent))

from strands import Agent
from strands.hooks import BeforeToolCallEvent
from core.llm_factory import get_model
from src.tools.robot_tools import move_arm, get_arm_status

# --- The Hook Function ---
# The type hint (BeforeToolCallEvent) is how the SDK knows when to fire this.
#
# Slice 2 adds the approval gate:
#   1. Return immediately if it's not move_arm — we don't care about other tools
#   2. Print the planned coordinates so the human can see exactly what's proposed
#   3. Ask y/n via input() — this pauses the entire agent loop and waits
#   4. If "n": set event.cancel_tool — the tool never runs, the agent gets
#      an error message back and can decide what to do next
#   5. If "y": just return — execution continues normally
#
# event.cancel_tool can be a string (your message) or True (SDK default message).
# The agent sees that message as the tool's result and responds accordingly.


def approval_hook(event: BeforeToolCallEvent) -> None:
    tool_name = event.tool_use["name"]

    # Only gate move_arm — let get_arm_status through without asking
    if tool_name != "move_arm":
        return

    args = event.tool_use["input"]
    print("\n" + "=" * 50)
    print("  APPROVAL REQUIRED")
    print(f"  Tool:   {tool_name}")
    print(f"  X: {args.get('x')}  Y: {args.get('y')}  Z: {args.get('z')}")
    print("=" * 50)

    answer = input("  Approve this move? (y/n): ").strip().lower()

    if answer != "y":
        print("[HOOK] Move blocked by operator.\n")
        event.cancel_tool = "Move rejected by human operator. Do not retry."
    else:
        print("[HOOK] Move approved. Executing...\n")


# --- Slice 2: Registering the Hook ---
# agent.add_hook() takes any function whose first argument is typed
# as a hook event. The SDK infers "attach this to BeforeToolCallEvent"
# purely from the type hint — no decorator, no config needed.
#
# The hook fires for EVERY tool call, not just move_arm.
# In Slice 2 we'll filter by name inside the function.

active_model = get_model()

agent = Agent(
    name="HITLAgent",
    system_prompt="""You are a robotic arm controller.
    Check the arm status first, then carry out movement instructions.
    Be brief. /no_think""",
    model=active_model,
    tools=[move_arm, get_arm_status],
)

agent.add_hook(approval_hook)

# --- Run ---
print("--- HITL Agent Demo ---")
print("You will be asked to approve the move_arm call before it executes.")
print("Try typing 'n' first to see the block, then run again and type 'y'.\n")
agent("Check the arm status, then move it to X:1, Y:2, Z:3.", stream=False)
