#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/11 19:22:29
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import os
from typing import List
import streamlit as st
from agit import AGIT_CONFIG_DIR, AGIT_ENV, LLM_MODELS
from agit.utils import getlog
from agit.assistant import Assistant
from agit.kb import Chunk


logger = getlog(AGIT_ENV, __file__)
config_path = os.path.join(AGIT_CONFIG_DIR, "taco_ai.json")


def build_detail_message(content, references: List[Chunk]):
    rs = content
    if references:
        # rs += "\n------------\n"
        rs += "References\n\n"
        for idx, ref in enumerate(references):
            rs += f"{idx+1}.{ref.to_str()}\n\n"
    return rs


def get_assistante() -> Assistant:
    if "assistant" not in st.session_state:
        logger.info("new assistant")
        assistant = Assistant.from_config(config=config_path)
        st.session_state["assistant"] = assistant
    return st.session_state.assistant


if "messages" not in st.session_state:
    st.session_state.messages = []

use_kb = st.sidebar.checkbox(label="使用知识库", value=True)
use_history = st.sidebar.checkbox(label="多轮聊天", value=True)
threshold = st.sidebar.slider(label="知识阈值", min_value=0.0, max_value=1.0, value=0.6)
new_session = st.sidebar.button(label="新会话")
show_ref = st.sidebar.checkbox(label="展示reference", value=True)
llm_model = st.sidebar.selectbox(label="选择模型", options=LLM_MODELS, index=LLM_MODELS.index("gpt-3.5-turbo-0301"))

if new_session:
    assistant = get_assistante()
    assistant.clear_history()
    st.session_state.messages = []


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        to_show = message["content"]
        if show_ref and "reference" in message:
            to_show = build_detail_message(message["content"], message["references"])

        st.markdown(to_show)


if prompt := st.chat_input("你好，你是谁？"):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        content = ""

    assistant: Assistant = get_assistante()
    resp = assistant.chat(message=prompt, stream=True, llm_model=llm_model,
                          use_kb=use_kb, use_history=use_history, threshold=threshold)
    # resp_gen = resp.to_gen()

    for token in resp.content:
        content += token
        message_placeholder.markdown(content + "▌")

    to_show = content
    if show_ref:
        to_show = build_detail_message(content, resp.references)

    logger.info(f"{to_show=}")
    message_placeholder.markdown(to_show)

    st.session_state.messages.append(
        {"role": "user", "content": prompt})
    st.session_state.messages.append(
        {"role": "assistant", "content": content, "references": resp.references})

    assistant.add_resp(content)
