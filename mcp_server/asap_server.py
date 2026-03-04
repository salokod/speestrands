import os
import re
import subprocess
import sys
from mcp.server.fastmcp import FastMCP

_host = os.getenv("MCP_HOST", "127.0.0.1")
mcp = FastMCP("asap-tools", host=_host)

# ASAP resolves assemblies as: /app/asap/assets/{ASSEMBLIES_DIR}/{assembly_id}
# Using a relative name here keeps us inside ASAP's expected assets/ tree,
# avoiding path resolution issues when ASAP passes asset_folder to RedMax.
ASSEMBLIES_DIR = os.getenv("ASSEMBLIES_DIR", "test_assembly")


ASAP_SCRIPT = "/app/asap/plan_sequence/run_seq_plan.py"
ASAP_DIR = "/app/asap"


@mcp.tool()
def plan_cad_assembly(
    assembly_id: str,
    max_gripper: int = 4,
    budget: int = 400,
    base_part: str = None,
) -> str:
    """
    Run the ASAP sequence planner on a CAD assembly and return the disassembly plan.
    The planner figures out in what order parts can be removed from the assembled state.
    assembly_id: folder name of the assembly (e.g. '00561').
    max_gripper: number of grippers available to hold parts stable (default 4, higher helps with stability failures).
    budget: max feasibility evaluations (default 400).
    base_part: part ID that stays fixed as the foundation (e.g. '0'). Leave None to auto-detect.
    """
    log_dir = f"/app/logs/{assembly_id}"
    os.makedirs(log_dir, exist_ok=True)

    render_dir = f"/app/renders/{assembly_id}"
    os.makedirs(render_dir, exist_ok=True)

    cmd = [
        "xvfb-run", "--auto-servernum",
        sys.executable,
        ASAP_SCRIPT,
        "--dir", ASSEMBLIES_DIR,
        "--id", assembly_id,
        "--planner", "dfs",
        "--generator", "heur-out",
        "--max-gripper", str(max_gripper),
        "--budget", str(budget),
        "--early-term",
        "--log-dir", log_dir,
        "--render",
        "--record-dir", render_dir,
    ]
    if base_part is not None:
        cmd.extend(["--base-part", str(base_part)])

    # Run the process and stream its output to the server's console in real-time
    process = subprocess.Popen(
        cmd,
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

    # Explicitly detect planning failure from the stats line.
    # The ASAP planner exits 0 even on failure, so we must parse stdout.
    stats_match = re.search(r'\[seq_plan\] stats: (.+)', out)
    if stats_match:
        stats_str = stats_match.group(1)
        if "'success': False" in stats_str:
            return (
                f"PLANNING FAILED: The planner returned success=False.\n"
                f"Stats: {stats_str}\n"
                f"This is likely due to false collision detections. "
                f"Use the subdivide_assembly tool to increase mesh resolution, then try again."
            )


    return out


@mcp.tool()
def subdivide_assembly(assembly_id: str, max_edge: float = 0.05) -> str:
    """
    Subdivide the 3D meshes of a CAD assembly to improve collision detection accuracy.
    If the sequence planner fails because it falsely detects collisions, run this tool 
    on the assembly to increase its polygon count, and then run the planner again.
    
    assembly_id is the folder name of the assembly (e.g. '00000').
    max_edge is the maximum edge length for the subdivision (smaller is more precise). Default 0.05.
    """
    source_dir = os.path.join(ASAP_DIR, "assets", ASSEMBLIES_DIR, assembly_id)
    target_dir = source_dir  # Overwrite in place to be used by the planner
    
    print(f"\n--- Subdividing meshes for assembly {assembly_id} (max_edge={max_edge}) ---", flush=True)
    
    result = subprocess.run(
        [
            sys.executable,
            os.path.join(ASAP_DIR, "assets", "subdivide.py"),
            "--source-dir", source_dir,
            "--target-dir", target_dir,
            "--max-edge", str(max_edge)
        ],
        capture_output=True,
        text=True,
        cwd=ASAP_DIR,
    )
    
    if result.returncode != 0:
        print(f"--- Subdivision failed (Exit Code: {result.returncode}) ---", flush=True)
        print(f"stdout: {result.stdout}", flush=True)
        print(f"stderr: {result.stderr}\n", flush=True)
        return (
            f"Subdivision failed (exit code {result.returncode}).\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )
        
    # Clear stale SDF cache files — subdivision changes the mesh geometry so any
    # previously cached .sdf voxel grids are invalid. Deleting them forces the
    # planner to regenerate fresh SDF data on the next run.
    sdf_files = [f for f in os.listdir(target_dir) if f.endswith(".sdf")]
    for sdf_file in sdf_files:
        os.remove(os.path.join(target_dir, sdf_file))

    print(f"--- Subdivision complete! Cleared {len(sdf_files)} stale SDF cache file(s). ---\n", flush=True)
    return f"Successfully subdivided meshes in assembly {assembly_id} and cleared {len(sdf_files)} stale SDF cache file(s). You can now try running the sequence planner again."


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run()
