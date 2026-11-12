# Build a Coding Agent with ADK

In one hour you'll build a coding agent with Google's [Agent Development Kit](https://adk.dev/):
an AI that reads a project, edits files, runs the tests, and keeps fixing until they pass.
It's about 100 lines of plain Python.

```
you ──▶ agent ──▶ model decides: "read cart.py" ──▶ tool runs ──▶ result goes back to model
                        ▲                                                    │
                        └──────────── repeat until it answers you ◀──────────┘
```

## Before the workshop (10 minutes, please do this at home)

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/):
   `curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) or see the link for Windows.
2. Get the code and install it:
   ```bash
   git clone <this-repo-url> coding_agent_workshop
   cd coding_agent_workshop
   uv sync
   ```
3. Get a free Gemini API key at <https://aistudio.google.com/apikey>, then:
   ```bash
   cp .env.example .env      # then open .env and paste your key
   ```
4. Create the practice project and check everything:
   ```bash
   uv run reset_workspace.py
   uv run check_setup.py
   ```
   Every line should say `OK`.

## Running an agent

```bash
uv run adk web --reload_agents agents
```

Open <http://localhost:8000> and pick an agent from **Select an app** at the top of the page.
`--reload_agents` picks up your code changes, so you don't need to restart.
Always start it with `uv run` so the agent's `python -m pytest` uses this project's Python.

## What's in here

| Path | What it is |
|---|---|
| `agents/my_agent/` | **Your agent.** You build this one up during the workshop. |
| `agents/step1_hello/` … `agents/step4_safe/` | Finished checkpoints for each step. |
| `demo_project/` | A tiny shopping cart with two bugs and failing tests. Don't edit it. |
| `workspace/` | The agent's copy of `demo_project/`. The agents only touch this folder. |
| `reset_workspace.py` | Puts the original buggy project back in `workspace/`. |

## The steps

Work in `agents/my_agent/agent.py`. Each step has a finished version you can compare against.

### Step 1: An agent with no tools (`step1_hello`)
An ADK agent is a model plus an instruction. Run `my_agent` and ask:
> The tests in my project are failing. Can you fix them?

It can't see your files, so all it can do is guess.

### Step 2: Give it hands (`step2_files`)
Write three plain Python functions and pass them in `tools=[...]`:
`list_files()`, `read_file(path)` and `write_file(path, content)`.
The docstrings and type hints are what the model reads, so write them clearly.
Ask:
> What's in my project, and what does cart.py do?

Open the **Events** tab in `adk web` to watch each tool call and its result.

### Step 3: Close the loop (`step3_run`)
Add `run_command(command)` using `subprocess.run(..., cwd=WORKSPACE, timeout=30)`,
and tell the agent in its instruction to run the tests after every change.
Run `uv run reset_workspace.py`, then ask:
> The tests are failing. Fix them.

Watch it run the tests, read the failures, fix the code, and run them again.

### Step 4: Add guardrails (`step4_safe`)
Two guardrails:
- File tools refuse any path outside `workspace/`.
- Wrap `write_file` and `run_command` in `FunctionTool(..., require_confirmation=True)` so `adk web` asks you first.
  A card shows the arguments: tick **Confirmed** and press **Submit** to allow it,
  or press **Submit** without ticking to reject it.

Why confirm writes too? Approving `python -m pytest` approves whatever code the tests load,
and the agent could have just written a `conftest.py`. Confirming writes means every line that runs is one you've seen.

Ask it to `Read ../pyproject.toml` (it should refuse), then reset and fix the tests again, approving the fix and each test run.
If it asks to run something you didn't ask for (it often tries `git diff`), reject it and watch what it does.

## Fell behind?

Copy the next checkpoint over your agent and carry on:

```bash
cp agents/step3_run/agent.py agents/my_agent/agent.py
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Address already in use` | `uv run adk web --reload_agents --port 8001 agents` |
| `429` / `RESOURCE_EXHAUSTED` | You've hit the free-tier rate limit. Wait a minute, or use a different key. |
| Agent says `cart.py` doesn't exist | Run `uv run reset_workspace.py`. |
| Agent fixed everything and you want to demo again | Run `uv run reset_workspace.py`. |
| `python: command not found` inside the agent | Start `adk web` with `uv run` as shown above. |

## Going further

- **Smaller edits:** add an `edit_file(path, old, new)` tool that replaces one snippet instead of rewriting the whole file.
- **Git:** let it make commits, so every change is easy to undo.
- **MCP tools:** plug in existing tool servers with ADK's `McpToolset`.
- **Real isolation:** the guardrails here are not a sandbox. ADK's
  [`long-horizon-harness`](https://github.com/google/adk-samples/tree/main/core/python/long-horizon-harness)
  sample shows a per-user sandbox, approval gates and memory.
