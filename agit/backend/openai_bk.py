#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 10:55:05
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
import os

import openai

from agit import AGIT_ENV
from agit.utils import getlog

logger = getlog(AGIT_ENV, __name__)


def check_api_key(api_key):
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY", None)
    if not api_key:
        raise ValueError("api_key is required")
    openai.api_key = api_key


def get_gen(chunks):
    for chunk in chunks:
        if hasattr(chunk.choices[0].delta, "content"):
            yield chunk.choices[0].delta.content


def call_llm_api(prompt, model="gpt-3.5-turbo-16k-0613",  history=[], stream=True, **kwargs):
    def _build_messages(prompt, history):
        messages = history + [dict(role="user", content=prompt)]
        return messages

    messages = _build_messages(prompt, history)
    logger.info(f"request to openai with {model=}")

    chunks = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        stream=True
    )
    gen = get_gen(chunks)
    if stream:
        return gen
    return "".join(gen)


if __name__ == "__main__":
    text = "你好"
    resp = call_llm_api(text, stream=False)
    print(resp)
