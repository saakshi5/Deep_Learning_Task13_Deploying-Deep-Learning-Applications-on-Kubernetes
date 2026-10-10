
import subprocess
import sys

def run_check(command):
    """Execute a kubectl command and display its result."""
    print("\n" + "=" * 65)
    print("COMMAND:", " ".join(command))
    print("=" * 65)
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=660,
            check=False
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("MESSAGES:")
            print(result.stderr)

        if result.returncode != 0:
            print("FAILED: exit code", result.returncode)
            return False

        print("CHECK PASSED")
        return True

    except FileNotFoundError:
        print("ERROR: kubectl was not found in PATH.")
        return False

    except subprocess.TimeoutExpired:
        print("ERROR: command timed out.")
        return False


def main():
    print("TASK 13: DEEP LEARNING KUBERNETES MONITOR")
    print("Checking deployment and service resources...")

    commands = [
        ["kubectl", "cluster-info"],
        ["kubectl", "get", "nodes"],
        ["kubectl", "get", "deployment",
         "task13-dl-deployment"],
        ["kubectl", "get", "pods", "-o", "wide"],
        ["kubectl", "get", "service",
         "task13-dl-service"],
        ["kubectl", "get", "endpointslices"],
        ["kubectl", "rollout", "status",
         "deployment/task13-dl-deployment",
         "--timeout=600s"],
    ]

    failures = 0

    for command in commands:
        if not run_check(command):
            failures += 1

    print("\n" + "=" * 65)

    if failures == 0:
        print("MONITORING COMPLETED: All commands succeeded.")
    else:
        print(
            "MONITORING COMPLETED WITH",
            failures,
            "failed command(s)."
        )
        print("Inspect the output and troubleshoot the issue.")

    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
