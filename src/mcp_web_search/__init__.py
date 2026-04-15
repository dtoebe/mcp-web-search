import logging

def init_logger(name: str, log_level: str, file_path: str) -> logging.Logger:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[
        logging.StreamHandler(),
        logging.FileHandler(file_path)
        ],
    )
    return logging.getLogger(name)