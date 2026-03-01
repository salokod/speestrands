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

## Module 6: The Capstone (Containerize Everything + ASAP)
**Goal:** Move the entire project off the local venv and into Docker. Each concern gets its own container — agent, robot MCP server, ASAP planner. A peer should be able to clone the repo and run `docker-compose up` with no other setup. Then add ASAP as the third container, completing the real pipeline.

> **Why Docker first:** ASAP requires compiling a C++ physics binding. Doing that inside a Dockerfile means it compiles once at build time and never again — no local toolchain required for you or your peers. The Docker image becomes the artifact.

- [ ] **Step 1: Containerize the Agent**
  - [ ] Write `docker/agent/Dockerfile` — Python base image, copy `requirements.txt`, install deps, copy source.
  - [ ] Write `docker-compose.yml` with a single `agent` service — verify all existing examples still run inside the container.
  - [ ] Configure Ollama connectivity: use `host.docker.internal:11434` to reach Ollama running on the host machine.
  - [ ] Move `LLM_PROVIDER`, Ollama host, and other config into a `.env` file — `docker-compose` picks it up automatically.

- [ ] **Step 2: Containerize the Robot MCP Server**
  - [ ] Write `docker/robot-mcp/Dockerfile` — same Python base, just the MCP server deps.
  - [ ] Switch `mcp_server/server.py` from stdio transport to HTTP: `mcp.run(transport="streamable-http", port=8000)`.
  - [ ] Add `robot-mcp` service to `docker-compose.yml` on an internal Docker network.
  - [ ] Update agent examples to use `streamablehttp_client` instead of `stdio_client` — one line change.
  - [ ] Verify `robot_mcp_agent.py` still works end-to-end, now over HTTP between containers.

- [ ] **Step 3: ASAP Container**
  - [ ] Write `docker/asap/Dockerfile` — clone ASAP, install system build tools, compile C++ binding at build time.
  - [ ] Add a FastMCP HTTP server (`mcp_server/asap_server.py`) that exposes `plan_cad_assembly(assembly_dir: str)`.
  - [ ] Add `asap` service to `docker-compose.yml`, mount an `assemblies/` volume for `.obj` input files.
  - [ ] **Tool:** Install [MeshLab](https://www.meshlab.net) or [Blender](https://www.blender.org/download/) (`brew install --cask blender`) to inspect `.obj` files before feeding them to ASAP.
  - [ ] Run ASAP manually inside the container first: `docker exec -it asap python run_seq_plan.py --dir assembly_examples/ball` — understand the output before the agent touches it.

- [ ] **Step 4: Full Pipeline**
  - [ ] Wire `GraphBuilder`: `PlannerAgent → ASAPExecutorAgent → ReviewerAgent`.
  - [ ] `PlannerAgent`: discovers `.obj` files via the robot MCP server's filesystem tools, picks an assembly.
  - [ ] `ASAPExecutorAgent`: calls `plan_cad_assembly` on the ASAP MCP server, returns raw planner output.
  - [ ] `ReviewerAgent`: summarizes into a human-readable markdown report, writes to `reports/` with a timestamp.
  - [ ] Activate the Module 5 hook — human approval required before `plan_cad_assembly` executes.
  - [ ] Verify full run: `docker-compose up` → one prompt → plan runs → report written → `docker-compose down`.

## Module 7: The Lens (Observability with Langfuse)
**Goal:** Instrument the pipeline with open-source observability so every agent run is traceable and evaluatable. Langfuse is the closest open-source equivalent to Galileo — built on OpenTelemetry, so swapping to Galileo or any other platform at work is an endpoint change, not a code change.

- [ ] **Step 1: Self-Host Langfuse**
  - [ ] Deploy Langfuse via Docker Compose on the homelab server.
  - [ ] Verify the dashboard is accessible and generate project API keys.
- [ ] **Step 2: Instrument the Pipeline**
  - [ ] Set the OpenTelemetry exporter endpoint in `.env` to point at your Langfuse instance.
  - [ ] Run a full ASAP assembly and verify the trace appears in the dashboard.
  - [ ] Inspect the trace: every agent node, tool call, token count, and latency — broken down.
- [ ] **Step 3: Evaluate**
  - [ ] Configure an LLM-as-a-judge evaluator in Langfuse to score `ReviewerAgent` summaries.
  - [ ] Run 3 different assemblies, compare scores across runs in the experiments view.
- [ ] **Step 4: The Swap (IRL Reference)**
  - [ ] Change the OpenTelemetry exporter endpoint to a Galileo (or other platform) endpoint.
  - [ ] Verify the same traces appear — zero agent code changes. This is the payoff of building on open standards.

## Module 8: Production Data (The Real Thing)
**Goal:** Point the full pipeline at real production `.obj` files instead of example data — the closest this learning repo gets to what you'll actually do at work.

- [ ] **Step 1: Real Assembly Files**
  - [ ] Drop production `.obj` files into an `assemblies/` directory.
  - [ ] Use the Module 4.5 MCP filesystem server so `PlannerAgent` discovers them automatically — no hardcoded filenames.
- [ ] **Step 2: End-to-End Run**
  - [ ] Run the full pipeline: MCP discovery → Planner → ASAP Executor (with human approval gate) → Reviewer report → Langfuse trace.
  - [ ] Review the generated markdown report in `reports/` and the ASAP `.gif` output side by side.
  - [ ] Note what breaks or surprises you — those are the real engineering problems for your IRL role.
