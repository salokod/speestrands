from strands import Agent
from strands.models import OllamaModel

# 1. Initialize the Ollama model
# We tell the SDK to use the 'llama3' model running on your local machine
# host is the url to your ollama server
ollama_model = OllamaModel(
    model_id="llama3",
    host="http://192.168.30.195:11434"
)

# 2. Initialize the Agent
# We pass the Ollama model to the agent, along with some basic instructions
agent = Agent(
    name="LocalHomelabAgentpyt",
    system_prompt="You are a helpful AI assistant running locally on a homelab server.",
    model=ollama_model
)

print(f"Agent '{agent.name}' initialized successfully!")

# 3. Test the connection
print("Sending a test prompt to Ollama...")
response = agent("Say hello and tell me what model you are.")
print(f"Response: {response}")