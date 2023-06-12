#!/usr/bin/env python3

import os
import sys
import logging
import socket
from pytz import timezone
from datetime import datetime

TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

LOGGER_MAP = {}

def numbers_to_string(numbers):
    return ",".join(str(n) for n in numbers)

def str2time(str, date_format=TIME_FORMAT):
    return datetime.strptime(str, date_format).astimezone(timezone('UTC'))

def get_host_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()

    return local_ip

def get_logger(filename):
    logger = LOGGER_MAP.get(filename)
    if logger:
        return logger
    else:
        logger = create_logger(filename)
        LOGGER_MAP[filename] = logger
        return logger

def create_logger(filename, log2console=False, logLevel=logging.INFO, logFolder= './logs'):
    logger = logging.getLogger(filename)
    logger.setLevel(logging.INFO)
    formatstr = '%(asctime)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s'
    formatter = logging.Formatter(formatstr)

    logfile = os.path.join(logFolder, filename)
    if not logfile.endswith(".log"):
        logfile += ".log"

    directory = os.path.dirname(logfile)
    if not os.path.exists(directory):
        os.makedirs(directory)

    handler = logging.FileHandler(logfile)
    handler.setLevel(logLevel)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if log2console:
        handler2 = logging.StreamHandler(sys.stdout)
        handler2.setFormatter(logging.Formatter(formatstr))
        handler2.setLevel(logLevel)
        logger.addHandler(handler2)
    return logger