import time
import uuid

import requests
import streamlit as st
from snippets import jdumps

from agit.utils import getlog
from views import ENV, get_key
from views.common import load_chat_view

logger = getlog(env=ENV, name=__name__)


def refresh_session():
    session_id = uuid.uuid1().hex
    st.session_state["session_id"] = session_id
    st.info(f'new session created:{st.session_state["session_id"] }')
    return session_id


def get_session_id():
    if "session_id" not in st.session_state:
        return refresh_session()
    return st.session_state["session_id"]


def gen_with_job_id(job_id, url, detail=False):
    start = time.time()

    url = url+"/get_resp"
    req = dict(job_id=job_id)
    max_round = 100
    idx = 0
    first_token_cost = None
    total_words = 0

    while idx <= max_round:
        resp = requests.post(url=url, json=req)
        logger.info(f"resp of {job_id=} is {resp.json()}")
        resp = resp.json()["data"]
        intents = resp["intents"]
        content = resp["resp"]
        status = resp["status"]
        if status != "PENDING":
            if not first_token_cost and content.strip():
                first_token_cost = time.time() - start
            total_words += len(content)
            yield content
        if status in ("FINISHED", "FAILED"):
            break
        idx += 1
        # time.sleep(0.1)
    yield f"\n\n intents:{jdumps(intents)}"
    total_cost= time.time() - start
    if detail:
        st.info(f"{first_token_cost=:2.3f}s, {total_cost=:2.3f}s, {total_words=}")


def load_view():
    hosts = ["https://langchain.bigmodel.cn/im_chat/v2/chat",
             "http://127.0.0.1:5001/chat"]

    characters = ["车载助手", "女友", "孔子"]

    # st.title("ChatBot")

    url = st.sidebar.selectbox(label="服务地址", options=hosts, index=0)
    model = st.sidebar.selectbox(
        label="模型", options=get_key("models","chat_config"), index=0)

    temperature = st.sidebar.slider(
        label="温度", min_value=0.0, max_value=1.0, value=0.01, step=0.01)

    character = st.sidebar.selectbox(
        label="人设", options=characters, index=0)

    # 设置控制栏
    # 是否自定义模板
    test_mode = st.sidebar.checkbox(label="调试模式", value=False)
    if test_mode:
        prompt_template = st.sidebar.text_area(
            label="prompt模板", value=chatbot_config["prompt_template"], height=400)
        context = st.sidebar.text_area(
            label="context", value=chatbot_config["context"], height=150)
        for c in characters:
            chatbot_config["characters"][c] = st.sidebar.text_area(
                f"{c}的人设描述", chatbot_config["characters"][c], height=80)

    def build_user_config():
        if test_mode:
            return {
                "prompt_template": prompt_template,
                "characters": chatbot_config["characters"],
                "context": context
            }
        else:
            return {}

    def get_resp(prompt):
        session_id = get_session_id()
        data = {
            "prompt": prompt,
            "session_id": session_id,
            "model": model,
            "params": {
                "temperature": temperature,
            },
            "character": character,
            "user_config": build_user_config()
        }

        create_url = url+"/create"

        logger.info(f"request to {create_url=} with data:\n{jdumps(data)}")
        resp = requests.post(url=create_url, json=data)
        logger.info(f"response from {create_url=}:\n{jdumps(resp.json())}")
        job_id = resp.json()["data"]["job_id"]
        resp_gen = gen_with_job_id(job_id=job_id, url=url, detail=True)

        return resp_gen

        # resp = resp.json()["data"]
        # intents = resp["intents"]
        # st.info(intents)
        # content = (e for e in resp["resp"])
        # return content

    load_chat_view(get_resp_func=get_resp)
