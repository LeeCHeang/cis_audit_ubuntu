import re
import logging  # <-- ADD THIS IMPORT
from audit_task import AuditTask
from functools import singledispatch

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m' # Yellow
    FAIL = '\03g[91m' # Red
    ENDC = '\033[0m' # Resets the color
    BOLD = '\033[1m'

def _get_common_data(task: AuditTask):
    """Helper function to extract data needed by all algorithms."""
    # logger = logging.getLogger()

    # Defensively check if actual_output is a dictionary before using it.
    if not isinstance(task.actual_output, dict):
        # logger.error(f"CRITICAL ERROR in _get_common_data for check {task.id}: task.actual_output was type {type(task.actual_output)}, not dict.")
        # Return values that will cause a clean failure.
        return "", -1, 0, []

    output_dict = task.actual_output
    stdout = output_dict.get("stdout", "")
    exit_code = output_dict.get("exit_code", -1)
    
    expected_exit_code = 0  # Default to 0
    
    # Log the type to see what's happening, then check if it's a dictionary before calling .get()
    # logger.debug(f"For check {task.id}, task.parameters is of type: {type(task.parameters)}")
    if isinstance(task.parameters, dict):
        expected_exit_code = int(task.parameters.get("success_code", 0))
    
    expected_conditions = [cond.strip() for cond in task.expected_value.split(';')] 
    return stdout, exit_code, expected_exit_code, expected_conditions

@singledispatch
def algorithm_null(task: AuditTask) -> bool:
    """Passes if the command exits with the expected success code and has no output."""
    stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
    return not bool(stdout)
# overload
@algorithm_null.register
def _(actual: str, expected: str ) -> bool:
    return not bool(actual)

@singledispatch
def algorithm_not_null(task: AuditTask) -> bool:
    """Passes if the command exits with the expected success code and has output."""
    stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
    return bool(stdout)
# overload
@algorithm_not_null.register
def _(actual: str, expected: str = '' ) -> bool:
    return bool(actual)

@singledispatch
def algorithm_exact(task: AuditTask) -> bool:
    """Passes if the command exits with the expected success code and output matches exactly."""
    stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
    return exit_code == expected_exit_code and any(condition.lower().split() == stdout.lower().split() for condition in expected_conditions)

@algorithm_exact.register
def _(actual: str, expected: str) -> bool:
    expected_conditions = [cond.strip() for cond in expected.split(';')]
    return any(condition.lower().split() == actual.lower().split() for condition in expected_conditions)

@singledispatch
def algorithm_contain(task: AuditTask) -> bool:
    """Passes if the command exits with the expected success code and output contains a substring."""
    stdout, exit_code, expected_exit_code, expected_conditions= _get_common_data(task)
    return exit_code == expected_exit_code and any(condition.lower().split() in stdout.lower().split() for condition in expected_conditions)

@algorithm_contain.register
def _(actual: str, expected: str) -> bool:
    expected_conditions = [cond.strip() for cond in expected.split(';')]
    return any(condition.lower().split() in actual.lower().split() for condition in expected_conditions)

@singledispatch
def algorithm_does_not_contain(task: AuditTask) -> bool:
    """Passes if the command exits with the expected success code and output contains a substring."""
    stdout, exit_code, expected_exit_code, expected_conditions= _get_common_data(task)
    return any(condition.lower() not in stdout.lower() for condition in expected_conditions)

@algorithm_does_not_contain.register
def _(actual: str, expected: str = '') -> bool:
    expected_conditions = [cond.strip() for cond in expected.split(';')] 
    return any(condition.lower() not in actual.lower() for condition in expected_conditions)

def algorithm_more_than(actual: str, expected: str) -> bool:
    try:
        return float(actual) > float(expected)
    except (ValueError, TypeError):
        return False # Cannot compare non-numeric values

