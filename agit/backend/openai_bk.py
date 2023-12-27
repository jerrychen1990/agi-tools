#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 10:55:05
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
import os
from typing import List

from agit import AGIT_ENV
from agit.utils import getlog
from openai import OpenAI


default_logger = getlog(AGIT_ENV, __file__)


def get_client(api_key, base_url, proxy):
    if api_key and base_url:
        return OpenAI(api_key=api_key, base_url=base_url)
    if proxy == "zhipu":
        default_logger.debug("use zhipu api_key")
        return OpenAI(api_key=os.environ.get("OPENAI_API_KEY_ZHIPU", None), base_url="https://one-api.glm.ai/v1")
    else:
        return OpenAI(api_key=os.environ.get("OPENAI_API_ZHIPU", None))


def get_gen(chunks):
    for chunk in chunks:
        choices = chunk.choices
        if not choices:
            continue
        content = choices[0].delta.content
        yield content or ""


def list_models(keyword=None, api_key=None, base_url=None, proxy=None) -> List[str]:
    client = get_client(api_key=api_key, base_url=base_url, proxy=proxy)
    models = client.models.list().data
    if keyword:
        models = [m for m in models if keyword in m.id]
    return models


def call_llm_api(prompt, model="gpt-3.5-turbo-1106",  history=[],
                 base_url=None, api_key=None, proxy=None, logger=None,
                 system: str = None, tools: List = None,
                 stream=True, **kwargs):

    def _build_messages(prompt, history, system, tools):
        messages = history + [dict(role="user", content=prompt)]
        if system:
            messages = [dict(role="system", content=system, tools=tools)] + messages
        return messages

    logger = logger or default_logger

    messages = _build_messages(prompt, history, system, tools)
    client = get_client(api_key=api_key, base_url=base_url, proxy=proxy)

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
        stream=stream,
    )
    gen = get_gen(chunks)
    if stream:
        return gen
    return "".join(gen)


if __name__ == "__main__":
    # text = "你好,你是谁？"
    # resp = call_llm_api(text, stream=True, model="gpt-3.5-turbo")
    # for item in resp:
    #     print(item, end="")

    # resp = call_llm_api(text, stream=True, model="gpt-4", proxy="zhipu")
    # for item in resp:
    #     print(item, end="")

    models = list_models(keyword="gpt-4", proxy="zhipu")
    # print(models)
    for model in models:
        print(model.id)
