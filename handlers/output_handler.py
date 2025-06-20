import re
from audit_task import AuditTask
from functools import singledispatch
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m' # Yellow
    FAIL = '\033[91m' # Red
    ENDC = '\033[0m' # Resets the color
    BOLD = '\033[1m'

def _get_common_data(task: AuditTask):
    """Helper function to extract data needed by all algorithms."""
    # print(task.actual_output)
    output_dict = task.actual_output
    stdout = output_dict.get("stdout", "")
    exit_code = output_dict.get("exit_code", -1)
    # Get the expected success code from params, defaulting to 0.
    expected_exit_code = int(task.parameters.get("success_code", 0))
    expected_conditions = [cond.strip() for cond in task.expected_value.split(';')] 
    return stdout, exit_code, expected_exit_code, expected_conditions

@singledispatch
def algorithm_null(task: AuditTask) -> bool:
    """Passes if the command exits with the expected success code and has no output."""
    stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
    # The check passes if the exit code matches what we expect for success AND stdout is empty.
    # return exit_code == expected_exit_code and not bool(stdout)
    return not bool(stdout)
# overload
@algorithm_null.register
def _(actual: str, expected: str ) -> bool:
    return not bool(actual)

@singledispatch
def algorithm_not_null(task: AuditTask) -> bool:
    """Passes if the command exits with the expected success code and has output."""
    stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
    # return exit_code == expected_exit_code and bool(stdout)
    return bool(stdout)
# overload
@algorithm_not_null.register
def _(actual: str, expected: str = '' ) -> bool:
    return bool(actual)

@singledispatch
def algorithm_exact(task: AuditTask) -> bool:
    """Passes if the command exits with the expected success code and output matches exactly."""
    stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
    # expected = False 
    # for condition in expected_conditions:
    #     if condition.lower() == stdout.lower():
    #         expected = True 
    #         break
    # return exit_code == expected_exit_code and expected
    return exit_code == expected_exit_code and any(condition.lower() == stdout.lower() for condition in expected_conditions)

@algorithm_exact.register
def _(actual: str, expected: str) -> bool:
    expected_conditions = [cond.strip() for cond in expected.split(';')]
    # return actual.lower() == expected.lower()

    return any(condition.lower() == actual.lower() for condition in expected_conditions)

@singledispatch
def algorithm_contain(task: AuditTask) -> bool:
    """Passes if the command exits with the expected success code and output contains a substring."""
    stdout, exit_code, expected_exit_code, expected_conditions= _get_common_data(task)
    # expected = False 
    # for condition in expected_conditions:
    #     if condition.lower() in stdout.lower():
    #         expected = True 
    #         break
    # return exit_code == expected_exit_code and expected
    return exit_code == expected_exit_code and any(condition.lower() in stdout.lower() for condition in expected_conditions)

@algorithm_contain.register
def _(actual: str, expected: str) -> bool:
#     # return print(f"Checking if '{Colors.FAIL}{expected}{Colors.ENDC}' is in '{Colors.OKGREEN}{actual}{Colors.ENDC}'")
    expected_conditions = [cond.strip() for cond in expected.split(';')]
    # print(expected_conditions)

    # return expected.lower() in actual.lower()
    return any(condition.lower() in actual.lower() for condition in expected_conditions)

@singledispatch
def algorithm_does_not_contain(task: AuditTask) -> bool:
    """Passes if the command exits with the expected success code and output contains a substring."""
    stdout, exit_code, expected_exit_code, expected_conditions= _get_common_data(task)
    # return exit_code == expected_exit_code and any(condition.lower() in stdout.lower() for condition in expected_conditions)
    return any(condition.lower() not in stdout.lower() for condition in expected_conditions)

