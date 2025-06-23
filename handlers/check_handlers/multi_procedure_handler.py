import importlib
import os
import subprocess
from typing import List, Dict

def handle(target: str, params: dict) -> List[Dict]:
    steps = params.get('steps')
    if not isinstance(steps, list):
        return [{'name': 'Handler Error', 'output': "ERROR: 'steps' parameter must be a list."}]

    results = []
    for step in steps:
        step_name = step.get('name', 'Unnamed Step')
        step_type = step.get('type', 'command')
        step_output = ""
        try:
            # Case 1: Execute a raw shell command
            if step_type == 'command':
                command = step.get('command')
                command_to_run = ['/bin/bash', '-c', command]
                # proc = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
                proc = subprocess.run(command_to_run, capture_output=True, text=True, check=False)
                # if proc.returncode != 0:
                #     # step_output = f"ERROR: Command exited with code {proc.returncode}. Details: {proc.stderr.strip()}"
                step_output = {
                    "stdout": proc.stdout.strip(),
                    "stderr": proc.stderr.strip(),
                    "exit_code": proc.returncode
                }
            # else:
                #     # step_output = proc.stdout.strip() if proc.stdout.strip() else "__EMPTY_OUTPUT__"
                #     step_output = {
                #         "stdout": proc.stdout.strip(),
                #         "stderr": proc.stderr.strip(),
                #         "exit_code": proc.returncode
                #     }
            
            # Case 2: Execute a script from the functions/ directory
            elif step_type == 'script':
                script_name = step.get('target_script')
                script_path = os.path.abspath(f"functions/{script_name}")
                if not os.path.exists(script_path):
                    # step_output = f"ERROR: Script file '{script_name}' not found."
                    step_output= {
                        "stdout": '',
                        "stderr": f"Script file '{script_name}' not found.",
                        "exit_code": proc.returncode
                    }
                else:
                    script_args = step.get('script_params', [])
                    proc = subprocess.run(['bash', script_path] + script_args, capture_output=True, text=True, check=False)
                    if proc.returncode != 0:
                        # step_output = f"ERROR: Script exited with code {proc.returncode}. Details: {proc.stderr.strip()}"
                        step_output= {
                            "stdout": '',
                            "stderr": proc.stderr.strip(),
                            "exit_code": proc.returncode
                        }
                    else:
                        # step_output = proc.stdout.strip() if proc.stdout.strip() else "__EMPTY_OUTPUT__"
                        step_output= {
                            "stdout": proc.stdout.strip(),
                            "stderr": proc.stderr.strip(),
                            "exit_code": proc.returncode
                        }

            # Case 3: Call another Python handler
            # this feature should not work on because we need to call the audit_handler inside here which is not good 
            elif step_type == 'handler':
                target_handler_name = step.get('target_handler')
                
                target_handler_module_name = f"handlers.check_handlers.{target_handler_name}_handler"

                # just import the module lib to here
                target_handler_module = importlib.import_module(target_handler_module_name)

                if not target_handler_module:
                    step_output = f"ERROR: Target handler '{target_handler_name}' not found in dispatcher."
                else:
                    handler_params = step.get('handler_params', {})
                    h_target = handler_params.get('target', '')
                    h_params = handler_params.get('params', {})
                    # Call the other handler function
                    sub_execute_func = getattr(target_handler_module, 'handle')
                    step_output = sub_execute_func(h_target, h_params)
            else:
                step_output = f"ERROR: Unknown step type '{step_type}'."
            
            results.append({'name': step_name, 'output': step_output})

        except Exception as e:
            results.append({'name': step_name, 'output': f"ERROR: An unexpected exception occurred: {e}"})
            
    return results