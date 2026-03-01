import sys
import uuid
import warnings
from pathlib import Path

# Fix the internal SDK warnings cluttering the terminal
warnings.filterwarnings("ignore", category=UserWarning, module="strands")

# Setup path so we can import our custom modules
sys.path.append(str(Path(__file__).parent.parent))

from strands import Agent
from strands.session import FileSessionManager
from core.llm_factory import get_model
from src.tools.robot_tools import move_arm, get_arm_status

# 1. Generate a dynamic Session ID
# This creates a folder like '.agent_sessions/session_a1b2c3d4'
CURRENT_SESSION_ID = f"session_{str(uuid.uuid4())[:8]}"

# 2. Initialize the Session Manager
db_path = Path(__file__).parent.parent / ".agent_sessions"

session_manager = FileSessionManager(
    session_id=CURRENT_SESSION_ID,
    storage_dir=str(db_path)
)

print(f"Session database ready at: {db_path}/{CURRENT_SESSION_ID}\n")

# 3. Get the model
active_model = get_model()

# 4. Initialize the Agent, passing in the Session Manager
agent = Agent(
    name="RobotController",
    system_prompt="""You are a helpful robotic arm controller. 
    You have tools to move the arm and check its status.
    Required to translate your thought into english for the user to read.""",
    model=active_model,
    tools=[move_arm, get_arm_status],
    session_manager=session_manager 
)

print(f"Agent '{agent.name}' initialized with Memory!\n")
print(f"--- Starting Session: {CURRENT_SESSION_ID} ---\n")

# 5. First Prompt (The Setup)
prompt_1 = "I am going to build a tower. Step 1 is moving the arm to X:10, Y:10, Z:10. Please do that now."
print(f"User: {prompt_1}\n")

# The session_id is already bound inside the session_manager we passed to the Agent.
# We set stream=False here just so the terminal output is cleaner to read.
response_1 = agent(prompt_1, stream=False)
print(f"Agent: {response_1}\n")

print("-" * 50)

# 6. Second Prompt (The Memory Test)
# We are NOT providing the coordinates again. We are relying on the database.
prompt_2 = "What were the coordinates for Step 1? I forgot."
print(f"\nUser: {prompt_2}\n")

response_2 = agent(prompt_2, stream=False)
print(f"Agent: {response_2}\n")