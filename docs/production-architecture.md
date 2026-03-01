# Production Architecture Reference

This document maps the learning repo structure to a real production deployment.
Everything built here is designed so the swap from local → production is
configuration, not code rewrites.

---

## Repo Boundaries

In this repo, everything lives together for convenience. In production, it splits
into two independently deployed services:

```
This repo (learning)              Production (two repos)
─────────────────────────         ──────────────────────────────────
mcp_server/                  →    Repo A: robot-mcp-server
  server.py                         server.py
  (future) tools/                   tools/
    robot_tools.py                    robot_tools.py
    asap_tools.py                     asap_tools.py
                                    Dockerfile
                                    requirements.txt

core/                        →    Repo B: strands-agent
examples/                           core/
src/tools/ (interim)                examples/
                                    Dockerfile
                                    requirements.txt
```

The tool implementations in `src/tools/` will migrate into `mcp_server/tools/`
in Module 6 when the real ASAP tooling is built. The learning examples keep
importing from `src/tools/` until that migration happens.

---

## Transport: Local vs Production

The only line that changes between local development and production is the
MCPClient transport. Everything else — agents, tools, graph pipeline — stays
identical.

**Local (this repo):**
```python
# stdio: MCPClient spawns the server as a subprocess
from mcp import stdio_client, StdioServerParameters
from strands.tools.mcp import MCPClient

mcp_client = MCPClient(lambda: stdio_client(
    StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "./"]
    )
))
```

**Production:**
```python
# HTTP: MCPClient connects to an always-on service over the network
from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp import MCPClient

mcp_client = MCPClient(
    lambda: streamablehttp_client(os.getenv("MCP_ROBOT_URL"))
)
```

This swap lives in a `core/mcp_factory.py` file (same pattern as `llm_factory.py`).
Set `MCP_TRANSPORT=http` in production, `MCP_TRANSPORT=stdio` locally.

---

## AWS Production Deployment

```
                        VPC (private subnets)
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌──────────────────────┐      ┌────────────────────────┐    │
│  │  ECS Service         │      │  ECS Service           │    │
│  │  strands-agent       │─────▶│  robot-mcp-server      │    │
│  │                      │ HTTP │                        │    │
│  │  graph_agent.py      │      │  move_arm()            │    │
│  │  PlannerAgent        │      │  get_arm_status()      │    │
│  │  ExecutorAgent       │      │  plan_cad_assembly()   │    │
│  │  ReviewerAgent       │      │                        │    │
│  └──────────┬───────────┘      └────────────────────────┘    │
│             │                            ▲                    │
│             │                           IAM task role         │
│             ▼                           (auth between         │
│  ┌──────────────────────┐               services)            │
│  │  S3 Bucket           │                                     │
│  │  reports/ output     │                                     │
│  │  session history     │                                     │
│  └──────────────────────┘                                     │
│                                                              │
│  ┌──────────────────────┐                                     │
│  │  Langfuse (Module 7) │◀── OpenTelemetry from both         │
│  │  ECS Service or      │    services                        │
│  │  Managed SaaS        │                                     │
│  └──────────────────────┘                                     │
└──────────────────────────────────────────────────────────────┘
```

### robot-mcp-server ECS Service

- **Type**: ECS Service (always-on, not a Task)
- **Replicas**: 2 minimum for availability
- **Discovery**: AWS Cloud Map → `http://robot-mcp.internal/mcp`
- **Auth**: IAM task role — only `strands-agent` tasks are allowed to call it
- **Ownership**: whoever owns the robot hardware / ASAP simulator
- **Release cycle**: independent from the agent service

### strands-agent ECS Service

- **Type**: ECS Service (always-on) or Task (on-demand per job)
- **Trigger**: API Gateway → Lambda → ECS Task, or SQS queue consumer
- **Config via environment variables**:
  ```
  LLM_PROVIDER=bedrock
  MCP_ROBOT_URL=http://robot-mcp.internal/mcp
  MCP_TRANSPORT=http
  LANGFUSE_HOST=http://langfuse.internal
  REPORTS_BUCKET=s3://my-assembly-reports
  ```
- **Ownership**: AI/ML team

---

## The Modularity Payoff

Every swap in this system is an environment variable, not a code change:

| What you swap       | How you swap it                        | Code changes |
|---------------------|----------------------------------------|--------------|
| Ollama → Bedrock    | `LLM_PROVIDER=bedrock`                 | None         |
| stdio → HTTP MCP    | `MCP_TRANSPORT=http`                   | None         |
| Local → prod MCP    | `MCP_ROBOT_URL=https://...`            | None         |
| Langfuse → Galileo  | Change OTEL exporter endpoint          | None         |
| Mock tools → ASAP   | Deploy new `robot-mcp-server` image    | None         |

This is the architecture you're building toward. Each module adds one more
swappable layer to the stack.
