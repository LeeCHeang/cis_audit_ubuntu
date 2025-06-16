import argparse
from handlers.log_handler import setup_logger
from utils.csv_parser import CISBenchmarkParser
from handlers.audit_handler import AuditHandler
from utils.report_generator import generate_summary_report, generate_csv_report

def main():
    parser = argparse.ArgumentParser(description="Run a CIS security audit from a CSV benchmark file.")
    parser.add_argument('benchmark_file', help="The path to the CIS benchmark CSV file.")

    parser.add_argument('--profile', help="Run only checks for a specific profile (e.g., Server, Workstation).")
    parser.add_argument('--level', help="Run only checks for a specific level (e.g., L1, L2).")
    parser.add_argument('--domain', help="Run only checks for a specific domain (e.g., 'Logging and Auditing').")
    parser.add_argument('--id', help="Run only a single check by its ID.")  

    parser.add_argument(
        '--format',
        choices=['txt', 'csv'],
        default='txt',
        help="The output format for the report (default: txt)."
    )
    # This adds the --loglevel flag to your command line.
    parser.add_argument(
        '--loglevel',
        choices=['DEBUG', 'INFO'],
        default='INFO',
        help="Set the logging verbosity (default: INFO)."
    )
    args = parser.parse_args()
    
    # Setup logger with the level from the command line
    logger = setup_logger(args.loglevel)
    
    logger.info(f"Starting CIS Auditor with file: '{args.benchmark_file}'")
    try:
        csv_parser = CISBenchmarkParser(args.benchmark_file)
        all_tasks = csv_parser.parse_csv()
        tasks_to_run = all_tasks
        if args.level:
            tasks_to_run = [t for t in tasks_to_run if t.level == args.level]
            logger.info(f"Filtering for Level: {args.level}")
        
        if args.profile:
            # This logic now checks if the requested profile is IN the task's list of profiles,
            # or if the task's profile list contains 'All'.
            tasks_to_run = [t for t in tasks_to_run if args.profile in t.profile or 'All' in t.profile]
            logger.info(f"Filtering for Profile: {args.profile}")
        if args.domain:
            tasks_to_run = [t for t in tasks_to_run if t.domain == args.domain]
            logger.info(f"Filtering for Domain: {args.domain}")
            
        if args.id:
            tasks_to_run = [t for t in tasks_to_run if t.id == args.id]
            logger.info(f"Filtering for single Check ID: {args.id}")
    except Exception as e:
        logger.critical(f"Failed to parse benchmark file. Error: {e}")
        return

    audit_handler = AuditHandler()
    
    # This tells the audit handler whether it should run in normal or debug mode.
    completed_tasks = audit_handler.run_audit(tasks_to_run, log_level=args.loglevel)
    
    generate_summary_report(completed_tasks)
    
    if args.format == 'csv':
        generate_csv_report(completed_tasks)
    
    logger.info("Application finished.")


if __name__ == "__main__":
    main()