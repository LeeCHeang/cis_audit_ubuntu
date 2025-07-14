import subprocess
from typing import Dict

from utils.decorators import debug_wrapper

@debug_wrapper
def handle(target: str, params: dict) -> Dict[str,any]:
    if params is None:
        params = {}
    command_to_run = ['/bin/bash', '-c', target]
    try:
        result = subprocess.run(
            command_to_run,
            # shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"stdout": "", "stderr": f"ERROR: Command failed to execute. Reason: {e}", "exit_code": 127}