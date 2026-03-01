from strands.tools import tool


# The @tool decorator is the magic! It inspects your Python function
# and automatically builds the JSON "menu" to send to the LLM.
@tool
def move_arm(x: float, y: float, z: float) -> str:
    """
    Moves the robotic arm to the specified X, Y, and Z coordinates.
    Always use this tool when the user asks to move the robot.
    """
    # In a real scenario, this is where you would put your ASAP physics
    # engine code or send commands over serial to a real robot arm.

    # For now, we are just mocking it.
    print(f"[ROBOT HARDWARE] Bzzzt... moving arm to X:{x}, Y:{y}, Z:{z}...")

    # It is crucial that tools return a string or simple data type.
    # This return value is what gets sent BACK to the AI so it knows what happened.
    return f"Success! Arm moved to {x}, {y}, {z}."


# We can put multiple tools in this file!
@tool
def get_arm_status() -> str:
    """
    Checks the current diagnostic status of the robotic arm.
    """
    return "Status: ONLINE. Diagnostics: NOMINAL."
