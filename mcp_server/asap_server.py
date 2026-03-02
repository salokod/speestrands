import os
import subprocess
import sys
from mcp.server.fastmcp import FastMCP

_host = os.getenv("MCP_HOST", "127.0.0.1")
mcp = FastMCP("asap-tools", host=_host)

# The assemblies directory is mounted into the container at /app/assemblies.
# Each sub-folder is one assembly: a set of .obj part meshes + contact_graph.json.
ASSEMBLIES_DIR = os.getenv("ASSEMBLIES_DIR", "/app/assemblies/test_assembly")


ASAP_SCRIPT = "/app/asap/plan_sequence/run_seq_plan.py"
ASAP_DIR = "/app/asap"


@mcp.tool()
def plan_cad_assembly(assembly_id: str) -> str:
    """
    Run the ASAP sequence planner on a CAD assembly and return the disassembly plan.
    The planner figures out in what order parts can be removed from the assembled state.
    assembly_id is the folder name of the assembly to plan (e.g. '00000').
    Returns the planner output including the sequence and planning statistics.
    """
    result = subprocess.run(
        [
            sys.executable,
            ASAP_SCRIPT,
            "--dir", ASSEMBLIES_DIR,
            "--id", assembly_id,
            "--planner", "dfs",
            "--generator", "rand",
        ],
        capture_output=True,
        text=True,
        cwd=ASAP_DIR,
    )

    if result.returncode != 0:
        return (
            f"Planner failed (exit code {result.returncode}).\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )

    return result.stdout or "Planner completed with no output."


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()
