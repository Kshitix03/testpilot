"""
TestPilot — turns an English instruction into a Playwright test, runs it,
and feeds failures back to the model until it passes or runs out of attempts.
"""
import os
import sys
from dotenv import load_dotenv
from google import genai
from runner import run_test

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    sys.exit(
        "GEMINI_API_KEY is not set.\n"
        "Copy .env.example to .env and put your key in it "
        "(get one at https://aistudio.google.com/apikey)."
    )

client = genai.Client(api_key=API_KEY)

MODEL = "models/gemini-3.1-flash-lite"

INSTRUCTION = "Log in to saucedemo.com and verify the inventory page loads"

MAX_RETRIES = 3

# Prompt for the first attempt: generate a test from scratch
GENERATE_PROMPT = """\
You are a test automation engineer. Write a Python Playwright test script.

Rules:
- Use playwright.sync_api (sync, not async)
- Target site: https://www.saucedemo.com
- Login credentials: username = standard_user, password = secret_sauce
- Launch the browser with headless=True (no visible window)
- At the end, print exactly "PASS: <what was verified>" if the test passes
- If something goes wrong, print exactly "FAIL: <reason>"
- Output ONLY the Python code. No explanations, no markdown, no code fences.

Instruction: {instruction}
"""

# Prompt for retry attempts: fix broken code using the error as feedback
FIX_PROMPT = """\
You are a test automation engineer. The Playwright test below failed. Fix it.

Original instruction: {instruction}

Code that failed:
{code}

Error output:
{error}

Rules:
- Use playwright.sync_api (sync, not async)
- Target site: https://www.saucedemo.com
- Login credentials: username = standard_user, password = secret_sauce
- Launch the browser with headless=True
- Print exactly "PASS: <what was verified>" if the test passes
- Output ONLY the corrected Python code. No explanations, no markdown, no code fences.
"""


def strip_code_fences(text):
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        return "\n".join(lines[1:-1])
    return text


def generate_test(instruction):
    prompt = GENERATE_PROMPT.format(instruction=instruction)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return strip_code_fences(response.text)


def fix_test(code, error, instruction):
    prompt = FIX_PROMPT.format(instruction=instruction, code=code, error=error)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )
    return strip_code_fences(response.text)


def main():
    print(f"TestPilot | model: {MODEL}")
    print(f"Instruction: {INSTRUCTION}\n")

    print("Generating initial test...")
    code = generate_test(INSTRUCTION)

    for attempt in range(1, MAX_RETRIES + 1):
        with open("generated_test.py", "w") as f:
            f.write(code)

        print(f"\nAttempt {attempt}/{MAX_RETRIES}: running test...")
        passed, output, error = run_test("generated_test.py")

        # Combine stdout and stderr so the LLM sees the full picture on failure
        full_output = "\n".join(filter(None, [output, error]))
        print(f"Output: {full_output}")

        if passed:
            print(f"\nResult: PASS (on attempt {attempt})")
            return

        print(f"Result: FAIL")

        if attempt < MAX_RETRIES:
            print(f"Sending error back to Gemini to fix...")
            code = fix_test(code, full_output, INSTRUCTION)

    print(f"\nResult: FAIL — could not fix after {MAX_RETRIES} attempts")


if __name__ == "__main__":
    main()
