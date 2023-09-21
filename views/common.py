#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/19 18:33:02
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import os
import time

import pandas as pd
import streamlit as st
from snippets import get_current_time_str
from tqdm import tqdm

from agit.utils import getlog, save_csv_xls
from views import TMP_DIR

logger = getlog(os.environ.get("AGIT_ENV", "dev"), __name__)


def load_chat_view(get_resp_func):
    if "messages" not in st.session_state:
        st.session_state.messages = []

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


def load_batch_view(get_resp_func):
    uploaded_file = st.file_uploader(
        label=f"上传文件，xlsx,csv类型，必须有一列名称是prompt", type=["xlsx", "csv"])
    submit = st.button(label='批量测试')
    t = time.time()
    if submit:
        history = []
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        results = []
        prompts = df['prompt'].tolist()
        total = len(prompts)
        for idx, prompt in tqdm(enumerate(prompts)):
            rs_item = get_resp_func(prompt=prompt, history=history)

            results.append(rs_item)
            cost = time.time() - t
            avg_cost = cost / (idx + 1)
            st.markdown(f"**第{idx + 1}条**")
            st.markdown(f"**prompt**:{prompt}")
            st.markdown(f"**resp**:{rs_item}")
            st.markdown(
                f"进度[{idx + 1} / {total}], 耗时{cost:2.2f}s, 平均单条耗时{avg_cost:2.2f}s, 预估剩余{avg_cost * (total - idx - 1):2.2f}s")
            st.markdown("*" * 30)
        st.markdown("任务完成")
        rs_df = pd.DataFrame.from_records(results)

        stem, surfix = uploaded_file.name.split(".")
        dst_file_name = f"{stem}_{get_current_time_str('%Y%m%d%H%M%S')}.{surfix}"
        st.info(f"writing file to {dst_file_name}")
        dst_file_path = f"{TMP_DIR}/{dst_file_name}"
        save_csv_xls(rs_df, dst_file_path)
        with open(dst_file_path) as f:
            download = st.download_button(
                "下载文件", data=f, file_name=dst_file_name)
