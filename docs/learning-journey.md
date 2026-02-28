# Strands Agents & ASAP: The Homelab Learning Journey 🤖

This repository tracks the progression of building a local, open-source AI agent ecosystem that can autonomously run complex robotic physics simulations using the Strands Agents SDK and MIT's ASAP planner.

## Module 1: The Foundation (Hello Local AI)
**Goal:** Get a local AI agent running for free and understand the basic Agent Loop.

- [x] **Step 1: Spin up Local AI**
  - [x] Deploy Ollama as a Docker container on the homelab server.
  - [x] Pull a fast open-weights model: `docker exec -it <container_name> ollama run llama3`.
- [x] **Step 2: Install the Strands SDK**
  - [x] Create a Python virtual environment: `python -m venv strands_env`.
  - [x] Activate the environment and install dependencies: `pip install strands-agents strands-agents-tools`.
- [x] **Step 3: The "Hello World" Agent**
  - [x] Write a `hello_agent.py` script.
  - [x] Configure the Strands client to point to the local Ollama endpoint instead of AWS Bedrock.
  - [x] Run a simple prompt-response execution loop to verify connectivity.

## Module 2: The Hands (Custom Tools & Structured Output)
**Goal:** Teach the agent to interact with Python code and return predictable data formats.

- [ ] **Step 1: Custom Tool Creation**
  - [ ] Create a mock "robot controller" Python function (e.g., `move_arm(x, y, z)`) that simply prints its actions.
  - [ ] Wrap the function using the Strands `@tool` decorator.
- [ ] **Step 2: Tool Execution**
  - [ ] Register the tool with the Agent.
  - [ ] Prompt the agent to "move the arm to coordinates 10, 20, 30" and verify the tool executes.
- [ ] **Step 3: Structured Output**
  - [ ] Configure the agent to return its final summary strictly as a JSON object containing `{"action_taken": string, "success": boolean}`.

## Module 3: The Memory (State & Session Management)
**Goal:** Enable the agent to remember context across a multi-step conversation.

- [ ] **Step 1: Session Management**
  - [ ] Implement a basic File or SQLite Session Manager from the Strands SDK.
- [ ] **Step 2: Multi-Turn Conversation**
  - [ ] Prompt the agent: "I want to build a tower. Step 1 is placing block A."
  - [ ] In a separate prompt execution, ask: "What was step 1? Now for step 2, place block B on top."
  - [ ] Verify the agent recalls the history.
- [ ] **Step 3: Context Limits**
  - [ ] Implement a "Sliding Window" conversation manager to ensure the local LLM doesn't crash from context overflow during long chats.

## Module 4: The Team (Multi-Agent Basics)
**Goal:** Distribute complex tasks across specialized agents.

- [ ] **Step 1: Agents as Tools**
  - [ ] Create an `ExecutorAgent` with the `move_arm` tool.
  - [ ] Create a `PlannerAgent` that has no tools, but can call the `ExecutorAgent` as a tool to accomplish a goal.
- [ ] **Step 2: Agent2Agent (A2A)**
  - [ ] Prompt the `PlannerAgent` to "build a 3-block tower." Verify it breaks down the plan and hands off the steps to the `ExecutorAgent`.

## Module 5: The Supervisor (Human-in-the-Loop)
**Goal:** Add safety guardrails before executing "dangerous" code.

- [ ] **Step 1: Interrupts**
  - [ ] Configure the agent to pause execution *before* running the `move_arm` tool.
  - [ ] Prompt the user in the CLI to type "Y/N" to approve the movement.
  - [ ] Resume the agent's execution loop based on the human's input.

## Module 6: The Capstone (ASAP Physics Integration)
**Goal:** Replace the mock tools with the real MIT robotic assembly simulator.

- [ ] **Step 1: Clone the ASAP Environment**
  - [ ] Clone `https://github.com/yunshengtian/ASAP.git` and install its specific dependencies (`trimesh`, `ikpy`, etc.).
- [ ] **Step 2: Real Tooling**
  - [ ] Create a new tool: `plan_cad_assembly(assembly_name: str)`.
  - [ ] Use Python's `subprocess` to trigger the ASAP `run_seq_plan.py` script.
- [ ] **Step 3: Orchestration**
  - [ ] Have the `PlannerAgent` receive a request ("Build the beam_assembly"), trigger the ASAP tool, and have a `ReviewerAgent` summarize the generated logs into a markdown report.

## Module 7: Advanced Homelab Escalation (Optional)
**Goal:** Scale the system.

- [ ] **Step 1: Model Context Protocol (MCP)**
  - [ ] Connect a local file-system MCP server so the agent can discover new CAD files automatically.
- [ ] **Step 2: Custom Data**
  - [ ] Run the pipeline on a custom `.obj` downloaded from the internet.
