import subprocess

# from utils.decorators import debug_wrapper # <-- Import our new decorator

# @debug_wrapper # <-- Apply the decorator to the handle function
def handle(target: str, params: dict) -> str:
    try:
        result = subprocess.run(['dpkg-query', '-s', target], capture_output=True, text=True)
        # return "installed" if result.returncode == 0 else "not_installed"
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }

    except FileNotFoundError:
        return "ERROR: dpkg-query not found."

    except Exception as e:
        return {"stdout": "", "stderr": f"ERROR: Command failed to execute. Reason: {e}", "exit_code": 127}