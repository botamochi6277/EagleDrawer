from logging import DEBUG, Formatter, Handler, Logger, LogRecord, StreamHandler, error, getLogger
# https://pod.hatenablog.com/entry/2020/03/01/221715
logger_mapping = {
    'DEBUG': '\x1b[0;36mDEBUG\x1b[0m',
    'INFO': '\x1b[0;32mINFO \x1b[0m',
    'WARN': '\x1b[0;33mWARN \x1b[0m',
    'WARNING': '\x1b[0;33mWARN \x1b[0m',
    'ERROR': '\x1b[0;31mERROR\x1b[0m',
    'CRITICAL': '\x1b[0;37;41mFATAL\x1b[0m'
}


class ColorfulHandler(StreamHandler):
    def emit(self, record: LogRecord) -> None:
        record.levelname = logger_mapping[record.levelname]
        super().emit(record)


def get_colorful_logger(name=__name__, level=DEBUG) -> Logger:
    logger = getLogger(name)
    handler = ColorfulHandler()

    formatter = Formatter(
        '%(levelname)s  %(asctime)s  %(message)s', '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    handler.setLevel(level)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


if __name__ == '__main__':
    logger = get_colorful_logger(__name__)

    logger.debug(f'debugging...')
    logger.info(f'information')
    logger.warning(f'watch out!')
    logger.error(f'i am missing a ball')
    logger.critical(f'this wound is deep')
