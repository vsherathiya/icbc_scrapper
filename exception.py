import sys,logging
import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def error_message_detail(error, error_detail: sys):
    """
    It returns the error message with the file name, try block line number, exception block line number
    and the error message

    :param error: The error message that was raised
    :param error_detail: sys
    :type error_detail: sys
    :return: The error message
    """
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    try_block_line_no = exc_tb.tb_lineno
    Exception_block_line_no = exc_tb.tb_frame.f_lineno
    error_message = f"""Python Script :
    [{file_name}] 
    at try block line number : [{try_block_line_no}] and exception block line no : [{Exception_block_line_no}] 
    error message : 
    [{str(error)}]
    """
    return error_message


class CustomException(Exception):
    def __init__(self, error_message, error_detail: sys):
        """
        A constructor function that initializes the class.

        :param error_message: The error message that will be displayed to the user
        :param error_detail: This is the error message that you want to display
        :type error_detail: sys
        """
        super().__init__(error_message)
        self.error_message = error_message_detail(
            error_message, error_detail=error_detail)

    def __str__(self):
        return self.error_message

    def __repr__(self) -> str:
        return CustomException.__name__.str()  
    
    
def setup_logger(name, file_prefix, level=logging.INFO, stream=False):
    # Ensure the logs directory exists
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    # Get the current hour
    logger = logging.getLogger(name)
    current_time = datetime.now()
    hour_folder = current_time.strftime("%Y-%m-%d_%H")
    log_dir = os.path.join(log_dir, 'logs_'+hour_folder)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    formatter = logging.Formatter(
        "[%(asctime)s] || %(filename)s || %(lineno)d || %(name)s || %(funcName)s() || %(levelname)s -->> %(message)s")
    # Create a logger
    logger.setLevel(level)
    # Create a timed rotating file handler
    log_file = os.path.join(log_dir, f"{file_prefix}.log")
    file_handler = TimedRotatingFileHandler(log_file, when="H", interval=1, backupCount=50)  # Rotate every hour, keep 24 backups
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # Optionally add a console handler
    if stream:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger