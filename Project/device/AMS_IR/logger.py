import logging
import logging.handlers
import os

fileMaxByte = 1024 * 1024 * 10  # 10MB
consolLevel = logging.DEBUG
fileLevel = logging.DEBUG


def make_logger(name=None):
    # 1 logger instance를 만든다.
    logger = logging.getLogger(name)

    if name:
        filename = f'./log/{name}.log'
    else:
        filename = './log/test.log'

    # 2 logger의 level을 가장 낮은 수준인 DEBUG로 설정해둔다.
    logger.setLevel(logging.DEBUG)

    # 3 formatter 지정
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s|%(filename)s|%(funcName)s:%(threadName)s:%(lineno)s] > %(message)s")

    if not os.path.isdir('./log'):
        os.mkdir('log')
    # 4 handler instance 생성
    console = logging.StreamHandler()
    file_handler = logging.handlers.RotatingFileHandler(filename, maxBytes=fileMaxByte, backupCount=10)
    # file_handler = logging.FileHandler(filename="test.log")

    # 5 handler 별로 다른 level 설정
    console.setLevel(consolLevel)
    file_handler.setLevel(fileLevel)

    # 6 handler 출력 format 지정
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 7 logger에 handler 추가
    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger
