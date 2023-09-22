
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
        label="知识库模板", height=400, value=get_key("prompt_template", "kb_config.json"))
    work_num = st.sidebar.number_input(
        key="work_num", label="并发数", min_value=1, max_value=10, value=1, step=1)

    def get_resp_func(item, history):
        prompt = item["prompt"]
        resp = ""
        try:
            json_data = {
                'knowledge_base_id': knowledge_base_id,
                'question': prompt,
                "prompt_template": prompt_template,
                'history': history,
            }
            resp = requests.post(f'{host}/local_doc_chat', json=json_data)
            resp.raise_for_status()
            resp = resp.json()
            response = resp["response"]
            reference = resp["source_documents"]
            item.update(response=response, reference=reference,
                        settings=dict(host=host, knowledge_base_id=knowledge_base_id))
        except Exception as e:
            logger.exception(e)
        return dict(prompt=prompt, response=response)

    load_batch_view(get_resp_func=get_resp_func, workers=work_num)
