# utils/logger.py
import logging
import sys

def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    创建通用 Logger，支持 INFO/DEBUG 输出到终端
    """
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

