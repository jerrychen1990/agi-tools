#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/11/13 10:35:18
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

from unittest import TestCase

from agit.backend.zhipuai_bk import call_llm_api


# unitt test
class TestBackend(TestCase):
    def test_zhipu_backend(self):
        prompt = "你好"
        resp = call_llm_api(prompt=prompt, model="glm-3-turbo")
        print(resp)
