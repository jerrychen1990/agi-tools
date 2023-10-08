#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@Time    :   2023/09/11 17:43:15
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
"""

import uuid

import streamlit as st

from agit.utils import get_config, getlog
from views import ENV
from views.common import load_batch_view, request_chatbot

logger = getlog(ENV, __name__)


def refresh_session(memory):
    session_id = uuid.uuid1().hex
    memory["session_id"] = session_id
    return session_id


def get_session_id(memory):
    if "session_id" not in memory:
        return refresh_session(memory)
    return memory["session_id"]


def load_view():
    chatbot_config = get_config("chatbot_config.json")
    hosts = chatbot_config["hosts"]
    url = hosts[0]

    default_prompt_template = chatbot_config["prompt_template"]

    default_characters = chatbot_config["characters"]
    characters = ["车载助手", "女友", "孔子"]

    # url = "https://langchain.bigmodel.cn/im_chat/chat"
    version = st.sidebar.selectbox("版本", ["v2", "v1"], index=0)
    temperature = st.sidebar.slider(
        key="temperature",
        label="temperature",
        min_value=0.01,
        max_value=1.0,
        value=0.01,
        step=0.01,
    )
    test_mode = st.sidebar.checkbox(label="调试模式", value=False)
    character = st.sidebar.selectbox(label="人设", options=characters, index=0)

    if test_mode:
        prompt_template = st.sidebar.text_area(
            label="prompt模板", value=default_prompt_template, height=400
        )
        # context = st.sidebar.text_area(label="环境", value = default_context, height=300)
        zhushou = st.sidebar.text_area(
            label="车载助手", value=default_characters["车载助手"], height=300
        )
        nvyou = st.sidebar.text_area(
            label="女友", value=default_characters["女友"], height=300
        )
        kongzi = st.sidebar.text_area(
            label="孔子", value=default_characters["孔子"], height=300
        )

    def build_user_config():
        if test_mode:
            return {
                "prompt_template": prompt_template,
                "characters": {"车载助手": zhushou, "女友": nvyou, "孔子": kongzi},
            }
        else:
            return {}

    def get_resp(item, memory):
        prompt = item["prompt"]
        content = ""
        intents = []
        try:
            if prompt == "<new session>":
                content = "更新session"
                refresh_session(memory)
                item.update(response=content, intents=intents)
            else:
                session_id = get_session_id(memory)
                data = {
                    "prompt": prompt,
                    "session_id": session_id,
                    "params": {
                        "temperature": temperature,
                    },
                    "context": {"lon": 121.65187, "lat": 31.25092},
                    "character": character,
                    "user_config": build_user_config(),
                }

                resp_item = request_chatbot(
                    data=data, url=url, version=version, sync=False, return_gen=False
                )
                content = resp_item["content"]
                intents = resp_item["intents"]

                item.update(response=content, intents=intents)

        except Exception as e:
            logger.exception(e)
            content = str(e)
        return {"question": prompt, "response": content, "intents": intents}

    load_batch_view(get_resp_func=get_resp, workers=1)
