import logging


def initialize_logger(logger_name=None, log_file_name=None, log_level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    if logger_name:
        # Define stream handler
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file_name:
        # Define a log file
        fh = logging.FileHandler(log_file_name)
        fh.setLevel(log_level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