@algorithm_does_not_contain.register
def _(actual: str, expected: str = '') -> bool:
    expected_conditions = [cond.strip() for cond in expected.split(';')] 
    # return expected.lower() not in actual.lower()
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
        step_definitions = task.parameters.get('steps')
        step_results = task.actual_output
        # Ensure the 'steps' definition exists and matches the number of results
        if not isinstance(step_definitions, list) or len(step_definitions) != len(step_results):
            return "ERROR: Malformed or missing 'steps' definition in CSV Parameters for this multi_procedure check."
        # detailed_results = []
        breakdown_results = []
        overall_pass = True

        for i, step_result in enumerate(task.actual_output):
            step_name = step_result.get('name', f"Step {i+1}")
            step_output = step_result.get('output', '')
            # getting the sub set of the step_output
            step_stdout = step_output.get('stdout','')
            # Get the corresponding step definition from the original parameters
            step_definition = task.parameters.get('steps', [])[i]
            algorithm_name = step_definition.get('algorithm')
            expected_string = step_definition.get('expected_value', "")

            # check to see if there mulit expected condition 
            algorithm_func = ALGORITHM_DISPATCHER.get(algorithm_name)
            step_is_pass = False

            # CheckPoint condition for main condition
            pass_stop_check = string_to_bool(step_definition.get('pass_stop_check', 'False'))
            # Checking for error so when fail it show error
            error_status = False
            # print(overall_pass)
            if "ERROR:" not in step_stdout and algorithm_func: 
                error_status = False
                step_is_pass = algorithm_func(step_stdout,expected_string)
            else:
                error_status = True
            # if not step_is_pass:
            #     overall_pass = False
            # sip = True => False and if psc 
            if not step_is_pass and i == 0 and not pass_stop_check:
                overall_pass = False

            if not step_is_pass and i > 0 and not pass_stop_check:
                overall_pass = False
            # Append a structured dictionary for this step
            # if pass_stop_check and step_is_pass and i == 0:
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
                    # "status": "PASS" if step_is_pass else "FAIL",
                    "details": step_output
                })

            # if not step_is_pass:
            #     overall_pass = False

            # breakdown_results.append({
            #     "name": step_name,
            #     "status": "PASS" if step_is_pass else ( "ERROR" if error_status else "FAIL"),
            #     # "status": "PASS" if step_is_pass else "FAIL",
            #     "details": step_output
            # })
        # Return a final dictionary, not a formatted string
        return {
            "overall_status": "PASS" if overall_pass else "FAIL",
            "breakdown": breakdown_results
        }
        #     if "ERROR:" in step_output or not algorithm_func:
        #         step_is_pass = False
        #     else:
        #         step_is_pass = algorithm_func(step_output, expected_value)
            
        #     if step_is_pass:
        #         detailed_results.append(f"  - {step_name}: [PASS]")
        #     else:
        #         detailed_results.append(f"  - {step_name}: [FAIL]\n    └─ Details: {step_output}")
        #         overall_pass = False
        
        # final_status_str = "Overall Result: PASS" if overall_pass else "Overall Result: FAIL"
        # # Return the full, formatted breakdown as the final output
        # # print(detailed_results)
        # return f"{final_status_str}\n--- Breakdown ---\n" + "\n".join(detailed_results)

    # Case 2: The handler returned a simple string (original behavior)
    else:
        """Judges a task's result using the specified algorithm."""
        algorithm_func = ALGORITHM_DISPATCHER.get(task.algorithm)
        
        if "ERROR:" in str(task.actual_output):
            # return f"{Colors.WARNING}ERROR{Colors.ENDC}"
            return f"ERROR"
        if not algorithm_func:
            # return f"{Colors.BOLD}{Colors.WARNING}ERROR: Unknown algorithm '{task.algorithm}'{Colors.ENDC}"
            return f"ERROR: Unknown algorithm '{task.algorithm}'"
            
        # Handle the 'Manual' case separately
        if task.algorithm == 'Manual':
            # return f"{Colors.WARNING}MANUAL{Colors.ENDC}"
            return "MANUAL"

        # Execute the algorithm and return PASS or FAIL
        # is_pass = algorithm_func(task.actual_output, task.expected_value)
        is_pass = algorithm_func(task)
        # print(is_pass)
        # print(task.actual_output)
        # print(task)
        if is_pass:
            # return f"{Colors.OKGREEN}PASS{Colors.ENDC}"
            return "PASS"
        else:
            # return f"{Colors.FAIL}FAIL{Colors.ENDC}"
            return "FAIL"