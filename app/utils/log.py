import logging


class Log:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        datefmt="%H:%M:%S")

    @staticmethod
    def info(message: str):
        logging.info(f"\033[0;32m{message}\033[0m")

    @staticmethod
    def warning(message: str):
        logging.warning(f"\033[0;33m{message}\033[0m")

    @staticmethod
    def error(message: str):
        logging.error(f"\033[0;31m{message}\033[0m")