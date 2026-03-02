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
    # Run the process and stream its output to the server's console in real-time
    process = subprocess.Popen(
        [
            sys.executable,
            ASAP_SCRIPT,
            "--dir", ASSEMBLIES_DIR,
            "--id", assembly_id,
            "--planner", "dfs",
            "--generator", "rand",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, # Merge stderr into stdout
        text=True,
        cwd=ASAP_DIR,
        bufsize=1, # Line buffered
    )

    full_output = []
    print(f"\n--- Starting ASAP Planner for assembly {assembly_id} ---", flush=True)
    
    # Stream the output line-by-line to the server logs
    for line in iter(process.stdout.readline, ''):
        print(line, end='', flush=True)
        full_output.append(line)
        
    process.stdout.close()
    returncode = process.wait()
    
    print(f"--- Finished ASAP Planner for assembly {assembly_id} (Exit Code: {returncode}) ---\n", flush=True)

    out = "".join(full_output)

    if returncode != 0:
        return (
            f"Planner failed (exit code {returncode}).\n"
            f"Output: {out[-2000:] if out else ''}"
        )

    out = out or "Planner completed with no output."
    
    # The raw output is extremely verbose and can crash the transport or LLM context.
    # We only care about the final summary block if it succeeds.
    if len(out) > 5000:
        out = f"... [Truncated {len(out) - 5000} chars] ...\n\n" + out[-5000:]

    return out


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()
