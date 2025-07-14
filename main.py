import argparse
import logging
from handlers.log_handler import setup_logger
from utils.csv_parser import CISBenchmarkParser
from handlers.audit_handler import AuditHandler
from utils.report_generator import generate_summary_report, generate_csv_report
from typing import List
from audit_task import AuditTask

def main():
    parser = argparse.ArgumentParser(description="Run a CIS security audit from a CSV benchmark file.")
    parser.add_argument('benchmark_file', help="The path to the CIS benchmark CSV file.")

    parser.add_argument('--profile', help="Run only checks for a specific profile.")
    parser.add_argument('--level', help="Run only checks for a specific level.")
    parser.add_argument('--domain', help="Run only checks for a specific domain.")
    parser.add_argument('--id', help="Run only a single check by its ID.")

    parser.add_argument(
        '--format',
        choices=['txt', 'csv'],
        default='txt',
        help="The output format for the report (default: txt)."
    )
    
    # This defines the --loglevel argument that the user can provide.
    parser.add_argument(
        '--loglevel',
        choices=['DEBUG', 'INFO'],
        default='INFO',
        help="Set the logging verbosity (default: INFO)."
    )
    args = parser.parse_args()
    
    # Setup the logger with the level provided from the command line
    logger = setup_logger(args.loglevel)
    
    logger.info(f"Starting CIS Auditor with file: '{args.benchmark_file}'")
    try:
        csv_parser = CISBenchmarkParser(args.benchmark_file)
        all_tasks = csv_parser.parse_csv()
        
        # Filtering logic based on args...
        tasks_to_run = all_tasks
        if args.level:
            tasks_to_run = [t for t in tasks_to_run if t.level == args.level]
        if args.profile:
            tasks_to_run = [t for t in tasks_to_run if args.profile in t.profile]
        if args.domain:
            tasks_to_run = [t for t in tasks_to_run if t.domain == args.domain]
        if args.id:
            tasks_to_run = [t for t in tasks_to_run if t.id == args.id]

    except Exception as e:
        logger.critical(f"Failed to parse benchmark file. Error: {e}")
        return

    audit_handler = AuditHandler()
    # The audit handler is also passed the log level for its own internal logic.
    completed_tasks = audit_handler.run_audit(tasks_to_run, log_level=args.loglevel)
    
    # We must pass the `log_level` from the args directly to the report generator.
    generate_summary_report(completed_tasks, log_level=args.loglevel)
    
    if args.format == 'csv':
        generate_csv_report(completed_tasks)
    
    logger.info("Application finished.")


if __name__ == "__main__":
    main()