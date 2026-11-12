"""Your coding agent. Build it up step by step (see README.md).

Stuck? Copy the next checkpoint over this file and keep going, e.g.:
    cp agents/step3_run/agent.py agents/my_agent/agent.py
"""

from google.adk.agents import Agent

# Step 2: write list_files(), read_file(path) and write_file(path, content)
#         here, then add them to tools=[...] below.

# Step 3: write run_command(command) and add it to tools=[...].

# Step 4: keep paths inside the workspace, and ask before running commands.

root_agent = Agent(
    name="coding_agent",
    model="gemini-3.8-flash",
    instruction="You are a helpful coding assistant.",
)
