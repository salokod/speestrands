import sys
from pathlib import Path

# Add the parent directory (repository root) to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from strands import Agent
from core.llm_factory import get_model

# 1. Get the configured model from our factory
active_model = get_model()

# 2. Initialize the Agent using whatever model the factory gave us
agent = Agent(
    name="LocalHomelabAgent",
    system_prompt="You are a helpful AI assistant running locally on a homelab server.",
    model=active_model,
)

print(f"Agent '{agent.name}' initialized successfully!")

# 3. Test the connection
print("Sending a test prompt...")
response = agent("Say hello and tell me what model you are.")
print(f"Response: {response}")
