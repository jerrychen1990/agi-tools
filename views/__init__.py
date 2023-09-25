#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/19 18:41:44
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import os

from snippets import jload

from agit.utils import get_config_path

# config_path = get_config_path("config.json")
# config_path = get_config_path("chatbot_config.json")
# chatbot_config = jload(config_path)

ENV = os.environ.get("AGIT_ENV", "local")

TMP_DIR = "/tmp/streamlit"
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)
    


def get_key(key, config_name="config.json"):
    config_path = get_config_path(config_name)
    config = jload(config_path)
    return config[key]
