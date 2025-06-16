import logging
import datetime
import os

class ColorFormatter(logging.Formatter):

    GREY = "\x1b[38;20m"
    BLUE = "\x1b[34;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    GREEN = '\033[32m'

    ORANGE = "\x1b[33;20m"
    CYAN = "\x1b[36;20m"
    RESET = "\x1b[0m"
    BOLD_LBLUE = '\033[94m\033[1m'
    
    # The color codes now wrap ONLY the '%(levelname)s' part.
    # Assign a color to each log level
    FORMATS = {
        logging.DEBUG: f"{GREEN}%(asctime)s {BOLD_RED}|{RESET} {YELLOW}%(levelname)s{RESET} {BOLD_RED}|{RESET} %(message)s",
        logging.INFO: f"{GREEN}%(asctime)s {BOLD_RED}|{RESET} {BOLD_LBLUE}%(levelname)s{RESET} {BOLD_RED}|{RESET} %(message)s",
        logging.WARNING: f"{GREEN}%(asctime)s {BOLD_RED}|{RESET} {ORANGE}%(levelname)s{RESET} {BOLD_RED}|{RESET} %(message)s", # Orange is also good for warnings
        logging.ERROR: f"{GREEN}%(asctime)s {BOLD_RED}|{RESET} {RED}%(levelname)s{RESET} {BOLD_RED}|{RESET} %(message)s",
        logging.CRITICAL: f"{GREEN}%(asctime)s {BOLD_RED}|{RESET} {BOLD_RED}%(levelname)s{RESET} {BOLD_RED}|{RESET} %(message)s",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logger(log_level_str: str = 'INFO'):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = os.path.join(log_dir, f"audit_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # File handler (no color)
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    
    # Console handler (with color)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter())

    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger