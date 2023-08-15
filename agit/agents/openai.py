#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/08/15 15:27:36
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import os
from typing import Any

import openai

from agit.utils import getlog

logger = getlog("dev", __name__)


def get_gen(chunks):
    for chunk in chunks:
        if hasattr(chunk.choices[0].delta, "content"):
            yield chunk.choices[0].delta.content


class OpenAIAgent:
    def __init__(self, api_base, api_key=None) -> None:
        openai.api_base = api_base
        if api_key:
            openai.api_key = api_key
        elif "OPENAI_API_KEY" in os.environ:
            openai.api_key = os.environ["OPENAI_API_KEY"]
            
    def _build_messages(self, prompt, history):
        messages = history + [dict(role="user", content=prompt)]
        return messages

    def __call__(self, prompt, model,  history=[], stream=True) -> Any:
        messages = self._build_messages(prompt, history)
        chunks = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            stream=True
        )
        gen = get_gen(chunks)
        if stream:
            return gen
        return "".join(gen)
