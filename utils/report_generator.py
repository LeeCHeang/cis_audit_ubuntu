import datetime
import os
import csv
from typing import List, Dict, Any
from audit_task import AuditTask
import logging
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def _print_rich_report_recursive(node: Dict[str, Any],log_level: str, prefix: str = "", is_last: bool = True):
    connector = "   └─ " if is_last else "   ├─ "
    status = node.get("overall_status", "ERROR")
    status_color = Colors.OKGREEN if status == "PASS" else (Colors.FAIL if status == "FAIL" else Colors.WARNING)

    if node.get("type") == "logic_node":
        logic = node.get("logic")
        print(f"{prefix}{connector}[{status_color}**{Colors.ENDC}] LOGIC GROUP ({logic})")
    else:
        title = node.get("title", "Untitled Step")
        print(f"{prefix}{connector}[{status_color}*{status}*{Colors.ENDC}] STEP: {title}")
    
    child_prefix = prefix + ("    " if is_last else "   │")

    if (log_level == 'DEBUG' or status != "PASS") and node.get("type") == "action_node":
        details = node.get("details", {})
        reason, error, evidence = details.get("reason"), details.get("error"), details.get("evidence")

        if error:
            print(f"{child_prefix}     └─ Reason: {error}")
            if log_level == 'DEBUG':
                print(f"{child_prefix}          └─ Details_Output: {evidence}")
        elif reason:
            print(f"{child_prefix}     └─ Reason: {reason}")
            if log_level == 'DEBUG':
                print(f"{child_prefix}          └─ Details_Output: {evidence}")
        else: # Fallback
            print(f"{child_prefix}       └─ Details: {details}")

    steps_results = node.get("steps_results", [])
    for i, step in enumerate(steps_results):
        _print_rich_report_recursive(step,log_level, child_prefix, i == len(steps_results) - 1)

def generate_summary_report(tasks: List[AuditTask], log_level: str = 'INFO'):
    pass_count = len([t for t in tasks if (isinstance(t.final_result, dict) and t.final_result.get("overall_status") == "PASS") or t.final_result == "PASS"])
    fail_count = len([t for t in tasks if (isinstance(t.final_result, dict) and t.final_result.get("overall_status") == "FAIL") or t.final_result == "FAIL"])
    error_count = len([t for t in tasks if (isinstance(t.final_result, dict) and t.final_result.get("overall_status") == "ERROR") or t.final_result == "ERROR"])

    print("\n" + Colors.BOLD + "="*25 + " AUDIT SUMMARY " + "="*25 + Colors.ENDC)
    print(f"Report Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Checks Run: {len(tasks)}")
    results_line = (f"RESULTS: {Colors.OKGREEN}{pass_count} Passed{Colors.ENDC}, "
                    f"{Colors.FAIL}{fail_count} Failed{Colors.ENDC}, "
                    f"{Colors.WARNING}{error_count} Errored{Colors.ENDC}.")
    print(Colors.BOLD + results_line + Colors.ENDC)
    print(f"{Colors.BOLD}="*67 + Colors.ENDC)
    
    if log_level == 'DEBUG':
        print(f"\nDETAILS FOR ALL CHECKS (DEBUG MODE):\n")
    elif fail_count > 0 or error_count > 0:
        print(f"\nDETAILS OF FAILED AND ERRORED CHECKS:\n")

    for task in tasks:
        final_result_obj = task.final_result
        simple_status = final_result_obj.get("overall_status") if isinstance(final_result_obj, dict) else final_result_obj
        if log_level == 'DEBUG' or simple_status != "PASS":
            status_color = Colors.OKGREEN if simple_status == "PASS" else (Colors.FAIL if simple_status == "FAIL" else Colors.WARNING)
            print(f"[{status_color}{simple_status}{Colors.ENDC}] - ID: {task.id} - {task.title}")
            if isinstance(final_result_obj, dict) and final_result_obj.get("type") in ["logic_node", "action_node"]:
                _print_rich_report_recursive(final_result_obj, log_level)
            elif isinstance(final_result_obj, dict):
                print(f"  └─ Details: {final_result_obj.get('details', 'No details available.')}")
            else:
                print(f"  └─ Details: {task.actual_output}")
    
    # --- File saving logic ---
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    file_report_path = os.path.join(report_dir, "audit_summary_report.txt")
    print(f"\nFull summary report saved to '{file_report_path}'")

# This is the separate function for generating the CSV report.
def generate_csv_report(tasks: List[AuditTask]):
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_filename = f"audit_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    report_path = os.path.join(report_dir, report_filename)
    headers = ['ID', 'Title', 'Result', 'Details']
    
    try:
        with open(report_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for task in tasks:
                final_result_obj = task.final_result
                simple_status = final_result_obj.get("overall_status") if isinstance(final_result_obj, dict) else final_result_obj
                details = str(task.actual_output)
                if isinstance(final_result_obj, dict):
                    # For CSV, we dump the whole rich object for maximum detail
                    details = str(final_result_obj)
                    
                writer.writerow({
                    'ID': task.id,
                    'Title': task.title,
                    'Result': simple_status,
                    'Details': details
                })
        print(f"Detailed CSV report saved to '{report_path}'")
    except Exception as e:
        print(f"ERROR: Could not write CSV report. Reason: {e}")

# This is the separate function for generating the CSV report.
def generate_csv_report(tasks: List[AuditTask]):
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_filename = f"audit_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    report_path = os.path.join(report_dir, report_filename)
    headers = ['ID', 'Title', 'Result', 'Details']
    
    try:
        with open(report_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for task in tasks:
                final_result_obj = task.final_result
                simple_status = final_result_obj.get("overall_status") if isinstance(final_result_obj, dict) else final_result_obj
                details = str(task.actual_output)
                if isinstance(final_result_obj, dict):
                    # For CSV, we dump the whole rich object for maximum detail
                    details = str(final_result_obj)
                    
                writer.writerow({
                    'ID': task.id,
                    'Title': task.title,
                    'Result': simple_status,
                    'Details': details
                })
        print(f"Detailed CSV report saved to '{report_path}'")
    except Exception as e:
        print(f"ERROR: Could not write CSV report. Reason: {e}")