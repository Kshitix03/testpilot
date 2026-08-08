import time
from agent import generate_test, fix_test
from runner import run_test
from eval_cases import CASES

MAX_RETRIES = 3
GENERATED_FILE = "generated_test.py"

# Small pause between cases to stay well within rate limits (15 RPM)
SLEEP_BETWEEN_CASES = 5


def run_case(case):
    """
    Runs the full agent loop for one eval case.
    Returns a result dict with: passed, attempts_used, error_summary.
    """
    instruction = case["instruction"]
    code = generate_test(instruction)

    for attempt in range(1, MAX_RETRIES + 1):
        with open(GENERATED_FILE, "w") as f:
            f.write(code)

        passed, output, error = run_test(GENERATED_FILE)
        full_output = "\n".join(filter(None, [output, error]))

        if passed:
            return {"passed": True, "attempts": attempt, "error": None}

        if attempt < MAX_RETRIES:
            code = fix_test(code, full_output, instruction)

    # Truncate error for display — full tracebacks are too long for a scoreboard
    short_error = full_output[:120].replace("\n", " ")
    return {"passed": False, "attempts": MAX_RETRIES, "error": short_error}


def print_scoreboard(results, cases):
    print("\n" + "=" * 60)
    print("EVAL RESULTS")
    print("=" * 60)

    for case, result in zip(cases, results):
        status = "PASS" if result["passed"] else "FAIL"
        attempts = result["attempts"]
        label = f"{case['id']:2}. {status} (attempt {attempts}) | {case['instruction'][:55]}"
        print(label)
        if not result["passed"] and result["error"]:
            print(f"     Error: {result['error']}")

    print("=" * 60)

    passed_count = sum(1 for r in results if r["passed"])
    total = len(results)
    avg_attempts = sum(r["attempts"] for r in results) / total

    print(f"Score: {passed_count}/{total} passed | Avg attempts: {avg_attempts:.1f}")

    # Failure analysis
    failed = [(cases[i], results[i]) for i in range(total) if not results[i]["passed"]]
    if failed:
        print(f"\nFailed cases ({len(failed)}):")
        for case, result in failed:
            print(f"  - Case {case['id']}: {case['instruction']}")
    print("=" * 60)


def main():
    print(f"TestPilot eval harness")
    print(f"Running {len(CASES)} cases (max {MAX_RETRIES} attempts each)...\n")
    results = []

    for i, case in enumerate(CASES):
        print(f"[{i+1}/{len(CASES)}] Case {case['id']}: {case['instruction'][:60]}...")
        result = run_case(case)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"       -> {status} in {result['attempts']} attempt(s)")
        results.append(result)

        # Don't sleep after the last case
        if i < len(CASES) - 1:
            time.sleep(SLEEP_BETWEEN_CASES)

    print_scoreboard(results, CASES)


if __name__ == "__main__":
    main()
