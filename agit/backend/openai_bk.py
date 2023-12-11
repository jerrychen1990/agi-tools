#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 10:55:05
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
import os
from typing import List

import logging
from agit import AGIT_ENV
from agit.utils import getlog
from openai import OpenAI


logger = getlog(AGIT_ENV, __file__)


def get_client(api_key, base_url):
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY", None)
    if not api_key:
        raise ValueError("api_key is required")
    return OpenAI(api_key=api_key, base_url=base_url)


def get_gen(chunks):
    for chunk in chunks:
        # logger.debug(chunk)
        content = chunk.choices[0].delta.content
        yield content or ""


def call_llm_api(prompt, model="gpt-3.5-turbo-1106",  history=[],
                 base_url=None,
                 system: str = None, tools: List = None, role="user",
                 stream=True, api_key=None, api_base=None,
                 verbose=logging.INFO, **kwargs):

    def _build_messages(prompt, history, system, tools):
        messages = history + [dict(role=role, content=prompt)]
        if system:
            messages = [dict(role="system", content=system, tools=tools)] + messages
        return messages
    

    messages = _build_messages(prompt, history, system, tools)
    logger.setLevel(verbose)

    client = get_client(api_key=api_key, base_url=base_url)

    detail_msgs = []
    for idx, item in enumerate(messages):
        msg = f"[{idx+1}].{item['role']}:{item['content']}"
        if "tools" in item:
            msg += (f"\n[tools]:{tools}")

        detail_msgs.append(msg)
    logger.debug("\n"+"\n".join(detail_msgs))

    logger.info(f"request to openai with {model=}, {kwargs=}")

    chunks = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    gen = get_gen(chunks)
    if stream:
        return gen
    return "".join(gen)


if __name__ == "__main__":
    text = "你好"
    # resp = call_llm_api(text, stream=False, verbose=logging.DEBUG)
    resp = call_llm_api(text, stream=False, verbose=logging.DEBUG, model="gpt-3.5-turbo",
                        api_key="sk-fZXC1WleN8HZtHlTDf721406A6Ce4bBc9340C23eEc5cCfEf",
                        base_url="https://one-api.glm.ai/v1")

    # resp = call_llm_api(text, stream=False, verbose=logging.DEBUG)

    print(resp)
