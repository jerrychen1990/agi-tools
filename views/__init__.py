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
from views.common import load_chat_view

config_path = get_config_path("config.json")
config = jload(config_path)
config_path = get_config_path("chatbot_config.json")
chatbot_config = jload(config_path)

ENV = os.environ.get("AGIT_ENV", "local")

model_cands = config["models"]
