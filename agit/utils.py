#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/08/14 16:07:24
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

from ctypes import Union
import logging
import os
from typing import List
from snippets import jload

import numpy as np
import pandas as pd


def getlog(env, name):
    # print(f"create logger with {env=}, {name=}")
    if env == "dev" or env == "local":
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


def read_csv_xls(path):
    if path.endswith(".csv"):
        return pd.read_csv(path)
    elif path.endswith(".xlsx"):
        return pd.read_excel(path)
    else:
        raise Exception(f"Unknown file format: {path}")


def cal_vec_similarity(vec1: List[float], vec2: List[float], normalize=True, metric="cosine"):
    """
    计算两个向量之间的相似度
    :param vec1: 向量1
    :param vec2: 向量2
    :return: 相似度/距离
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    if normalize:
        vec1 = vec1 / np.linalg.norm(vec1, ord=2)
        vec2 = vec2 / np.linalg.norm(vec2, ord=2)
    if metric == "cosine":
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1, 2) * np.linalg.norm(vec2, 2))
    if metric == "l2_distance":
        return np.linalg.norm((vec1-vec2), 2)
    else:
        raise Exception(f"Unknown metric: {metric}")


def get_config_path(config_name):
    config_home = os.environ["AGIT_CONFIG_HOME"]
    env = os.environ["AGIT_ENV"]
    config_path = os.path.join(config_home, env, config_name)
    return config_path


def get_config(config_name):
    return jload(get_config_path(config_name))



class ConfigMixin:
    @classmethod
    def from_config(cls, config:Union[dict, str])
        if isinstance(config, str):
                if config.endswith(".json"):
                    config = jload(config)
                else:
                    raise ValueError(f"{config} is not a valid config file")
        instance = cls(**config)
        return instance
        
    