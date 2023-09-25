#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 17:43:15
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

from json import dumps
import requests
from scipy.fftpack import ss_diff
from snippets import jdumps, jload
import streamlit as st

from agit.backend.zhipuai_bk import call_llm_api
from agit.utils import getlog,get_config_path
from views import ENV, get_key
from views.common import load_batch_view
import uuid

logger = getlog(ENV, __name__)

chatbot_config = jload(get_config_path("chatbot_config.json"))


default_prompt_template = chatbot_config["prompt_template"]

default_characters =chatbot_config["characters"]


default_context=chatbot_config["context"]
characters = ["车载助手", "女友", "孔子"]


def refresh_session():
    session_id = uuid.uuid1().hex
    st.session_state["session_id"] = session_id
    st.info(f'new session created:{st.session_state["session_id"] }')
    return session_id

def get_session_id():
    if "session_id" not in st.session_state:
        session_id = uuid.uuid1().hex
        st.session_state["session_id"] = session_id
        return session_id
    return st.session_state["session_id"]


def load_view():
    
    url = "https://langchain.bigmodel.cn/im_chat/chat"
    version = st.sidebar.selectbox("版本", ["v1","v2"], index=0)
    temperature = st.sidebar.slider(key=f"temperature", label="temperature",
                                    min_value=0.01, max_value=1.0, value=0.01, step=0.01)
    test_mode = st.sidebar.checkbox(label="调试模式", value=False)
    character = st.sidebar.selectbox(label="人设", options=characters, index=0)

    if test_mode:
        prompt_template = st.sidebar.text_area(label="prompt模板", value = default_prompt_template, height=400)
        context = st.sidebar.text_area(label="环境", value = default_context, height=300)
        zhushou = st.sidebar.text_area(label="车载助手", value = default_characters["车载助手"], height=300)
        nvyou = st.sidebar.text_area(label="女友", value = default_characters["女友"], height=300)
        kongzi = st.sidebar.text_area(label="孔子", value = default_characters["孔子"], height=300)

    
    
    def build_user_config():
        if test_mode:
            return {
                "prompt_template": prompt_template,
                "context": context,
                "characters":{
                    "车载助手": zhushou,
                    "女友": nvyou,
                    "孔子": kongzi
                }
            }
        else:
            return {}    


    def get_resp(item,history):
        prompt = item["prompt"]
        content=""
        intents = []
        try:
            session_id = get_session_id()
            data = {
                "prompt": prompt,
                "session_id": session_id,
                "params": {
                    "temperature": temperature,
                },
                "character": character,
                "user_config": build_user_config()
            }
            base_url = url
            
            if version == "v2":
                base_url = base_url.replace("im_chat", "im_chat/v2")
                
            logger.info(f"request to {base_url=} with data:\n{jdumps(data)}")
            resp = requests.post(url=url, json=data)
            resp = resp.json()
            
            logger.info(f"response from {base_url=}:\n{jdumps(resp)}")
            content = resp["data"]["resp"]
            intents = resp["data"].get("intents", [])
            item.update(resp=content, intents=intents)
            
        except Exception as e:
            logger.exception(e)
        return {"question":prompt, "response":content, "intents":intents}

    load_batch_view(get_resp_func=get_resp, workers=1)
