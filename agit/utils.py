#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/08/14 16:07:24
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import logging


def getlog(env, name):
    # print(f"create logger with {env=}, {name=}")
    if env == "dev":
        logger = logging.getLogger(name)
        if name in logging.Logger.manager.loggerDict:
            return logger
        logger.propagate = False
        logger.setLevel(logging.DEBUG)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(fmt=logging.Formatter(
            "%(asctime)s [%(levelname)s][%(filename)s:%(lineno)d]:%(message)s", datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(streamHandler)
        return logger
    else:
        logger = logging.getLogger(name)
        if name in logging.Logger.manager.loggerDict:
            return logger
        logger.propagate = False
        logger.setLevel(logging.INFO)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(fmt=logging.Formatter(
            "%(asctime)s [%(levelname)s]%(message)s", datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(streamHandler)
        return logger


def save_csv_xls(df, path):
    if path.endswith(".csv"):
        df.to_csv(path, index=False)
    elif path.endswith(".xlsx"):
        df.to_excel(path, index=False)
    else:
        raise Exception(f"Unknown file format: {path}")
