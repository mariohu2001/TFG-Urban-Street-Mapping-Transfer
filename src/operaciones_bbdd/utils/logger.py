import logging as lg
import os


LOG_FOLDER: str = os.path.join(os.path.dirname(__file__), '..', 'logs')


def create_logger(logger_name: str, log_file: str, log_level=lg.INFO):

    logger: lg.Logger = lg.getLogger(logger_name)
    logger.setLevel(log_level)

    format: lg.Formatter = lg.Formatter(
        "%(levelname)s >>> [%(asctime)s]: %(message)s")
    file_handler: lg.FileHandler = lg.FileHandler(
        filename=f"{LOG_FOLDER}\\{log_file}.log", mode="w", encoding="UTF-8")
    file_handler.setFormatter(format)
    logger.addHandler(file_handler)

    return logger
