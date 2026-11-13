# Facilitator guide (60 minutes)

The goal: everyone leaves having watched *their own* agent turn red tests green, and understanding
that a coding agent is just **a model + tools + a loop**.

## Before Saturday

- [ ] Send the "Before the workshop" section of the README a few days ahead. Ask people to reply
      with a screenshot of `uv run check_setup.py` all `OK`. Setup is the biggest risk to the hour.
- [ ] Rehearse Step 3 at least five times with `step3_run` and a fresh `uv run reset_workspace.py`.
      Note how many test runs it usually takes, so you can predict it live. In testing on
      `gemini-3.8-flash` it took 6–7 tool calls and 20–30 seconds, fixing both bugs in one edit.
- [ ] Have a spare API key ready for anyone whose key fails on the day.
- [ ] Open the README's **Open in Cloud Shell** button once yourself, so you've seen the tutorial
      panel and the Web Preview step before someone asks.
- [ ] Bump your editor and browser font size for the projector.

## Run of show

| Time | Segment | You do | They do |
|---|---|---|---|
| 0:00–0:05 | **Hook** | Run `step4_safe` live: "The tests are failing. Fix them." Approve the fix and each test run (tick **Confirmed**, press **Submit**) until green. | Watch |
| 0:05–0:12 | **Setup check** | Walk the room; hand out the spare key | `uv run adk web --reload_agents agents`, open `my_agent` |
| 0:12–0:20 | **Step 1: no tools** | Show `Agent(name, model, instruction)`. Ask it to fix the tests: it guesses. | Same, in `my_agent` |
| 0:20–0:32 | **Step 2: give it hands** | Live-code `list_files` and `read_file`, then `write_file`. Open the Events tab. | Add the three tools |
| 0:32–0:44 | **Step 3: close the loop** | Add `run_command` and the "run the tests" line in the instruction. Reset, then "Fix the tests." | Same. This is the moment that matters. |
| 0:44–0:52 | **Step 4: safety** | Add `_resolve` and `require_confirmation`. Demo `Read ../pyproject.toml`. | Same, or copy `step4_safe` |
| 0:52–1:00 | **Wrap + Q&A** | "Going further" list in the README | Questions |

If you're behind at 0:32, have everyone `cp agents/step2_files/agent.py agents/my_agent/agent.py`
so nobody misses Step 3.

## Talking points

**Step 1.** The model has knowledge but no eyes or hands. Everything it says about "your project"
is a guess.

**Step 2.**
- ADK reads the function's name, type hints and docstring and sends them to the model as a tool
  definition. A vague docstring gives you a confused agent.
- The model never runs your code. It *asks* for a tool call, ADK runs the function, and the result
  goes back to the model. Point at this in the Events tab.
- Tools return `{"error": ...}` instead of raising. ADK re-raises a tool's exception and ends the
  run, but an error message is something the model can recover from.

**Step 3.**
- You didn't write a loop. ADK's runner keeps calling the model until it answers with text instead
  of a tool call.
- The instruction "run the tests after every change" is what turns edit-and-hope into
  edit-and-check. Try removing it and compare.
- Output is truncated to the last 4000 characters: the end is where the failures and summary are,
  and long tool output eats the context window.

**Step 4.**
- In rehearsal, after the tests went green the agent asked to run `git diff`, which nobody requested.
  In Step 3 it just runs. In Step 4 you can reject it: press **Submit** without ticking **Confirmed**,
  and the agent explains it skipped the command. That's the clearest argument for approvals.
- Ask the room: *"We already approve every command. Why approve writes too?"*
  Answer: approving `python -m pytest` approves whatever code the tests load. Without write
  approval the agent could add a `conftest.py` that runs on the next test run, and the card would
  still just say `python -m pytest`. It's the same reason you can't auto-approve test runs.
- These guardrails are not a sandbox. `run_command` can still `cat ../.env` if you approve it.
  Real isolation means a container or VM (see the `long-horizon-harness` sample).

## Things that can go wrong live

Never demo the path guard with `../.env`: in Step 3 it works, and prints your API key on the
projector. Use `../pyproject.toml`.

| Symptom | Recovery |
|---|---|
| Agent rewrites the tests instead of the code | Add "Never edit test files" to the instruction. Good discussion point. |
| Agent stops after one fix with tests still failing | Reply "run the tests again". Then point out why the instruction matters. |
| Wi-Fi or rate limit dies | Show your rehearsal: keep a screen recording of Step 3 going green. |
| `workspace/` already fixed from a previous run | `uv run reset_workspace.py` |
| Someone's laptop setup won't work | Send them to **Open in Cloud Shell** in the README: nothing to install, and its tutorial covers every step. |

## The bugs in the demo project

`demo_project/cart.py` has two bugs that fail three of its four tests:

1. `subtotal` ignores `quantity` (fails `test_subtotal_counts_quantity` and `test_total_with_discount`).
2. `apply_discount` subtracts the percentage as a flat amount (fails `test_discount_is_a_percentage`).

The agent has to run the tests at least twice (once to see the failures, once to confirm the fix),
which shows off the loop. If it only fixes one bug at first, even better.
