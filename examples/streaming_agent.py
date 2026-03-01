import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning, module="strands")

sys.path.append(str(Path(__file__).parent.parent))

from strands import Agent
from core.llm_factory import get_model
from src.tools.robot_tools import move_arm, get_arm_status

# --- The Callback Function ---
# The SDK calls this function repeatedly as the agent works.
# Each call carries a different event — a text chunk, a tool firing,
# a completion signal. We check which one arrived and react.
#
# This is the streaming version of what stream=False was hiding
# in earlier examples. Before, you waited in silence then got
# the full response at once. Now you see each piece as it arrives.

def stream_handler(**kwargs) -> None:
    # Text chunk from the model — print it immediately without a newline
    # so the fragments stitch together into readable sentences.
    if "data" in kwargs:
        print(kwargs["data"], end="", flush=True)

    # The agent is about to call a tool — show which one.
    if "current_tool_use" in kwargs:
        tool = kwargs["current_tool_use"]
        if tool.get("name"):
            print(f"\n[calling tool: {tool['name']}]\n", flush=True)

    # Stream finished — move to a new line.
    if "complete" in kwargs:
        print()


# --- The Agent ---
active_model = get_model()

agent = Agent(
    name="RobotController",
    system_prompt="""You are a helpful robotic arm controller.
    You have tools to move the arm and check its status.""",
    model=active_model,
    tools=[move_arm, get_arm_status],
    callback_handler=stream_handler,
)

# --- The Demo ---
# One prompt. The agent will think, call a tool, then respond.
# Your stream_handler fires for every step — you'll see the text
# arrive in fragments rather than all at once at the end.
print("\n--- Streaming demo ---\n")
agent("Move the arm to X:7, Y:3, Z:15 and tell me when it's done.")
