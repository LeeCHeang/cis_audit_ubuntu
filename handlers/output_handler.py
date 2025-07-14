# In cis_auditor_v3/handlers/output_handler.py
import re
import logging
from audit_task import AuditTask
from functools import singledispatch
from typing import Tuple

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def _get_common_data(task: AuditTask):
    if not isinstance(task.actual_output, dict):
        return "", -1, 0, []
    output_dict = task.actual_output
    stdout = output_dict.get("stdout", "")
    exit_code = output_dict.get("exit_code", -1)
    expected_exit_code = int(task.parameters.get("success_code", 0)) if isinstance(task.parameters, dict) else 0
    expected_conditions = [cond.strip() for cond in task.expected_value.split(';')] if task.expected_value else []
    return stdout, exit_code, expected_exit_code, expected_conditions

def algorithm_exact(task: AuditTask) -> bool:
    stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
    return exit_code == expected_exit_code and any(condition.lower().strip() == stdout.lower().strip() for condition in expected_conditions)

def algorithm_null(task: AuditTask) -> bool:
    stdout, exit_code, expected_exit_code, _ = _get_common_data(task)
    return not bool(stdout)

def algorithm_not_null(task: AuditTask) -> bool:
    stdout, exit_code, expected_exit_code, _ = _get_common_data(task)
    return bool(stdout)

def algorithm_contain(task: AuditTask) -> bool:
    stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
    # Normalize whitespace for better matching
    normalized_stdout = ' '.join(stdout.lower().split())
    # print(f"Normalized stdout: {normalized_stdout}")  # Debugging output
    # print(f"Expected conditions: {expected_conditions}")  # Debugging output
    for condition in expected_conditions:
        normalized_condition = ' '.join(condition.lower().split())
        if normalized_condition not in normalized_stdout:
            return False
    return True  # All conditions must be present

# def algorithm_contain_all_lines(task: AuditTask) -> bool:
#     stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
#     stdout_lines = [line.strip().lower() for line in stdout.split('\n') if line.strip()]
    
#     for condition in expected_conditions:
#         condition_lines = [line.strip().lower() for line in condition.split('\n') if line.strip()]
#         for expected_line in condition_lines:
#             if not any(expected_line in stdout_line for stdout_line in stdout_lines):
#                 return False
#     return True

def algorithm_does_not_contain(task: AuditTask) -> bool:
    stdout, exit_code, expected_exit_code, expected_conditions = _get_common_data(task)
    # return all(condition.lower() not in stdout.lower() for condition in expected_conditions)
    normalized_stdout = ' '.join(stdout.lower().split())
    # print(f"Normalized stdout: {normalized_stdout}")  # Debugging output
    # print(f"Expected conditions: {expected_conditions}")  # Debugging output
    for condition in expected_conditions:
        normalized_condition = ' '.join(condition.lower().split())
        if normalized_condition in normalized_stdout:
            return False
    return True  # All conditions must be present


ALGORITHM_DISPATCHER = {
    'Exact': algorithm_exact,
    'Contain': algorithm_contain,
    # new algorithms but have not been tested yet
    # 'Contain All Lines': algorithm_contain_all_lines,
    'Does Not Contain': algorithm_does_not_contain,
    'Null': algorithm_null,
    'Not Null': algorithm_not_null,
}


def _judge_simple_check(task: AuditTask) -> dict:
    status_str = "FAIL"  # Default status
    reason_str = "Condition not met." # Default reason
    raw_output = task.actual_output
    error_str = raw_output.get('stderr', "Unknown Error output. Cuz output is empty")

    if not isinstance(raw_output, dict) or "exit_code" not in raw_output:
        status_str = "ERROR"
        error_str = raw_output.get('stderr')
        reason_str = "Malformed evidence from handler. Expected dict with 'exit_code'."
    elif raw_output.get("exit_code") == 127:
        status_str = "ERROR"
        reason_str = f"Command not found. Stderr: {raw_output.get('stderr')}"
    else:
        algorithm_func = ALGORITHM_DISPATCHER.get(task.algorithm)
        if not algorithm_func:
            status_str = "ERROR"
            reason_str = f"Unknown algorithm specified: '{task.algorithm}'"
        else:
            if algorithm_func(task):
                status_str = "PASS"
                # reason_str = "Check passed successfully."
                reason_str = f"Check passed successfully for algorithm '{task.algorithm}' with expected value '{task.expected_value}'."
            else:
                status_str = "FAIL"
                reason_str = f"Check failed for algorithm '{task.algorithm}' with expected value '{task.expected_value}'."
    
    return {
        "type": "action_node",
        "title": task.title,
        "overall_status": status_str, # Guaranteed to be a string
        "details": {"reason": reason_str,"error":error_str, "evidence": raw_output}
    }

def _judge_evidence_tree_recursive(node: dict) -> dict:
    if "logic" in node:
        logic = node.get("logic", "AND").upper()
        is_passed, has_error = (logic == "AND"), False
        child_results = []
        for sub_node in node.get("steps", []):
            sub_result_obj = _judge_evidence_tree_recursive(sub_node)
            child_results.append(sub_result_obj)
            sub_verdict = sub_result_obj.get("overall_status")
            if sub_verdict == "ERROR": has_error = True
            if sub_verdict == "PASS" and str(sub_node.get('pass_stop_check', 'false')).lower() == 'true':
                is_passed = True; break
            if logic == "AND" and sub_verdict != "PASS": is_passed = False
            if logic == "OR" and sub_verdict == "PASS": is_passed = True; break
        final_status = "ERROR" if has_error else ("PASS" if is_passed else "FAIL")
        return {"type": "logic_node", "logic": logic, "overall_status": final_status, "steps_results": child_results}
    else:
        sub_task = AuditTask(
            algorithm=node.get('algorithm'), expected_value=node.get('expected_value'),
            actual_output=node.get('raw_evidence'), parameters=node.get('params'),
            title=node.get('title', 'Untitled Step'),
            id='', level='', profile=[], domain='', check_type='', target=''
        )
        return _judge_simple_check(sub_task)

def process_with_algorithm(task: AuditTask) -> dict:
    if isinstance(task.actual_output, dict) and "error" in task.actual_output:
        return {"overall_status": "ERROR", "type": "action_node", "title": task.title, "details": task.actual_output}
    if isinstance(task.actual_output, dict) and task.actual_output.get("is_unified_logic_payload"):
        payload = task.actual_output
        evidence_tree = payload.get("evidence_tree", [])
        top_level_logic = payload.get("logic", "AND")
        if not top_level_logic: top_level_logic = "AND"
        if not evidence_tree: return {"overall_status": "ERROR", "type": "action_node", "title": task.title, "details": "Logic tree empty."}
        root_node = {"logic": top_level_logic, "steps": evidence_tree}
        return _judge_evidence_tree_recursive(root_node)
    else:
        return _judge_simple_check(task)