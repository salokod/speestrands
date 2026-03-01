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

### 6. Code Quality (Linting & Formatting)
This project uses [Ruff](https://docs.astral.sh/ruff/), an extremely fast Python linter and formatter, to maintain code quality and prevent syntax errors.

Before committing code, it is highly recommended to run Ruff from the root of the repository:

**To find and automatically fix syntax/import errors:**
```bash
ruff check --fix .
```

**To automatically format your code (spacing, quotes, etc.):**
```bash
ruff format .
```

---

## Examples

Each file in `examples/` builds on the previous one. Run them in order to follow the learning progression.

| File | Module | What it teaches |
|---|---|---|
| `hello_world.py` | 1 | Bare minimum agent — connect to a local Ollama model and get a response |
| `robot_agent.py` | 2 | Custom tools — wrap a Python function with `@tool` so the agent can call it |
| `structured_agent.py` | 2 | Structured output — force the agent to return a validated Pydantic object instead of plain text |
| `memory_agent.py` | 3 | Session memory — persist conversation history to disk so the agent remembers across prompts |
| `context_agent.py` | 3 | Context limits — explicitly control how many messages the model sees at once with `SlidingWindowConversationManager` |
| `streaming_agent.py` | 3 | Streaming — intercept text chunks and tool calls as they arrive via a callback handler |
| `multi_agent.py` | 4 | Agents as tools — wrap an `ExecutorAgent` with `@tool` so a `PlannerAgent` can delegate to it; demonstrates a full multi-agent chain: `PlannerAgent → executor_agent() → ExecutorAgent → move_arm()` |

## Key Concepts

**`core/llm_factory.py`** — Provider factory. All examples import `get_model()` from here instead of hardcoding a model. Set `LLM_PROVIDER=bedrock` to switch from local Ollama to AWS Claude without touching agent code.

**`src/tools/robot_tools.py`** — Shared mock tools (`move_arm`, `get_arm_status`) used across examples. These simulate a robotic arm and will be replaced with the real MIT ASAP simulator in Module 6.

**`FileSessionManager`** — Writes conversation history to `.agent_sessions/` on disk. The agent can pick up where it left off across separate script runs.

**`SlidingWindowConversationManager`** — Caps how many messages are loaded into the model's active context per call. Protects local models from context overflow on long conversations. Default window is 40; tune it down for smaller models.

**`callback_handler`** — A function you wire into the agent that fires on every streaming event. Use it to print text as it arrives, display tool calls in progress, or pipe output to a UI.

**Agents as Tools** — Wrap any agent function with `@tool` so a higher-level orchestrator can call it like any other tool. The orchestrator doesn't know or care that a full agent loop is running inside — it just sees a function with a name and a docstring.

---
*Follow along with the detailed progression in `docs/learning-journey.md`.*