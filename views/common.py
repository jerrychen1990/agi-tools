#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/19 18:33:02
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import os

from agit.utils import getlog

logger = getlog(os.environ.get("AGIT_ENV", "dev"), __name__)


def load_chat_view(get_resp_func):
    import streamlit as st

    if "messages" not in st.session_state:
        st.session_state.messages = []
    st.session_state.setdefault("history", [])

    # Accept user input
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("你好，你是谁？"):
        # st.info(prompt)
        # Add user message to chat history
        # logger.info("add message")
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

        resp = get_resp_func(prompt)
        for token in resp:
            full_response += token
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "user", "content": prompt})
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
