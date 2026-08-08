"""
Demo: self-correction loop.
Starts with a broken test (wrong selector), watches Gemini fix it.
"""
from agent import fix_test
from runner import run_test

INSTRUCTION = "Log in to saucedemo.com and verify the inventory page loads"

BROKEN_CODE = """\
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.saucedemo.com")
    page.fill("#wrong-username-field", "standard_user")
    page.fill("#wrong-password-field", "secret_sauce")
    page.click("#wrong-login-btn")
    print("PASS: logged in")
    browser.close()
"""

print("=== TestPilot: self-correction demo ===\n")
print("Step 1: Run the broken test (wrong selectors)")
print("-" * 40)

with open("generated_test.py", "w") as f:
    f.write(BROKEN_CODE)

passed, output, error = run_test("generated_test.py")
full_output = "\n".join(filter(None, [output, error]))
print(f"Result: {'PASS' if passed else 'FAIL'}")
print(f"Output: {full_output[:300]}")

print("\nStep 2: Send error to Gemini, get fixed code")
print("-" * 40)
fixed_code = fix_test(BROKEN_CODE, full_output, INSTRUCTION)
print("Fixed code received. Running it...")

with open("generated_test.py", "w") as f:
    f.write(fixed_code)

passed, output, error = run_test("generated_test.py")
print(f"Result: {'PASS' if passed else 'FAIL'}")
print(f"Output: {output}")
