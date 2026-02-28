import sys
from pathlib import Path

# Add the parent directory (repository root) to the Python path
# This allows us to import from 'core' and 'src'
sys.path.append(str(Path(__file__).parent.parent))

from strands import Agent
from core.llm_factory import get_model
from src.tools.robot_tools import move_arm, get_arm_status

# 1. Get the configured model from our factory
active_model = get_model()

# 2. Initialize the Agent, but this time, give it tools!
agent = Agent(
    name="RobotController",
    system_prompt="""You are a helpful AI assistant that controls a robotic arm. 
    You have tools available to move the arm and check its status. 
    Required to translate your thought into english for the user to read.
    Always use the provided tools to interact with the robot. 
    If you move the arm, confirm the final coordinates with the user.""",
    model=active_model,
    tools=[move_arm, get_arm_status],  # <--- This is the magic line!
)

print(f"Agent '{agent.name}' initialized with tools successfully!")

# 3. Prompt the agent to do something that requires a tool
prompt = "Can you move the robot arm to coordinates X:10, Y:20, Z:30?"
print(f"User: {prompt}")

print("Agent is thinking and executing tools...")
response = agent(prompt)

print(f"\n\nAgent final response:{response}")
