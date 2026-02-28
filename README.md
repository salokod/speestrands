# Strands Agents Learning Journey

Welcome to the Strands Agents learning repository! This project tracks my journey in building a local, open-source AI agent ecosystem to run complex robotic physics simulations using the Strands Agents SDK and MIT's ASAP planner.

## Getting Started

If you want to run this code on your own machine, you'll need to set up a Python Virtual Environment. This ensures that the dependencies for this project don't conflict with other Python projects on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/speestrands.git
cd speestrands
```

### 2. Create a Virtual Environment
Create a localized environment named `strands_env`:
```bash
python3 -m venv strands_env
```

### 3. Activate the Environment
You must activate the environment every time you open a new terminal to work on this project.

**On macOS/Linux:**
```bash
source strands_env/bin/activate
```
*(You should see `(strands_env)` appear at the beginning of your terminal prompt).*

**On Windows:**
```cmd
strands_env\Scripts\activate
```

### 4. Install Dependencies
Once activated, install the required packages:
```bash
pip install -r requirements.txt
```

### 5. Running the Agents
By default, the agents in this repository are configured to run completely locally using **Ollama** as the model provider. 

To run a basic test:
```bash
python3 examples/hello_world.py
```

#### Swapping Model Providers
This project uses a factory pattern (`core/llm_factory.py`) to easily swap between local models and cloud providers without changing the agent logic. You can control which model is used by setting the `LLM_PROVIDER` environment variable.

**Run with local Ollama (Default):**
```bash
LLM_PROVIDER=ollama python3 examples/hello_world.py
```

**Run with AWS Bedrock (Claude 3.5 Sonnet):**
*(Requires valid AWS credentials in `~/.aws/credentials`)*
```bash
LLM_PROVIDER=bedrock python3 examples/hello_world.py
```

---
*Follow along with the detailed progression in `docs/learning-journey.md`.*