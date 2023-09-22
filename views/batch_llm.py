#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 17:43:15
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import streamlit as st

from agit.backend.zhipuai_bk import call_llm_api
from agit.utils import getlog
from views import ENV, get_key
from views.common import load_batch_view

logger = getlog(ENV, __name__)


def load_view():
    prompt_template = st.sidebar.text_area(key=f"prompt_template", label="套在prompt上的模板,用{{content}}槽位表示",
                                           value="{{content}}")
    temperature = st.sidebar.slider(key=f"temperature", label="temperature",
                                    min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    top_p = st.sidebar.slider(key=f"top_p", label="top_p", min_value=0.1,
                              max_value=0.9, value=0.7, step=0.1)
    multi_turn = st.sidebar.checkbox(
        key=f"multi_turn", label="是否开启多轮对话", value=False)
    if multi_turn:
        history_len = st.sidebar.slider(key=f"history_len", label="历史长度（轮），一对问答为一轮",
                                        min_value=0, max_value=10, value=5, step=1)
    else:
        history_len = 0

    model = st.sidebar.selectbox(
        key=f"models", label="选择模型", options=get_key("models"))
    work_num = st.sidebar.number_input(
        key="work_num", label="并发数", min_value=1, max_value=10, value=1, step=1)

    def get_resp_func(item, history):
        prompt = item["prompt"]
        resp = ""
        try:
            prompt_with_template = prompt_template.replace(
                "{{content}}", prompt)
            history_start = max(0, len(history) - 2*history_len)
            resp = call_llm_api(
                prompt=prompt_with_template, history=history[history_start:], temperature=temperature, top_p=top_p, model=model, stream=False)
            item.update(prompt=prompt, prompt_with_template=prompt_with_template, response=resp,
                        settings=dict(temperature=temperature, top_p=top_p, model=model))
            history.extend([dict(role="user", content=prompt),
                            dict(role="assistant", content=resp)])
            # st.info(prompt)
            # st.info(resp)
        except Exception as e:
            logger.exception(e)
        return dict(prompt=prompt, response=resp)

    if work_num > 1 and history_len:
        st.warning("多轮对话时，并发数不能大于1")
    else:
        load_batch_view(get_resp_func=get_resp_func, workers=work_num)
