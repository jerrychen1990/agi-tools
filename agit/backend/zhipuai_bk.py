#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 10:19:27
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


import logging
import os
from typing import Any

import numpy as np
import zhipuai
from cachetools import LRUCache, cached
from snippets import retry
from agit import AGIT_ENV


from agit.utils import getlog

logger = getlog(AGIT_ENV, __file__)


def check_api_key(api_key):
    if api_key is None:
        api_key = os.environ.get("ZHIPUAI_API_KEY", None)
    if not api_key:
        raise ValueError("未设置api_key且未设置ZHIPUAI_API_KEY环境变量")
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


# sdk请求模型
def call_llm_api(prompt: str, model: str, history=[],
                 api_key=None, stream=True, max_len=None, max_history_len=None,
                 verbose=logging.INFO, max_single_history_len=None,
                 do_search=True, search_query=None,
                 **kwargs) -> Any:
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

    if "ref" not in kwargs:
        ref = dict(enable=do_search, query=search_query if search_query else prompt)
        kwargs.update(ref=ref)
    if "request_id" not in kwargs:
        request_id = gen_req_id(prompt=prompt, model=model)
        kwargs.update(request_id=request_id)
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


def call_character_api(prompt: str, user_name, user_info, bot_name, bot_info,
                       history=[], model="characterglm", api_key=None, stream=True, max_len=None, **kwargs):
    check_api_key(api_key)
    zhipu_prompt = history + [dict(role="user", content=prompt)]
    total_words = sum([len(e['content']) for e in zhipu_prompt])
    logger.debug(f"zhipu prompt:")
    detail_msgs = []

    for idx, item in enumerate(zhipu_prompt):
        detail_msgs.append(f"[{idx+1}].{item['role']}:{item['content']}")
    logger.debug("\n"+"\n".join(detail_msgs))
    logger.debug(
        f"{model=},{kwargs=}, history_len={len(history)}, words_num={total_words}")
    meta = {
        "user_info": user_info,
        "bot_info": bot_info,
        "bot_name": bot_name,
        "user_name": user_name
    }
    response = zhipuai.model_api.sse_invoke(
        model=model,
        meta=meta,
        prompt=zhipu_prompt,
        incremental=True,
        ** kwargs
    )
    generator = resp_generator(response.events(), max_len=None)
    if stream:
        return generator
    else:
        resp = "".join(list(generator)).strip()
        if max_len:
            resp = resp[:max_len]
        return resp


@cached(LRUCache(maxsize=1000))
def call_embedding_api(text: str, api_key=None, norm=None, retry_num=2, wait_time=1):
    check_api_key(api_key)

    def attempt():
        resp = zhipuai.model_api.invoke(
            model="text_embedding",
            prompt=text
        )
        if resp["code"] != 200:
            raise Exception(resp["msg"])
        embedding = resp["data"]["embedding"]
        if norm is not None:
            embedding = embedding / np.linalg.norm(embedding, norm)
        return embedding

    if retry_num:
        attempt = retry(retry_num=retry_num, wait_time=wait_time)(attempt)
    return attempt()


if __name__ == "__main__":
    text = "你好"
    resp = "".join(call_llm_api(text))
    print(resp)
    emb = call_embedding_api(text)
    print(len(emb))
    print(emb[:4])
