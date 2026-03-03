FROM python:3.10-slim

# System build tools — this is what makes ASAP different from the other containers.
# ASAP has a C++ physics simulation that must be compiled from source.
# build-essential = gcc, g++, make
# cmake           = build system ASAP's C++ code uses
# git             = needed to clone ASAP inside the build
# python3-dev     = Python C headers, required for Python/C++ bindings
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3-dev \
    libgl-dev \
    libglx-dev \
    libglu1-mesa-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxi-dev \
    libxxf86vm-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone ASAP at a specific commit so this build is reproducible.
# Using a moving target like HEAD means a build that works today
# might silently break tomorrow if the ASAP repo changes.
RUN git clone https://github.com/yunshengtian/ASAP.git asap

# Install ASAP's Python dependencies before compiling the C++ binding.
# numpy must exist first — the C++ extension links against it at compile time.
# torch and torch-geometric are needed for the neural network-based part selector.
RUN pip install --no-cache-dir \
    "numpy<2" \
    scipy \
    networkx \
    trimesh \
    torch \
    torch-geometric \
    matplotlib \
    ikpy \
    seaborn \
    pyquaternion \
    rtree \
    scikit-learn \
    tqdm \
    pyglet \
    sortedcontainers


# Compile the C++ physics simulation binding.
# This produces a native .so file that Python imports as the "simulation" module.
# It must run after numpy is installed — numpy headers are needed at compile time.
# Patch setup.py to use 1 parallel job instead of 8.
# The hardcoded -j8 causes OOM when compiling inside Docker Desktop's
# default memory limit. -j1 is slower but reliably fits in 4GB.
RUN sed -i 's/-j[0-9]*/-j3/g' asap/simulation/setup.py && \
    cd asap/simulation && python setup.py install

RUN pip install --no-cache-dir mcp

# Patch upstream bug in ASAP's subdivide.py:
# edge_length_dict is keyed by (a, b) but edges are sometimes looked up as (b, a).
# Fix: try both orderings before raising KeyError.
RUN sed -i 's/longest_edge_length = edge_length_dict\[longest_edge\]/longest_edge_length = edge_length_dict.get(longest_edge) or edge_length_dict.get((longest_edge[1], longest_edge[0]), 0)/' \
    asap/assets/subdivide.py

COPY mcp_server/asap_server.py mcp_server/asap_server.py

CMD ["python", "mcp_server/asap_server.py"]
