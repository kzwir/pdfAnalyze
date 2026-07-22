# -*- coding: utf-8 -*-

import os
import logging

# Przykład użycia w glowny.py
# from logging_config import setup_logging

# logger = setup_logging(
#     log_dir="logs",
#     log_file="main.log",
#     log_level="INFO"
# )

# logger.info("Start programu")


def setup_logging(
    log_dir="logs",
    log_file="app.log",
    log_level="INFO"
):
    """
    Konfiguracja logowania.

    Parametry:
        log_dir  - katalog logów
        log_file - nazwa pliku logu
        log_level - DEBUG, INFO, WARNING, ERROR, CRITICAL

    Zwraca:
        logger
    """

    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, log_file)

    level = getattr(
        logging,
        str(log_level).upper(),
        logging.INFO
    )

    logger = logging.getLogger()

    # usuń poprzednie handlery
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)

    handler = logging.FileHandler(
        log_path,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def get_logger(name):
    return logging.getLogger(name)