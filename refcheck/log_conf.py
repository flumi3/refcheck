import logging


def setup_logging(verbose=False):
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Clear any existing handlers
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # Create a console handler
    console_handler = logging.StreamHandler()

    if verbose:
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s]  %(message)s")
    else:
        console_handler.setLevel(logging.CRITICAL)
        console_formatter = logging.Formatter("%(asctime)s - %(message)s")

    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
