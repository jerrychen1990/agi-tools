#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/08/15 11:11:03
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
import os

__version__ = "0.1.0"
AGIT_ENV = os.environ.get("AGIT_ENV", "local")
AGIT_PROJECT_HOME = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
AGIT_DATA_HOME = os.environ.get("AGIT_DATA_HOME", AGIT_PROJECT_HOME)


AGIT_TEMP_DIR = os.path.join(AGIT_DATA_HOME, "temp")
AGIT_KB_DIR = os.path.join(AGIT_DATA_HOME, "kb")
AGIT_CONFIG_DIR = os.path.join(AGIT_DATA_HOME, "config")


assistant_default_prompt_template = '''你是一个知识渊博、风趣幽默的人工智能小助手
你回答问题的时候可以参考reference标志的信息
reference
```
{{reference}}
```
问题:
{{message}}'''

LLM_MODELS = [
    "chatglm_lite",
    "chatglm_std",
    "chatglm_pro",
    "gpt-3.5-turbo-0301"
]
