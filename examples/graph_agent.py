import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning, module="strands")

sys.path.append(str(Path(__file__).parent.parent))

from strands import Agent
from strands.multiagent import GraphBuilder
from core.llm_factory import get_model
from src.tools.robot_tools import move_arm

# --- Slice 2: The Three Agents ---
# Each agent has one job and knows nothing about the others.
# The Graph wires them together — the agents themselves don't.
#
# Compare to multi_agent.py where the planner knew about the executor
# and had to manually decide when to call it. Here, none of these
# agents know the others exist. The SDK handles the handoffs.

# Node 1: Planner — thinks, does not act
# No tools. Its only output is a clear, ordered plan in plain text.
# That text becomes the Executor's input automatically.
planner = Agent(
    name="Planner",
    system_prompt="""You are a robotic assembly planner. /no_think
    Given a goal, output a numbered list of arm movements required to complete it.
    Each step must specify exact X, Y, Z coordinates.
    Do not execute anything — only plan.""",
    model=get_model(),
)

# Node 2: Executor — acts, does not think
# Has move_arm but no planning logic. It receives the planner's output
# and executes each step in order. Brief confirmations only.
executor = Agent(
    name="Executor",
    system_prompt="""You are a robotic arm executor. /no_think
    You will receive a numbered plan. Execute each step in order using move_arm.
    After all steps are complete, output a single line per step: 'Step N: moved to X, Y, Z'.""",
    model=get_model(),
    tools=[move_arm],
)

# Node 3: Reviewer — summarises, does not act
# No tools. Receives the executor's output and writes a clean summary.
# This is the pattern we'll use in Module 6 to generate assembly reports.
reviewer = Agent(
    name="Reviewer",
    system_prompt="""You are an assembly reviewer. /no_think
    You will receive a log of completed arm movements.
    Write a short markdown summary: what was built, how many steps, final position.""",
    model=get_model(),
)

# --- Slice 3: Building the Graph ---
# GraphBuilder is a fluent builder — you chain calls to declare
# the structure, then call .build() to get a runnable graph.
#
# add_node(agent, "id")  — registers an agent as a named node
# add_edge("a", "b")     — declares that node "a" feeds into node "b"
# set_entry_point("id")  — declares which node receives the initial prompt
#
# The SDK uses the edges to determine execution order and automatically
# packages each node's output as context for the next node.
# You don't write any of that routing logic — it's all handled for you.

builder = GraphBuilder()

builder.add_node(planner, "planner")
builder.add_node(executor, "executor")
builder.add_node(reviewer, "reviewer")

builder.add_edge("planner", "executor")
builder.add_edge("executor", "reviewer")

builder.set_entry_point("planner")

graph = builder.build()

# --- Slice 4: The Demo ---
# One prompt into the graph. The SDK handles the rest:
#   1. Planner receives the prompt, outputs a movement plan
#   2. Executor receives the plan as context, executes each step
#   3. Reviewer receives the execution log, writes a summary
#
# result.results is a dict keyed by node id — you can inspect
# each node's output individually, not just the final result.

print("\n--- Graph Demo: Build a 3-block tower ---\n")

result = graph("Build a 3-block tower at X:0, Y:0, starting at Z:0 and stacking upward.  There are blocks at 1,0,0 and 2,0,0 and 3,0,0 to start.")

print("\n--- Planner output ---")
print(result.results["planner"].result)

print("\n--- Executor output ---")
print(result.results["executor"].result)

print("\n--- Reviewer summary ---")
print(result.results["reviewer"].result)
