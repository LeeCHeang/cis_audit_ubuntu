import subprocess

def handle(target: str, params: dict) -> str:
    if params is None:
        params = {}
    
    try:
        result = subprocess.run(
            target,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )

        # # Get the list of exit codes that are "allowed" to fail from the CSV.
        # # Defaults to an empty list if not provided.
        # # To use "{'allow_error_exit': [1, 2]}"
        # allowed_error_codes = params.get('allow_error_exit', [])
        # # Case 1: The command's exit code is in our list of allowed failures.
        # # This means the check is a success because the thing we were looking for wasn't found.
        # if result.returncode in allowed_error_codes:
        #     return "PASS"
        # #     return f"Command exited with code {result.returncode}."
        # # # Case 2: show the error if allowed_error_codes is empty.
        # if result.returncode != 0 and not allowed_error_codes:
        #     error_details = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
        #     if not error_details:
        #         error_details = "Unknown"
        #     return f"Command exited with code {result.returncode}. Details: {error_details}"
        
        # # # Case 3: The command succeeded and produced no output.
        # # if not result.stdout.strip():
        # #     return "__EMPTY_OUTPUT__"
        
        # # Case 4: The command succeeded and produced output.
        # return result.stdout.strip()
            
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"stdout": "", "stderr": f"ERROR: Command failed to execute. Reason: {e}", "exit_code": 127}