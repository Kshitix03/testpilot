import subprocess
import sys

TIMEOUT_SECONDS = 60


def run_test(filepath):
    """
    Runs a Python file in a subprocess.
    Returns (passed, output, error):
      - passed: True if the file ran without crashing AND printed a line starting with "PASS"
      - output: everything the script printed to stdout
      - error: traceback or stderr if it crashed

    The file being run was written by an LLM, so it is treated as untrusted:
    a separate process means a crash or a hang can't take the agent down.
    """
    try:
        result = subprocess.run(
            [sys.executable, filepath],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS
        )
    except subprocess.TimeoutExpired as e:
        # A hung test is a failure, not a crash of the agent. Hand back whatever
        # the script managed to print so the model has something to work with.
        partial = _decode(e.stdout)
        return False, partial, f"TimeoutExpired: test exceeded {TIMEOUT_SECONDS}s and was killed"

    output = result.stdout.strip()
    error = result.stderr.strip()

    # A test passes if it printed a PASS line and didn't crash
    passed = result.returncode == 0 and any(
        line.startswith("PASS") for line in output.splitlines()
    )

    return passed, output, error


def _decode(stream):
    """TimeoutExpired.stdout is bytes or str depending on how it died, and may be None."""
    if stream is None:
        return ""
    if isinstance(stream, bytes):
        return stream.decode(errors="replace").strip()
    return stream.strip()
