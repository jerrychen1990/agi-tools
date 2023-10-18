import enum
import time
import uuid

import requests
import streamlit as st
from snippets import jdumps, jload, batchify

from agit import AGIT_ENV
from agit.utils import get_config, getlog
from views.common import load_chat_view, request_chatbot

logger = getlog(env=AGIT_ENV, name=__name__)


def refresh_session():
    session_id = uuid.uuid1().hex
    st.session_state["session_id"] = session_id
    st.info(f'new session created:{st.session_state["session_id"] }')
    return session_id


def get_session_id():
    if "session_id" not in st.session_state:
        return refresh_session()
    return st.session_state["session_id"]


def load_view():
    chatbot_config = get_config("chatbot_config.json")
    hosts = chatbot_config["hosts"]
    characters = list(chatbot_config["characters"].keys())
    # st.title("ChatBot")

    url = st.sidebar.selectbox(label="服务地址", options=hosts, index=0)
    # model = st.sidebar.selectbox(
    #     label="模型", options=chatbot_config["models"], index=0)
    temperature = st.sidebar.slider(
        label="温度", min_value=0.0, max_value=1.0, value=0.01, step=0.01)

    character = st.sidebar.selectbox(
        label="人设", options=characters, index=0)

    version = st.sidebar.selectbox("版本", ["v3", "v2", "v1"], index=0)
    clear = st.sidebar.button("清空历史")
    if clear:
        refresh_session()
        st.session_state.messages = []

    # 设置控制栏
    # 是否自定义模板
    test_mode = st.sidebar.checkbox(label="调试模式", value=False)
    if test_mode:
        prompt_template = st.sidebar.text_area(
            label="prompt模板", value=chatbot_config["prompt_template"], height=400)
        # context = st.sidebar.text_area(
        #     label="context", value=chatbot_config["context"], height=150)
        for c in characters:
            chatbot_config["characters"][c] = st.sidebar.text_area(
                f"{c}的人设描述", chatbot_config["characters"][c], height=80)

    def build_user_config():
        if test_mode:
            return {
                "prompt_template": prompt_template,
                "characters": chatbot_config["characters"],
            }
        else:
            return {}

    def get_resp(prompt):
        session_id = get_session_id()

        history = []
        for idx, (u, a) in enumerate(batchify(st.session_state.messages, batch_size=2)):
            item = dict(timestamp=idx, prompt=u["content"], response=a["content"], intents=[])
            history.append(item)
        # logger.info(f"{history=}")
        data = {
            "prompt": prompt,
            "session_id": session_id,
            # "model": model,
            "context": {
                "lon": 121.65187,
                "lat": 31.25092
            },
            "history": history[-10:],
            "params": {
                "temperature": temperature,
                # "model": model
            },
            "character": character,
            "user_config": build_user_config()
        }
        return request_chatbot(data=data, url=url, version=version, sync=False, return_gen=True)

    load_chat_view(get_resp_func=get_resp)
