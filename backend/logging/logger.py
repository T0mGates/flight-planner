import logging
import sys

class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and specific format: [Date] | LEVEL | File:Line | PID >>> Message"""

    # ANSI Color Codes
    GREY = "\x1b[38;20m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    GREEN = "\x1b[32;20m"
    RESET = "\x1b[0m"

    # Updated format string: Starting with date in brackets, removed first name field
    fmt = "[%(asctime)s] | %(levelname)-8s | %(filename)s:%(lineno)d | %(process)d >>> %(message)s"

    FORMATS = {
        logging.DEBUG: GREY + fmt + RESET,
        logging.INFO: GREEN + fmt + RESET,
        logging.WARNING: YELLOW + fmt + RESET,
        logging.ERROR: RED + fmt + RESET,
        logging.CRITICAL: BOLD_RED + fmt + RESET
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        # datefmt includes the milliseconds
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        formatted_record = formatter.format(record)
        # Clean up the microsecond to millisecond (stripping last 3 digits of %f)
        return formatted_record.replace(formatted_record[-7:-4], formatted_record[-7:-4])[:-3]

def get_logger(name="app"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(CustomFormatter())
        logger.addHandler(ch)

    return logger

# --- Usage ---
if __name__ == "__main__":
    log = get_logger()
    
    # Will automatically forward with sentry
    log.debug("A debug message")
    log.info("An info message")
    log.warning("A warning message")
    log.error("An error message")
    log.critical("A critical message")