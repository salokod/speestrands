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

## Module 1.5: The Architecture (Modular Configuration)
**Goal:** Structure the project so the LLM provider (Ollama vs. AWS Bedrock) can be swapped out instantly using environment variables, keeping the agent logic provider-agnostic.

- [x] **Step 1: The Config Module**
  - [x] Create a `core/llm_factory.py` file.
  - [x] Write a function `get_model()` that reads an environment variable (e.g., `PROVIDER=ollama` or `PROVIDER=bedrock`).
  - [x] Return the correctly configured Model object (`OllamaModel` or `BedrockModel`).
- [x] **Step 2: Refactoring "Hello World"**
  - [x] Update `hello_world.py` to import and use the `get_model()` function instead of hardcoding Ollama.
- [x] **Step 3: Test the Swap**
  - [x] Run the code with `PROVIDER=ollama` to verify it still works locally.
  - [x] (Optional) Run the code with `PROVIDER=bedrock` to see the exact same code use AWS Claude.

## Module 2: The Hands (Custom Tools & Structured Output)
**Goal:** Teach the agent to interact with Python code and return predictable data formats.

- [x] **Step 1: Custom Tool Creation**
  - [x] Create a mock "robot controller" Python function (e.g., `move_arm(x, y, z)`) that simply prints its actions.
  - [x] Wrap the function using the Strands `@tool` decorator.
- [x] **Step 2: Tool Execution**
  - [x] Register the tool with the Agent.
  - [x] Prompt the agent to "move the arm to coordinates 10, 20, 30" and verify the tool executes.
- [x] **Step 3: Structured Output**
  - [x] Configure the agent to return its final summary strictly as a JSON object containing `{"action_taken": string, "success": boolean}`.

## Module 3: The Memory (State & Session Management)
**Goal:** Enable the agent to remember context across a multi-step conversation and stream responses in real-time.

- [x] **Step 1: Session Management**
  - [x] Implement `FileSessionManager` from the Strands SDK.
  - [x] Use Python's `uuid` module to generate dynamic, unique folders for each session.
  - [x] Suppress SDK UserWarnings (e.g., the `**kwargs` deprecation warning) to keep terminal logs clean.
- [x] **Step 2: Multi-Turn Conversation**
  - [x] Prompt the agent: "I want to build a tower. Step 1 is moving the arm to X:10, Y:10, Z:10."
  - [x] In a sequential prompt, ask: "What were the coordinates for Step 1?"
  - [x] Verify the agent recalls the history from the persisted session file.
- [x] **Step 3: Context Limits**
  - [x] Import and configure `SlidingWindowConversationManager` to cap the rolling context window.
  - [x] Understand the trade-off: older turns are dropped to prevent local LLM context overflow.
  - [x] Note the alternative: `NullConversationManager` for fully stateless (no history) agents.
- [x] **Step 4: Real-Time Streaming**
  - [x] Use a **callback handler** (`on_stream_event`) to print text chunks as the agent generates them.
  - [x] Understand the event types: lifecycle, model stream, tool, and multi-agent events.
  - [x] Contrast with `stream=False` (used in Step 2) — notice the difference in perceived responsiveness.

## Module 4: The Team (Multi-Agent Systems)
**Goal:** Distribute complex tasks across specialized agents using multiple coordination patterns.

- [x] **Step 1: Agents as Tools**
  - [x] Create an `ExecutorAgent` with the `move_arm` tool.
  - [x] Create a `PlannerAgent` that has no tools, but wraps `ExecutorAgent` as a callable tool.
  - [x] Prompt the `PlannerAgent` to "build a 3-block tower" and verify it delegates steps to `ExecutorAgent`.
- [x] **Step 2: Agent2Agent (A2A)**
  - [x] Explore how the `PlannerAgent` and `ExecutorAgent` exchange structured messages during the handoff.
  - [x] Observe the multi-agent events emitted in the stream (node execution, handoffs).
- [x] **Step 3: Graphs (DAG Workflows)**
  - [x] Define a 3-node pipeline: `Planner → Executor → Reviewer`.
  - [x] Wire the nodes using the SDK's Graph API so output from one node feeds the next.
  - [x] Run the graph with a single "Build the beam assembly" prompt and observe the structured handoffs.

## Module 4.5: The Protocol (MCP Tools)
**Goal:** Expose external capabilities to the agent using the Model Context Protocol — the SDK's standard for third-party tool integration.

- [x] **Step 1: Local Filesystem MCP Server**
  - [x] Install and run a local MCP filesystem server (e.g., `npx @modelcontextprotocol/server-filesystem`).
  - [x] Connect it to the agent using `MCPClient` from `strands.tools.mcp`.
- [x] **Step 2: Agent-Driven Discovery**
  - [x] Prompt the agent to list the contents of the `examples/` directory using only the MCP tools.
  - [x] Verify the agent discovers and reads files without any custom Python tool code.
- [x] **Step 3: Your Own MCP Server**
  - [x] Build `mcp_server/server.py` using FastMCP — expose `move_arm` and `get_arm_status` as MCP tools.
  - [x] Write `examples/robot_mcp_agent.py` — connect to the custom server via `stdio_client`.
  - [x] Verify the agent discovers tools at runtime and calls them through the MCP wire protocol.
  - [x] Observe `CallToolRequest` log lines from the server — confirms tool calls travel over MCP, not direct Python calls.

## Module 5: The Supervisor (Human-in-the-Loop)
**Goal:** Add safety guardrails using SDK Hooks before executing "dangerous" actions.

- [x] **Step 1: Lifecycle Hooks**
  - [x] Register a `before_tool_call` hook on the agent via `agent.add_hook()`.
  - [x] The SDK infers which lifecycle event to attach by reading the function's type hint (`BeforeToolCallEvent`).
  - [x] `event.tool_use["name"]` identifies the tool; `event.tool_use["input"]` exposes the arguments.
- [x] **Step 2: Human Approval Gate**
  - [x] Filter to `move_arm` only — let `get_arm_status` and other tools pass through unblocked.
  - [x] Print the planned coordinates and ask the operator to type y/n in the CLI.
  - [x] If "n": set `event.cancel_tool` with a message — the tool never runs; the agent receives the message as the tool result.
  - [x] If "y": return normally — execution continues unchanged.
  - [x] Verified: agent handles rejection gracefully and does not retry after "Do not retry." message.

## Module 6: The Capstone (Production-Grade ASAP Integration)
**Goal:** Replace the mock tools with the real MIT robotic assembly simulator and make the system look and feel production-ready — proper CLI, config, structured reports, and all previous modules working together.

- [ ] **Step 1: Clone the ASAP Environment**
  - [ ] Clone `https://github.com/yunshengtian/ASAP.git` and install its specific dependencies (`trimesh`, `ikpy`, etc.).
- [ ] **Step 2: Real Tooling**
  - [ ] Create a new tool: `plan_cad_assembly(assembly_name: str)`.
  - [ ] Use Python's `subprocess` to trigger the ASAP `run_seq_plan.py` script.
- [ ] **Step 3: Full Orchestration**
  - [ ] Wire up the Module 4 Graph: `PlannerAgent → ASAP ExecutorAgent → ReviewerAgent`.
  - [ ] Activate the Module 5 human approval gate before any `plan_cad_assembly` call.
  - [ ] Use the Module 4.5 MCP filesystem server so the `PlannerAgent` discovers assembly files automatically.
- [ ] **Step 4: Production Hardening**
  - [ ] Move all configuration (model, Ollama host, ASAP path) to a `.env` file loaded via `python-dotenv`.
  - [ ] Add a health check at startup — verify Ollama is reachable before the graph runs.
  - [ ] Build a proper CLI entrypoint using `argparse` or `typer`: `python run.py --assembly beam_assembly`.
  - [ ] Write the `ReviewerAgent` markdown summary to a timestamped file in `reports/` on every run.
  - [ ] Add structured Python `logging` throughout — no bare `print()` statements in production code.

## Module 7: The Lens (Observability with Langfuse)
**Goal:** Instrument the production pipeline with open-source observability so every agent run is traceable, evaluatable, and comparable — and swappable for Galileo or any other OpenTelemetry-compatible platform at work.

- [ ] **Step 1: Self-Host Langfuse**
  - [ ] Deploy Langfuse via Docker Compose on the homelab.
  - [ ] Verify the dashboard is accessible and the project API keys are generated.
- [ ] **Step 2: Instrument the Pipeline**
  - [ ] Connect the Strands agent pipeline to Langfuse via the OpenTelemetry exporter already in `requirements.txt`.
  - [ ] Run a full ASAP assembly and verify the trace appears in the Langfuse dashboard.
  - [ ] Inspect the trace: see every agent node, tool call, token count, and latency broken down.
- [ ] **Step 3: Evaluate**
  - [ ] Configure an LLM-as-a-judge evaluator in Langfuse to score the `ReviewerAgent`'s summaries.
  - [ ] Run 3 assemblies and compare scores across runs in the Langfuse experiments view.
- [ ] **Step 4: The Swap (Optional)**
  - [ ] Change the OpenTelemetry exporter endpoint to a Galileo endpoint.
  - [ ] Verify the same traces appear in Galileo with zero changes to agent code — this is the payoff of building on open standards.

## Module 8: Advanced Homelab Escalation (Optional)
**Goal:** Scale the system with real-world data end-to-end.

- [ ] **Step 1: Custom Data**
  - [ ] Download a custom `.obj` assembly file from the internet.
  - [ ] Use the MCP filesystem server so the `PlannerAgent` discovers it automatically — no hardcoded paths.
  - [ ] Run the full pipeline end-to-end: discovery → planning → ASAP execution → report → Langfuse trace.
