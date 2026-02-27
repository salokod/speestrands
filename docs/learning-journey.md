# Strands Agents & ASAP: The Homelab Learning Journey 🤖

This repository tracks the progression of building a local, open-source AI agent ecosystem that can autonomously run complex robotic physics simulations using the Strands Agents SDK and MIT's ASAP planner.

## Module 1: Strands Agents Basics (The Brain)
**Goal:** Get a local AI agent running for free.

- [ ] **Step 1: Spin up Local AI**
  - [ ] Deploy Ollama as a Docker container on the homelab server.
  - [ ] Pull a fast open-weights model: `docker exec -it <container_name> ollama run llama3`.
- [ ] **Step 2: Install the Strands SDK**
  - [ ] Create a Python virtual environment: `python -m venv strands_env`.
  - [ ] Activate the environment and install dependencies: `pip install strands-agents strands-agents-tools`.
- [ ] **Step 3: The "Hello World" Agent**
  - [ ] Write a `hello_agent.py` script.
  - [ ] Configure the Strands client to point to the local Ollama endpoint instead of AWS Bedrock.
  - [ ] Provide a basic built-in tool (e.g., calculator) and test the execution loop.



## Module 2: ASAP Physics & CAD Setup (The Hands)
**Goal:** Run the MIT robotic assembly simulation using their provided CAD data.

- [ ] **Step 1: Clone the ASAP Environment**
  - [ ] Clone the repository: `git clone https://github.com/yunshengtian/ASAP.git`.
  - [ ] Create a separate Python environment for ASAP to avoid dependency conflicts.
  - [ ] Install required physics and geometry libraries: `trimesh`, `torch_geometric`, `ikpy`.
- [ ] **Step 2: Run the Example Data**
  - [ ] Navigate to the ASAP directory.
  - [ ] Run the sequence planner on the default dataset: `python plan_sequence/run_seq_plan.py --dir beam_assembly`.
  - [ ] Verify the output log generates step-by-step assembly instructions.
- [ ] **Step 3: Visualize the Output**
  - [ ] Run the included simulation viewer script on the generated log to see the 3D assembly process.



## Module 3: Integration (Giving the Brain the Hands)
**Goal:** Teach the Strands Agent how to control the ASAP planner.

- [ ] **Step 1: The `@tool` Wrapper**
  - [ ] Create a Python function `plan_cad_assembly(assembly_name: str)`.
  - [ ] Use Python's `subprocess` module within the function to trigger the ASAP `run_seq_plan.py` script.
  - [ ] Decorate the function with `@tool`.
- [ ] **Step 2: The Agent Prompt**
  - [ ] Instantiate a Strands Agent and register the new tool.
  - [ ] Define the prompt: *"You are a robotic manufacturing assistant. When asked to assemble a product, run the planning tool and summarize the first 3 steps from the output log."*
- [ ] **Step 3: Test the Pipeline**
  - [ ] Prompt the agent: *"Please figure out how to build the beam_assembly."*
  - [ ] Confirm the agent autonomously executes the ASAP script, reads the log, and outputs plain-English instructions.

## Module 4: Advanced Homelab Escalation (Optional)
**Goal:** Scale the system to handle custom CAD files and complex multi-agent reasoning.

- [ ] **Step 1: Custom Open-Source Data**
  - [ ] Download a free multi-part `.obj` or `.stl` model (e.g., from GrabCAD).
  - [ ] Format the files to match the ASAP directory structure and run a manual test.
- [ ] **Step 2: Model Context Protocol (MCP)**
  - [ ] Connect a local file-system MCP server to the Strands Agent.
  - [ ] Test prompting the agent to discover and process new CAD files dropped into a specific directory automatically.
- [ ] **Step 3: Multi-Agent Orchestration**
  - [ ] Implement the Agent-to-Agent (A2A) protocol.
  - [ ] Build **Agent A (The Engineer)** to handle ASAP processing.
  - [ ] Build **Agent B (The Reviewer)** to ingest Agent A's logs and generate a structured markdown report detailing assembly time and potential grasping failures.
