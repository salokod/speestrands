import sys
from pathlib import Path
from pydantic import BaseModel, Field

# Setup path so we can import our custom modules
sys.path.append(str(Path(__file__).parent.parent))

from strands import Agent
from core.llm_factory import get_model
from src.tools.robot_tools import move_arm, get_arm_status

# 1. Define the Structured Output Schema using Pydantic
class RobotSummary(BaseModel):
    action_taken: str = Field(
        description="The name of the action the robot just performed (e.g., 'move_arm')."
    )
    success: bool = Field(
        description="Whether the action was completed successfully."
    )
    final_coordinates: list[float] = Field(
        description="The final [x, y, z] coordinates of the arm."
    )

# 2. Get the configured model from our factory
active_model = get_model()

# 3. Initialize the Agent with tools
agent = Agent(
    name="RobotController",
    system_prompt="""You are a robotic arm controller. Use your tools to fulfill the user's request. 
    When finished, you must summarize your final actions using the exact JSON structure requested.""",
    model=active_model,
    tools=[move_arm, get_arm_status]
)

print(f"Agent '{agent.name}' initialized. Testing Structured Output...\n")

# 4. Prompt the agent
prompt = "Please move the arm to X:5, Y:15, Z:25 and give me a summary."
print(f"User: {prompt}\n")

# 5. Call the agent, passing our Pydantic class to the 'structured_output_model' argument
response = agent(
    prompt,
    structured_output_model=RobotSummary
)

# 6. Extract the parsed object
# The .structured_output property contains an instance of our RobotSummary class!
structured_data = response.structured_output

print("\n--- Python Object Properties ---")
print(f"Action: {structured_data.action_taken}")
print(f"Success: {structured_data.success}")
print(f"Coordinates: {structured_data.final_coordinates}")

print("\n--- Raw JSON Dump ---")
# Because it's a Pydantic object, we can easily convert it back to a pure JSON string
print(structured_data.model_dump_json(indent=2))