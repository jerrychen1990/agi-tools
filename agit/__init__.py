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
AGIT_TEMP_DIR = os.environ.get("AGIT_TEMP_DIR", "/tmp")
