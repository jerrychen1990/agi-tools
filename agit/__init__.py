#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/08/15 11:11:03
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
import os
from loguru import logger
from snippets.logs import LoguruFormat
from snippets import print_info

AGIT_ENV = os.environ.get("AGIT_ENV", "dev")
HOME = os.environ["HOME"]
AGIT_HOME = os.environ.get("AGIT_HOME", os.path.join(HOME, ".agit"))

AGIT_LOG_HOME = os.path.join(AGIT_HOME, "logs")
os.makedirs(AGIT_LOG_HOME, exist_ok=True)

def init_log():
    logger.remove()
    level = "DEBUG" if AGIT_ENV == "dev" else "INFO"
    fmt = LoguruFormat.DETAIL if AGIT_ENV == "dev" else LoguruFormat.SIMPLE
    
    # logger.add(sys.stdout, colorize=True, format=fmt, level=level)
    # detail_log_path = os.path.join(LOG_DIR, "detail.log")
    # logger.add(detail_log_path, rotation="00:00", retention="7 days", enqueue=True, backtrace=True, level="DEBUG")
    # output_log_path = os.path.join(LOG_DIR, "output.log")
    # logger.add(output_log_path, rotation="00:00", retention="30 days", enqueue=True, backtrace=True, level="INFO")

    # logger.add(os.path.join(AGIT_LOG_HOME,"zhipuai_bk.log"), retention="365 days", rotation=" 1day", level="INFO", filter=__name__, format=LoguruFormat.SIMPLE) 



def show_env():
    print_info("current AGIT env", logger)
    logger.info(f"{AGIT_ENV=}")
    logger.info(f"{AGIT_HOME=}")
    logger.info(f"{AGIT_LOG_HOME=}")
    print_info("", logger)
show_env()