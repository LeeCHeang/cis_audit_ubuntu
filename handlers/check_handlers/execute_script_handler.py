import os, subprocess
from typing import List, Dict
from utils.decorators import debug_wrapper

@debug_wrapper
def handle(script_name: str, params: List[str]) -> Dict[str, any]:  # Fixed return type
    if not script_name:
        return {
            'stdout': '',
            'stderr': 'ERROR: No script name provided.',
            'exit_code': 1
        }
    
    script_path = os.path.abspath(f"functions/{script_name}")
    if not isinstance(params, list):
        params = []
    
    # print(params)
    script_name = ['bash', script_path] + params
    
    try:
        result = subprocess.run(
            script_name, 
            capture_output=True, 
            text=True, 
            check=False
        )
        return {
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'exit_code': result.returncode
        }
    except FileNotFoundError:
        return {
            'stdout': '',
            'stderr': f"ERROR: 'bash' or script '{script_path}' not found.",
            'exit_code': 1
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': f"ERROR: An unexpected exception occurred: {e}",
            'exit_code': 1
        }