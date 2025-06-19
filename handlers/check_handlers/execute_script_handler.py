import os, subprocess
from typing import List, Tuple

# def get_script_path_and_name(given_path):
#     abs_path = os.path.abspath(given_path)
#     script_name = os.path.basename(abs_path)
#     return abs_path, script_name

# path, name = get_script_path_and_name("ensure_kernel_module_is_not_available.sh")
# print("Absolute path:", path)
# print("Script name:", name)
from utils.decorators import debug_wrapper # <-- Import our new decorator

@debug_wrapper # <-- Apply the decorator to the handle function
def handle(script_name: str, params: List[str]) -> Tuple[str, str, int]:
    if not script_name:
        return ("", "ERROR: No script name provided.", 1)

    script_path = os.path.abspath(f"functions/{script_name}")
    if not isinstance(params, list):
        params = []  # Default to an empty list if params is not a list

    script_name = ['bash', script_path] + params
    
    try:
        result = subprocess.run(
            script_name, 
            capture_output=True, 
            text=True, 
            check=False # Do not raise exception on non-zero exit
        )
        # return (result.stdout.strip(), result.stderr.strip(), result.returncode)
        # If there's an error, return stderr with ERROR prefix
        # if result.returncode != 0 and result.stderr.strip():
        #     return f"ERROR: {result.stderr.strip()}"
        
        # # Return stdout, or indicate empty output
        # return result.stdout.strip() if result.stdout.strip() else "No output"
        # if result.returncode != 0:
        #     # If the script failed, return a formatted error with its output
        #     error_details = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
        #     return f"ERROR: Script '{script_name}' exited with code {result.returncode}. Details: {error_details}"
        
        # If the script succeeded, return its standard output
        # return result.stdout.strip()
        return {
            'stdout': result.stdout.strip(),
            'stderr': result.stderr.strip(),
            'exit_code': result.returncode
        }

    except FileNotFoundError:
        return ("", f"ERROR: 'bash' or script '{script_path}' not found.", 1)
    except Exception as e:
        return ("", f"ERROR: An unexpected exception occurred: {e}", 1)