def algorithm_less_than(actual: str, expected: str) -> bool:
    try:
        return float(actual) < float(expected)
    except (ValueError, TypeError):
        return False # Cannot compare non-numeric values

def algorithm_regex_match(actual: str, expected_pattern: str) -> bool:
    try:
        return bool(re.search(expected_pattern, actual, re.MULTILINE))
    except re.error:
        return False # Invalid regex pattern

def algorithm_manual(actual: str, expected: str) -> bool:
    return True # This function's result is handled specially in process_with_algorithm

def string_to_bool(s):
    s_lower = s.lower()
    if s_lower == 'true':
        return True
    elif s_lower == 'false':
        return False
    else:
        raise ValueError(f"Invalid boolean string: '{s}'")


# The dispatcher maps algorithm names from the CSV to the functions above
ALGORITHM_DISPATCHER = {
    'Exact': algorithm_exact,
    'Contain': algorithm_contain,
    'Does Not Contain': algorithm_does_not_contain,
    'Null': algorithm_null,
    'Not Null': algorithm_not_null,
    'More Than': algorithm_more_than,
    'Less Than': algorithm_less_than,
    'Regex Match': algorithm_regex_match,
    'Manual': algorithm_manual,
}
def condition():
    return 
    
def process_with_algorithm(task: AuditTask) -> str:
    # Case 1: The handler returned a structured list for a multi-step check
    if isinstance(task.actual_output, list):
        # A multi-procedure check logically requires a dictionary of parameters.
        if not isinstance(task.parameters, dict):
            return "ERROR: Multi-procedure check requires dictionary parameters, but received a list."
            
        step_definitions = task.parameters.get('steps')
        step_results = task.actual_output
        if not isinstance(step_definitions, list) or len(step_definitions) != len(step_results):
            return "ERROR: Malformed or missing 'steps' definition in CSV Parameters for this multi_procedure check."
        
        breakdown_results = []
        overall_pass = True

        for i, step_result in enumerate(task.actual_output):
            step_name = step_result.get('name', f"Step {i+1}")
            step_output = step_result.get('output', '')
            step_stdout = step_output.get('stdout','')
            step_definition = task.parameters.get('steps', [])[i]
            algorithm_name = step_definition.get('algorithm')
            expected_string = step_definition.get('expected_value', "")
            algorithm_func = ALGORITHM_DISPATCHER.get(algorithm_name)
            step_is_pass = False
            pass_stop_check = string_to_bool(step_definition.get('pass_stop_check', 'False'))
            error_status = False

            if "ERROR:" not in step_stdout and algorithm_func: 
                error_status = False
                step_is_pass = algorithm_func(step_stdout,expected_string)
            else:
                error_status = True

            if not step_is_pass and i == 0 and not pass_stop_check:
                overall_pass = False

            if not step_is_pass and i > 0 and not pass_stop_check:
                overall_pass = False

            if pass_stop_check and step_is_pass:
                overall_pass = True
                breakdown_results.append({
                    "name": step_name,
                    "status": "PASS" if step_is_pass else "ERROR",
                    "details": step_output
                })
                break
            else: 
                breakdown_results.append({
                    "name": step_name,
                    "status": "PASS" if step_is_pass else ( "ERROR" if error_status else "FAIL"),
                    "details": step_output
                })
        return {
            "overall_status": "PASS" if overall_pass else "FAIL",
            "breakdown": breakdown_results
        }

    # Case 2: The handler returned a simple string (original behavior)
    else:
        """Judges a task's result using the specified algorithm."""
        algorithm_func = ALGORITHM_DISPATCHER.get(task.algorithm)
        
        if "ERROR:" in str(task.actual_output):
            return f"ERROR"
        if not algorithm_func:
            return f"ERROR: Unknown algorithm '{task.algorithm}'"
            
        if task.algorithm == 'Manual':
            return "MANUAL"

        is_pass = algorithm_func(task)
        
        if is_pass:
            return "PASS"
        else:
            return "FAIL"