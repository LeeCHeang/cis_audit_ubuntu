import datetime
import os
import csv # Import the csv module
from typing import List
from audit_task import AuditTask
# Add this Colors class at the top of the file
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m' # Yellow
    FAIL = '\033[91m' # Red
    ENDC = '\033[0m' # Resets the color
    BOLD = '\033[1m'

# The generate_summary_report function remains the same...
def generate_summary_report(tasks: List[AuditTask]):
    pass_count = 0
    fail_count = 0
    error_count = 0

    for task in tasks:
        result = task.final_result
        status = result.get("overall_status") if isinstance(result, dict) else result
        if status == "PASS":
            pass_count += 1
        elif status == "FAIL":
            fail_count += 1
        elif status == "ERROR":
            error_count += 1
    # pass_count = len([t for t in tasks if t.final_result == "PASS"])
    # fail_count = len([t for t in tasks if t.final_result == "FAIL"])
    # error_count = len([t for t in tasks if t.final_result == "ERROR"])
    # pass_count = len([t for t in tasks if t.final_result == f"{Colors.OKGREEN}PASS{Colors.ENDC}"])
    # fail_count = len([t for t in tasks if t.final_result == f"{Colors.FAIL}FAIL{Colors.ENDC}"])
    # error_count = len([t for t in tasks if t.final_result == f"{Colors.BOLD}{Colors.WARNING}ERROR{Colors.ENDC}"])

    # Build the report string for the file (without colors)
    report_lines = []
    report_lines.append("="*25 + " AUDIT SUMMARY " + "="*25)
    report_lines.append(f"Report Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Total Checks Run: {len(tasks)}")
    report_lines.append(f"RESULTS: {pass_count} Passed, {fail_count} Failed, {error_count} Errored.")
    report_lines.append("="*67)
    report_lines.append("\nDETAILS OF FAILED AND ERRORED CHECKS:\n")

    # --- Print colored output to the console ---
    print("\n" + Colors.BOLD + "="*25 + " AUDIT SUMMARY " + "="*25 + Colors.ENDC)
    print(f"Report Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total Checks Run: {len(tasks)}")
    
    # Format the results line with colors
    results_line = (
        f"RESULTS: {Colors.OKGREEN}{pass_count} Passed{Colors.ENDC}, "
        f"{Colors.FAIL}{fail_count} Failed{Colors.ENDC}, "
        f"{Colors.WARNING}{error_count} Errored{Colors.ENDC}."
    )
    print(Colors.BOLD + results_line + Colors.ENDC)
    print(f"{Colors.BOLD}="*67 + Colors.ENDC)
    
    print(f"\nDETAILS OF FAILED AND ERRORED CHECKS:\n")
    report_lines.append("\nDETAILS OF FAILED AND ERRORED CHECKS:\n")

    # for task in tasks:
    #     if task.final_result != "PASS":
    #         # status_color = Colors.FAIL if task.final_result == "FAIL" else Colors.WARNING
            
    #         # # Colored line for the console
    #         # print(f"[{status_color}{task.final_result}{Colors.ENDC}] - ID: {task.id} - {task.title}")
    #         # print(f"    └─ Details: {task.actual_output}")
            
    #         # # Uncolored line for the file report
    #         # report_lines.append(f"[{task.final_result}] - ID: {task.id} - {task.title}")
    #         # report_lines.append(f"    └─ Details: {task.actual_output}")
    #         # Case 1: The result is a complex, multi-line breakdown
    #         if "Overall Result:" in task.final_result:
    #             # The final_result from the handler is already formatted with PASS/FAIL
    #             # and contains the full breakdown. We just need to color it.
    #             if "FAIL" in task.final_result:
    #                 colored_output = task.final_result.replace("Overall Result: FAIL", f"{Colors.FAIL}Overall Result: FAIL{Colors.ENDC}")
    #             else: # Handle ERROR cases if any
    #                 colored_output = task.final_result.replace("Overall Result: ERROR", f"{Colors.WARNING}Overall Result: ERROR{Colors.ENDC}")

    #             print(f"[{task.id}] - {task.title}")
    #             print(colored_output) # Print the pre-formatted, colored breakdown

    #         # Case 2: It's a simple, single-line result
    #         else:
    #             status_color = Colors.FAIL if task.final_result == "FAIL" else Colors.WARNING
    #             print(f"[{status_color}{task.final_result}{Colors.ENDC}] - ID: {task.id} - {task.title}")
    #             print(f"    └─ Details: {task.actual_output}")
    ################################## tring multip
    # for task in tasks:
    #     # Determine the simple status (PASS, FAIL, ERROR)
    #     simple_status = task.final_result
    #     if "Overall Result: PASS" in simple_status: simple_status = "Overall Result: ** PASS **"
    #     if "Overall Result: FAIL" in simple_status: simple_status = "Overall Result: ** FAIL **"

    #     if simple_status not in "Overall Result: ** PASS **":
    #         status_color = Colors.FAIL if simple_status in "Overall Result: ** FAIL **" else Colors.WARNING

    #         # Print the main header for the failed check
    #         print(f"[{status_color}{simple_status}{Colors.ENDC}] - ID: {task.id} - {task.title}")
    #         report_lines.append(f"[{simple_status}] - ID: {task.id} - {task.title}")
            
    #         # Now, intelligently print the details
    #         # Case 1: It's a complex multi-step check
    #         if isinstance(task.actual_output, list):
    #             # 'actual_output' is the list of dictionaries from the handler
    #             for step in task.actual_output:
    #                 step_name = step.get('name', 'Unnamed Step')
    #                 step_output = step.get('output', '')
                    
    #                 # Determine step status for color
    #                 # print("========================================")
    #                 # print(task.final_result)
    #                 # print("========================================")
    #                 step_status_str = "PASS" if "__EMPTY_OUTPUT__" in step_output or "PASS" in step_output else "FAIL"
    #                 step_status_color = Colors.OKGREEN if step_status_str == "PASS" else Colors.FAIL

    #                 # Print formatted sub-step details to console
    #                 print(f"    ├─ [{step_status_color}{step_status_str}{Colors.ENDC}] {step_name}")
    #                 if "FAIL" in step_status_str:
    #                      print(f"    │   └─ Details: {step_output}")
                    
    #                 # Add uncolored sub-step details to the report file
    #                 report_lines.append(f"    ├─ [{step_status_str}] {step_name}")
    #                 if "FAIL" in step_status_str:
    #                     report_lines.append(f"    │   └─ Details: {step_output}")

    #         # Case 2: It's a simple check with a single string output
    #         else:
    #             print(f"    └─ Details: {task.actual_output}")
    #             report_lines.append(f"    └─ Details: {task.actual_output}")
    
    for task in tasks:
        final_result = task.final_result
        
        # Determine the simple status word for the header line
        simple_status = final_result.get("overall_status") if isinstance(final_result, dict) else final_result
        
        if simple_status != "PASS":
            status_color = Colors.FAIL if simple_status == "FAIL" else Colors.WARNING
            header_line = f"[{status_color}{simple_status}{Colors.ENDC}] - ID: {task.id} - {task.title}"
            print(header_line)
            report_lines.append(f"[{simple_status}] - ID: {task.id} - {task.title}")
            
            # --- NEW LOGIC for printing details ---
            # If the result is a dictionary, format the breakdown
            if isinstance(final_result, dict):
                for step in final_result.get("breakdown", []):
                    step_status = step.get("status")
                    step_color = Colors.OKGREEN if step_status == "PASS" else (Colors.FAIL if step_status == "FAIL" else Colors.WARNING)
                    
                    line1 = f"    ├─ [{step_color}{step_status}{Colors.ENDC}] {step.get('name')}"
                    print(line1)
                    report_lines.append(line1.replace(step_color, "").replace(Colors.ENDC, "")) # Add uncolored to file
                    
                    # if step_status == "FAIL" or step_status == "ERROR":
                    if step_status != "PASS":
                        line2 = f"    │   └─ Details: {step.get('details')}"
                        print(line2)
                        report_lines.append(line2)
            # Otherwise, it's a simple result, print the raw output
            else:
                details_line = f"    └─ Details: {task.actual_output}"
                print(details_line)
                report_lines.append(details_line)





    # Save the uncolored report to the file
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "audit_summary_report.txt")
    with open(report_path, "w", encoding='utf-8') as f:
        f.write("\n".join(report_lines))
    print(f"\nFull summary report saved to '{report_path}'")



