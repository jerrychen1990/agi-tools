#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 10:19:27
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


import logging
import os
import sys
from typing import Any, List

import zhipuai
from snippets import get_batched_data

from agit.utils import getlog

logger = getlog("prod", __name__)


def check_api_key(api_key):
    if api_key is None:
        api_key = os.environ.get("ZHIPUAI_API_KEY", None)
    if not api_key:
        raise ValueError("api_key is required")
    zhipuai.api_key = api_key


def resp_generator(events, max_len=None, err_resp=None):
    token_left = max_len if max_len else None
    for event in events:
        if event.event == "add":
            if token_left:
                if len(event.data) > token_left:
                    data = event.data[:token_left]
                else:
                    data = event.data
                token_left -= len(data)
                yield data
                if token_left == 0:
                    break
            else:
                yield event.data
        elif event.event == "finish":
            pass
        else:
            logger.error(
                f"zhipu api resp failed with event:{event.event}, data:{event.data}")
            yield err_resp if err_resp else event.data


def call_llm_api(prompt: str, history=[], model: str = "chatglm_lite",
                 api_key=None, stream=True, max_len=None, max_history_len=None,
                 verbose=logging.INFO,
                 max_single_history_len=None, **kwargs) -> Any:
    check_api_key(api_key)
    logger.setLevel(verbose)

    if max_history_len:
        logger.debug(
            f"history length:{len(history)}, cut to {max_history_len}")
        history = history[-max_history_len:]
    if max_single_history_len:
        logger.debug(
            f"cut each history's length to {max_single_history_len}")
        history = [dict(role=e['role'], content=e['content']
                        [:max_single_history_len]) for e in history]
    zhipu_prompt = history + [dict(role="user", content=prompt)]
    total_words = sum([len(e['content']) for e in zhipu_prompt])
    logger.debug(f"zhipu prompt:")
    detail_msgs = []

    for idx, item in enumerate(zhipu_prompt):
        detail_msgs.append(f"[{idx+1}].{item['role']}:{item['content']}")
    logger.debug("\n"+"\n".join(detail_msgs))
    logger.debug(
        f"{model=}, {stream=}, {kwargs=}, history_len={len(history)}, words_num={total_words}")
    response = zhipuai.model_api.sse_invoke(
        model=model,
        prompt=zhipu_prompt,
        **kwargs
    )
    generator = resp_generator(response.events(), max_len=max_len)
    if stream:
        return generator
    else:
        resp = "".join(list(generator)).strip()
        if max_len:
            resp = resp[:max_len]
        return resp


def call_embedding_api(text: str, api_key=None):
    check_api_key(api_key)
    resp = zhipuai.model_api.invoke(
        model="text_embedding",
        prompt=text
    )
    if resp["code"] != 200:
        raise Exception(resp["msg"])
    embedding = resp["data"]["embedding"]
    return embedding


if __name__ == "__main__":
    text = "你好"
    resp = "".join(call_llm_api(text))
    print(resp)
    emb = call_embedding_api(text)
    print(len(emb))
    print(emb[:4])
