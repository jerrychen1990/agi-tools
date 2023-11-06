#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 10:55:05
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
import os
from typing import List

import openai
import logging
from agit import AGIT_ENV
from agit.utils import getlog

logger = getlog(AGIT_ENV, __file__)


def check_api_key(api_key):
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY", None)
    if not api_key:
        raise ValueError("api_key is required")
    openai.api_key = api_key


def get_gen(chunks):
    for chunk in chunks:
        # logger.debug(chunk)

        if hasattr(chunk.choices[0].delta, "content"):
            content = chunk.choices[0].delta.content
            if content:
                yield chunk.choices[0].delta.content




def call_llm_api(prompt, model="gpt-3.5-turbo-16k-0613",  history=[],
                 system: str = None, tools: List = None, role="user",
                 stream=True, api_key=None, api_base=None,
                 verbose=logging.INFO, **kwargs):

    def _build_messages(prompt, history, system, tools):
        messages = history + [dict(role=role, content=prompt)]
        if system:
            messages = [dict(role="system", content=system, tools=tools)] + messages
        return messages
    check_api_key(api_key=api_key)
    if api_base:
        openai.api_base = api_base
    logger.setLevel(verbose)

    messages = _build_messages(prompt, history, system, tools)

    detail_msgs = []

    for idx, item in enumerate(messages):
        msg = f"[{idx+1}].{item['role']}:{item['content']}"
        if "tools" in item:
            msg += (f"\n[tools]:{tools}")

        detail_msgs.append(msg)
    logger.debug("\n"+"\n".join(detail_msgs))

    logger.info(f"request to openai with {model=}, {kwargs=}")

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
