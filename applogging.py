import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
import shutil
import os
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_logging(app):
    # Set up file logging (with rotation)
    file_handler = RotatingFileHandler(f"{app.config['path_of_interfaceOnly_javap']}/app.log", maxBytes=2000, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Set up console logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
def log_action(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"{func.__name__} returned {result}")
        return result
    return wrapper

# Wrap shutil functions with the logging decorator
shutil.copy = log_action(shutil.copy)
shutil.copy2 = log_action(shutil.copy2)
shutil.copyfile = log_action(shutil.copyfile)
shutil.move = log_action(shutil.move)
shutil.rmtree = log_action(shutil.rmtree)
shutil.make_archive = log_action(shutil.make_archive)
shutil.unpack_archive = log_action(shutil.unpack_archive)
shutil.disk_usage = log_action(shutil.disk_usage)
shutil.chown = log_action(shutil.chown)

def log_subprocess_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"{func.__name__} returned {result}")
        return result
    return wrapper

# Wrap subprocess functions with the logging decorator
subprocess.run = log_subprocess_call(subprocess.run)
subprocess.call = log_subprocess_call(subprocess.call)
subprocess.check_call = log_subprocess_call(subprocess.check_call)
subprocess.check_output = log_subprocess_call(subprocess.check_output)