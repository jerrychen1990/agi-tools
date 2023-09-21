
import requests
import streamlit as st

from agit.utils import getlog
from views import ENV, get_key
from views.common import load_batch_view

logger = getlog(ENV, __name__)


def list_kbs(host):
    url = f'{host}/list_knowledge_base'
    logger.info(f"{url=}")
    resp = requests.get(f'{host}/list_knowledge_base')
    return resp.json()["data"]


def load_view():
    hosts = get_key("kbqa_hosts", "kb_config.json")
    host = st.sidebar.selectbox("host", hosts, 0)
    kbs = list_kbs(host)
    knowledge_base_id = st.sidebar.selectbox(
        key=f"kbs", label="选择知识库", options=kbs)
    prompt_template = st.sidebar.text_area(
        lalbe="知识库模板", height=400, value=get_key("prompt_template", "kb_config.json"))

    def get_resp_func(prompt, history):

        json_data = {
            'knowledge_base_id': knowledge_base_id,
            'question': prompt,
            "prompt_template": prompt_template,
            'history': history,
        }
        resp = requests.post(f'{host}/local_doc_chat', json=json_data)
        rs_item = dict(prompt=prompt, response=resp,
                       settings=dict(host=host, knowledge_base_id=knowledge_base_id))
        return rs_item
    load_batch_view(get_resp_func=get_resp_func)
