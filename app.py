import logging

import streamlit as st

from views import (batch_llm, character_chat, chatbot, model_chat, similarity,
                   test_llm_api)

st.set_page_config(layout="wide", page_title='AI工具集合')
# st.set_option('deprecation.showPyplotGlobalUse', False)


NAVBAR_PATHS = {
    '文本相似度': 'similarity',
    'api测试': 'test_llm_api',
    "批量测试": 'batch_llm',
    "角色对话": "character_chat",
    "聊天机器人": "chatbot",
    "模型对话": "model_chat"

}
_view_map = {
    "similarity": similarity,
    "test_llm_api": test_llm_api,
    "batch_llm": batch_llm,
    "character_chat": character_chat,
    "chatbot": chatbot,
    "model_chat": model_chat
}


SETTINGS = {
    'OPTIONS': 'options',
    'CONFIGURATION': 'configuration'
}


def inject_custom_css():
    with open('assets/styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def get_current_route():
    try:
        return st.experimental_get_query_params()['nav'][0]
    except:
        return None


def navbar_component():
    navbar_items = ''
    for key, value in NAVBAR_PATHS.items():
        navbar_items += (
            f'<a class="navitem"  target="_self" href="/?nav={value}">{key}</a>')
    component = rf'''
            <nav class="container navbar" id="navbar">
                <ul class="navlist">
                {navbar_items}
                </ul>
            </nav>
            '''
    st.markdown(component, unsafe_allow_html=True)


logging.getLogger().setLevel(logging.INFO)


inject_custom_css()
navbar_component()


def navigation():
    route = get_current_route()
    view = _view_map.get(route, similarity)
    view.load_view()


navigation()
