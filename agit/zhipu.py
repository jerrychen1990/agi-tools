#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/08/14 16:06:30
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


import os
from typing import Any, List

import zhipuai
from snippets import get_batched_data

from agit.utils import getlog

env = os.environ.get("IM_ENV", "dev")
logger = getlog(env, __name__)

_HISTORY_PLACEHOLDER = '$HISTORY'


def resp_generator(events, max_len=None):
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
            yield event.data


def build_history_str(history: List[str], history_tmplate) -> str:
    assert len(history) % 2 == 0
    rs = []
    for idx, (q, a) in enumerate(get_batched_data(history, 2)):
        q, a = q["content"], a["content"]
        rs.append(history_tmplate.format(q=q, a=a, idx=idx+1))
    rs = "\n".join(rs)
    return rs


class ZhipuAgent:
    def __init__(self, api_key=None) -> None:
        if api_key:
            zhipuai.api_key = api_key
        else:
            zhipuai.api_key = os.environ["ZHIPU_API_KEY"]

    def __call__(self, prompt: str, history=[], model: str = "chatglm_lite", stream=True,
                 max_len=None, max_history_len=None, max_single_history_len=None,
                 history_template=None, **kwargs) -> Any:
        if max_history_len:
            logger.debug(
                f"history length:{len(history)}, cut to {max_history_len}")
            history = history[-max_history_len:]
        if max_single_history_len:
            logger.debug(
                f"cut each history's length to {max_single_history_len}")
            history = [dict(role=e['role'], content=e['content']
                            [:max_single_history_len]) for e in history]

        if history_template:
            logger.debug(
                f"build history with history template:{history_template}")
            assert _HISTORY_PLACEHOLDER in prompt
            history_str = build_history_str(history, history_template)
            prompt = prompt.replace(_HISTORY_PLACEHOLDER, history_str)
            zhipu_prompt = [dict(role="user", content=prompt)]
        else:
            zhipu_prompt = history + [dict(role="user", content=prompt)]

        total_words = sum([len(e['content']) for e in zhipu_prompt])
        logger.info(f"zhipu prompt:")
        detail_msgs = []

        for idx, item in enumerate(zhipu_prompt):
            detail_msgs.append(f"[{idx+1}].{item['role']}:{item['content']}")
        logger.info("\n"+"\n".join(detail_msgs))
        logger.info(
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