def generate_csv_report(tasks: List[AuditTask]):
    report_dir = "reports"
    os.makedirs(report_dir, exist_ok=True)
    
    report_filename = f"audit_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    report_path = os.path.join(report_dir, report_filename)
    
    # Define the headers for our CSV file
    headers = ['ID', 'Title', 'Result', 'Details']
    
    try:
        with open(report_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for task in tasks:
                # Case 1: Complex multi-step result
                if isinstance(task.actual_output, list):
                    overall_result = "PASS" if all("PASS" in step.get("result_text", "") for step in task.actual_output) else "FAIL"
                    # Write the main parent row
                    writer.writerow({
                        'ID': task.id,
                        'Title': task.title,
                        'Overall Result': task.final_result.splitlines()[0], # Just "Overall Result: FAIL"
                    })
                    # Write a child row for each sub-step
                    for step in task.actual_output:
                        writer.writerow({
                            'ID': '', # Keep ID blank for sub-steps
                            'Title': '',
                            'Overall Result': '',
                            'Sub-Check': step.get('name'),
                            'Sub-Check Result': "PASS" if "__EMPTY_OUTPUT__" in step.get('output') else "FAIL", # Simplified logic
                            'Details': step.get('output')
                        })
                
                # Case 2: Simple single-line result
                else:
                    writer.writerow({
                        'ID': task.id,
                        'Title': task.title,
                        'Overall Result': task.final_result,
                        'Details': task.actual_output
                    })
        print(f"Detailed CSV report saved to '{report_path}'")
    except Exception as e:
        print(f"ERROR: Could not write CSV report. Reason: {e}")