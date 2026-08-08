# TestPilot

I wanted to know whether an LLM could write a browser test that actually runs —
and whether it could fix that test when it broke, without me in the loop.
TestPilot is the answer I built.

You hand it a sentence:

> "Log in to saucedemo.com, add one product to the cart, and verify the cart badge shows 1"

It writes a Playwright script, runs it in a real Chromium, and reads the result.
If the script crashed or the assertion failed, it gets the traceback back and
tries again. Three attempts, then it gives up and tells you it gave up.

That retry step is the whole point. A model that writes test code is a code
generator. A model that runs its own code, looks at what went wrong, and adjusts
is doing something meaningfully different, and I wanted to build the smallest
honest version of that.

## Running it

You'll need Python 3.11+ and a Gemini API key ([aistudio.google.com/apikey](https://aistudio.google.com/apikey) — the free tier is enough).

```bash
git clone https://github.com/Kshitix03/testpilot.git
cd testpilot

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
playwright install chromium

cp .env.example .env           # then put your key in it
```

Then:

```bash
python agent.py            # one instruction, verbose output
python evals.py            # all 12 cases, prints a scoreboard
python demo_correction.py  # feeds it a deliberately broken test, watch it recover
```

`demo_correction.py` is the one to run if you only run one. It starts with a test
that uses selectors that don't exist, so you see the failure and the fix back to back.

## What's in here

| File | |
|---|---|
| `agent.py` | The agent. Generates a test, runs it, feeds failures back to the model. |
| `runner.py` | Executes a Python file in a subprocess, returns pass/fail plus output. |
| `evals.py` | Runs every case and prints a scoreboard. |
| `eval_cases.py` | The dataset: 12 instructions. |
| `demo_correction.py` | Starts from a broken test to show the correction loop. |
| `test_manual.py` | A hand-written test, no AI. This was step one, before any of the rest existed. |

`generated_test.py` shows up when you run anything — it's the model's current
output, overwritten every attempt, and it's gitignored.

## Decisions I made, and why

**No framework.** LangChain would have hidden the generate → run → fix loop behind
an abstraction, and that loop is the only interesting thing here. Written out
directly it's about thirty lines in `main()`, and I can point at any of them and
say what it does.

**Generated code runs in a subprocess.** It comes from a model, so I don't trust it.
A subprocess means a crash or a hang can't take the agent down with it, and I get
the full traceback as text — which is exactly what I need to send back to the model
anyway. That turned out to be the convenient choice as well as the safe one.

**The pass signal is a printed `PASS:` line.** No pytest, no exit code parsing, no
XML. The prompt tells the model exactly what to print and the runner looks for it.
It's crude, but it's a contract I can explain in one sentence and change in one line.

**Three retries.** I tried more. Past the second attempt the model usually stops
fixing the original test and starts writing a different wrong one instead, so the
extra calls buy nothing. Three also keeps a full eval run down to a few minutes.

**`gemini-3.1-flash-lite`.** 500 requests a day free, which is enough to run the
eval set several times over. The bigger models had no free quota on my account,
which decided it for me.

## Results

```
Score: 12/12 passed | Avg attempts: 1.0
```

saucedemo.com, `gemini-3.1-flash-lite`, max 3 retries.

I want to be straight about what that number is worth. saucedemo.com is a site
built specifically for people practising test automation. The selectors are clean
and stable (`#user-name`, `#login-button`), and the model has near-certainly seen
it during training. 12/12 on that is close to the floor, not the ceiling.

Things it doesn't tell you:

- How it does on a real site with generated class names, shadow DOM, or a login wall
- Whether it can hold state across a long flow — full checkout, then confirm the
  order number turns up in history
- Anything about flakiness. There's no retry for network timeouts, only for logic errors
- Anything about vague instructions. All 12 cases name something observable. Give it
  "make sure checkout works" and results get inconsistent fast

## Where it breaks

**Code fences.** The prompt says no markdown. The model sometimes adds it anyway.
`strip_code_fences()` handles the simple case, but if there's a sentence of
explanation before the fence it falls over. A real fix is structured output rather
than a string trim.

**Retries that wander.** The only thing carried between attempts is the last error
message. The agent has no idea it already tried a particular approach, so on the
harder instructions it can circle instead of converge. Passing every prior attempt
into the context would fix this and is the next thing I'd do.

**Timeouts read as bugs.** Playwright's default timeout is short. On a slow machine
a test can time out for environmental reasons and the agent will confidently try to
"fix" code that was already correct. It has no way to tell those two failures apart.

**The eval set is too easy.** One site, twelve cases, all of them friendly. A
benchmark worth the name would include sites the model hasn't memorised and flows
that need assertions between steps rather than only at the end.

## License

MIT. See [LICENSE](LICENSE).
