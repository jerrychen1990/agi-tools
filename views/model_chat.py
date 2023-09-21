#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 17:43:15
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


import streamlit as st
from snippets.utils import jload

from agit.backend import call_llm_api
from agit.utils import get_config_path
from views import get_key
from views.common import load_chat_view


def load_view():
    model_cands = get_key("models")
    default_model = get_key("default_chat_model")
    default_model_idx = model_cands.index(default_model)

    prompt_template = st.sidebar.text_area(key=f"prompt_template", label="套在prompt上的模板,用{{content}}槽位表示",
                                           value="{{content}}")
    temperature = st.sidebar.slider(key=f"temperature", label="temperature",
                                    min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    top_p = st.sidebar.slider(key=f"top_p", label="top_p", min_value=0.1,
                              max_value=0.9, value=0.7, step=0.1)

    history_len = st.sidebar.slider(key=f"history_len", label="历史长度（轮），一对问答为一轮",
                                    min_value=0, max_value=10, value=5, step=1)

    model = st.sidebar.selectbox(
        key=f"models", label="选择模型", options=model_cands, index=default_model_idx)

    clear = st.sidebar.button(key=f"clear", label="清空历史")
    if clear:
        st.info("历史已清空")
        st.session_state.messages = []

    def get_resp(prompt):
        history = st.session_state.messages
        history_start = max(0, len(history) - 2*history_len)

        history = history[history_start:]
        prompt_with_template = prompt_template.replace("{{content}}", prompt)
        resp = call_llm_api(prompt_with_template, model=model, history=history,
                            temperature=temperature, top_p=top_p, stream=True)
        return resp

    load_chat_view(get_resp_func=get_resp)
