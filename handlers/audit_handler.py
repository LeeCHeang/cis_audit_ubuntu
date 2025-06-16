import logging
import importlib
from typing import List
from audit_task import AuditTask
from handlers.output_handler import process_with_algorithm

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m' # Yellow
    FAIL = '\033[91m' # Red
    ENDC = '\033[0m' # Resets the color
    BOLD = '\033[1m'
    CYAN = "\x1b[36;1m"    # ANSI code for cyan/sky blue
    BOLD_RED = "\x1b[31;1m"
    ORANGE = '\033[38;2;255;165;0m'

class AuditHandler:
    def __init__(self):
        self.logger = logging.getLogger()

    # It now accepts 'log_level' from main.py
    def run_audit(self, tasks: List[AuditTask], log_level: str = 'INFO') -> List[AuditTask]:
        self.logger.info(f"Starting audit with {len(tasks)} tasks.")
        
        for task in tasks:
            task.status = "RUNNING"
            self.logger.info(f"{Colors.ORANGE}Executing check: [{task.id}] {task.title}{Colors.ENDC}")
            
            try:
                handler_module_name = f"handlers.check_handlers.{task.check_type}_handler"
                handler_module = importlib.import_module(handler_module_name)

                
                execute_func = None
                # If we are in DEBUG mode, try to find a function named 'debug' first.
                if log_level == 'DEBUG':
                    execute_func = getattr(handler_module, 'debug', None)
                
                # If we're not in debug mode, or if a 'debug' function wasn't found,
                # fall back to the standard 'handle' function.
                if not execute_func:
                    execute_func = getattr(handler_module, 'handle')
                # If the check we are running is the multi_procedure check...
                # if task.check_type == 'multi_procedure':
                #     # ...then we call its handler with the special third argument.
                #     raw_value = execute_func(task.target, task.parameters, handler_module)

                # else:
                    # Otherwise, we call all other handlers normally with two arguments.
                    raw_value = execute_func(task.target, task.parameters)

                task.actual_output = raw_value
                # print(raw_value)
                task.final_result = process_with_algorithm(task)

            except ImportError:
                task.final_result = "ERROR"
                task.actual_output = f"Check handler module not found: '{handler_module_name}.py'. Please create this file."
            except AttributeError:
                task.final_result = "ERROR"
                task.actual_output = f"Handler module '{handler_module_name}.py' must contain a 'handle' function."
            except Exception as e:
                task.final_result = "ERROR"
                task.actual_output = f"An unexpected error occurred in handler '{task.check_type}': {e}"
            
            task.status = "COMPLETED"

            simple_status = task.final_result
            if isinstance(simple_status, dict):
                simple_status = simple_status.get("overall_status")
            if "Overall Result: PASS" in simple_status:
                simple_status = "PASS"
            elif "Overall Result: FAIL" in simple_status:
                simple_status = "FAIL"
                
            # self.logger.info(f"Finished check: [{task.id}] - Result: {task.final_result}")
            case_color = Colors.OKGREEN if simple_status == "PASS" else Colors.FAIL if simple_status == "FAIL" else Colors.WARNING
            self.logger.info(f"{Colors.BOLD}Finished check:{Colors.ENDC} [{task.id}] {Colors.BOLD_RED}-{Colors.ENDC} {Colors.BOLD}Result:{Colors.ENDC} [{case_color}{simple_status}{Colors.ENDC}]")

        self.logger.info(f"{Colors.CYAN}AUDIT RUN HAS BEEN COMPLETED.{Colors.ENDC}")
        return tasks
        #         task.status = "COMPLETED"
        #         self.logger.info(f"Finished check: [{task.id}] - Result: {task.final_result}")
        #         case_color = Colors.OKGREEN if task.final_result == "PASS" else Colors.FAIL if task.final_result == "FAIL" else Colors.WARNING
        #         self.logger.info(f"{Colors.BOLD}Finished check:{Colors.ENDC} [{task.id}] {Colors.BOLD_RED}-{Colors.ENDC} {Colors.BOLD}Result:{Colors.ENDC} [{case_color}{task.final_result}{Colors.ENDC}]")

        # self.logger.info(f"{Colors.CYAN}\n\n\tAUDIT RUN HAS BEEN COMPLETED.{Colors.ENDC}")
        # return tasks