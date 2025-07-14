# In cis_auditor_v3/handlers/audit_handler.py
import logging
import importlib
from typing import List
from audit_task import AuditTask
# We must import the Judge function here to be used by the handler
from handlers.output_handler import process_with_algorithm

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    CYAN = "\x1b[36;1m"
    BOLD_RED = "\x1b[31;1m"
    ORANGE = '\033[38;2;255;165;0m'

class AuditHandler:
    def __init__(self):
        self.logger = logging.getLogger()

    def run_audit(self, tasks: List[AuditTask], log_level: str = 'INFO') -> List[AuditTask]:
        self.logger.info(f"Starting audit with {len(tasks)} tasks.")
        
        for task in tasks:
            task.status = "RUNNING"
            self.logger.info(f"{Colors.ORANGE}Executing check: [{task.id}] {task.title}{Colors.ENDC}")
            
            try:
                # This line correctly uses task.check_type to find the handler module.
                if not task.check_type:
                    raise ValueError("Task has no 'check_type' defined. Please check CSV headers and data.")
                
                handler_module_name = f"handlers.check_handlers.{task.check_type}_handler"
                
                handler_module = importlib.import_module(handler_module_name)
                execute_func = getattr(handler_module, 'handle')

                # The handler collects the evidence payload
                raw_value = execute_func(task.target, task.parameters)
                task.actual_output = raw_value

                # The Judge makes the final decision
                task.final_result = process_with_algorithm(task)

            except Exception as e:
                # Create a standard error object if anything goes wrong during this process
                task.final_result = {"overall_status": "ERROR", "type":"action_node", "details": {"error":f"Audit Handler Error: {e}"}}
            
            task.status = "COMPLETED"


            # case_color = Colors.OKGREEN if simple_status == "PASS" else Colors.FAIL if simple_status == "FAIL" else Colors.WARNING

            final_result_obj = task.final_result
            if isinstance(final_result_obj, dict):
                simple_status = final_result_obj.get("overall_status", "ERROR")
            elif isinstance(final_result_obj, str):
                simple_status = final_result_obj
           
            # Use the correct log level based on the final status.
            if simple_status == "ERROR":
                # Log as an ERROR, but keep the message simple. The report will have the details.
                self.logger.error(f"{Colors.BOLD}Finished check:{Colors.ENDC} [{task.id}] - {Colors.BOLD}Result:{Colors.ENDC} [{Colors.WARNING}ERROR{Colors.ENDC}]")
            else:
                case_color = Colors.OKGREEN if simple_status == "PASS" else Colors.FAIL
                self.logger.info(f"{Colors.BOLD}Finished check:{Colors.ENDC} [{task.id}] - {Colors.BOLD}Result:{Colors.ENDC} [{case_color}{simple_status}{Colors.ENDC}]")


        self.logger.info(f"{Colors.CYAN}AUDIT RUN HAS BEEN COMPLETED.{Colors.ENDC}")
        return tasks