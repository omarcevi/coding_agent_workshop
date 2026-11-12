"""Step 1: an agent with no tools.

An ADK agent is a model plus an instruction. `adk web` finds `root_agent`
in this file and gives you a chat window for it.

Try: "The tests in my project are failing. Can you fix them?"
It can't see your files, so all it can do is guess. Step 2 fixes that.
"""

from google.adk.agents import Agent

root_agent = Agent(
    name="coding_agent",
    model="gemini-3.8-flash",
    instruction="You are a helpful coding assistant.",
)
