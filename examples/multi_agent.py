import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning, module="strands")

sys.path.append(str(Path(__file__).parent.parent))

from strands import Agent, tool
from core.llm_factory import get_model
from src.tools.robot_tools import move_arm, get_arm_status

# --- Slice 2: The ExecutorAgent ---
# This agent's only job is physical execution — it knows how to operate
# the arm and nothing else. It has no idea a planner exists above it.
#
# The @tool decorator is the key move here. It turns the whole function
# into something the PlannerAgent can call like any other tool.
# The docstring is critical — that's what the PlannerAgent reads to
# understand what this tool does and when to use it.

@tool
def executor_agent(instruction: str) -> str:
    """
    Executes a single robotic arm instruction.
    Use this tool to physically move the arm or check its status.
    Pass one clear instruction at a time, e.g. 'Move the arm to X:1, Y:1, Z:1'.
    """
    agent = Agent(
        name="ExecutorAgent",
        system_prompt="""You are a robotic arm executor. /no_think
        You receive one instruction at a time and carry it out using your tools.
        Be brief — confirm what you did and the final coordinates, nothing more.""",
        model=get_model(),
        tools=[move_arm, get_arm_status],
    )
    return str(agent(instruction, stream=False))

# --- Slice 3: The PlannerAgent ---
# The planner's job is thinking, not doing. It has no move_arm tool,
# no get_arm_status tool — it cannot touch the hardware directly.
# Its only capability is calling executor_agent, which it treats
# as a black box that "does the physical work."
#
# This is the separation of concerns in action:
#   - Planner knows WHAT needs to happen and in what order
#   - Executor knows HOW to make it happen
#   - Neither knows the other's internals

planner = Agent(
    name="PlannerAgent",
    system_prompt="""You are a robotic assembly planner. /no_think
    You break down high-level goals into a sequence of individual arm movements.
    You do not move the arm yourself — you delegate each step to your executor_agent tool.
    Execute all steps one at a time and wait for confirmation before proceeding to the next.""",
    model=get_model(),
    tools=[executor_agent],
)

# --- Slice 4: The Demo ---
# One prompt to the planner. We never mention executor_agent or move_arm.
# The planner reads the goal, breaks it into steps, and calls executor_agent
# once per step. executor_agent spins up its own agent loop, calls move_arm,
# and returns a confirmation. The planner reads that confirmation and moves
# to the next step.
#
# The full call chain for each block:
#   planner → executor_agent() → ExecutorAgent → move_arm()
#
# Watch the output — you should see three separate executor calls,
# one for each block in the tower.

print("\n--- Multi-Agent Demo: Build a 3-block tower ---\n")
response = planner(
    "Build a 3-block tower. Place block 1 at X:0, Y:0, Z:0. "
    "Block 2 at X:0, Y:0, Z:1. Block 3 at X:0, Y:0, Z:2.",
    stream=False
)
print(f"\nPlanner summary:\n{response}")
