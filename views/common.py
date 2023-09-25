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
from snippets import batch_process, get_current_time_str
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
            # st.info(full_response)
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        st.session_state.messages.append(
            {"role": "user", "content": prompt})
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})


def load_batch_view(get_resp_func, workers=1, save_interval=20, overwrite=False):
    def save_file():
        dst_file_name = f"{stem}_{idx}_{len(records)}_{get_current_time_str('%Y%m%d%H%M%S')}.{surfix}"
        dst_file_path = f"{TMP_DIR}/{dst_file_name}"
        rs_df = pd.DataFrame.from_records(records)
        logger.info(f"writing file to {dst_file_path}")
        save_csv_xls(rs_df, dst_file_path)
        with open(dst_file_path, "rb") as f:
            byte_content = f.read()
            st.download_button(label="下载文件", key=dst_file_name, data=byte_content,
                               file_name=dst_file_name, mime="application/octet-stream")

    uploaded_file = st.file_uploader(
        label=f"上传文件，xlsx,csv类型，必须有一列名称是prompt", type=["xlsx", "csv"])
    submit = st.button(label='批量测试')

    if submit:
        history = []
        t = time.time()
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        batch_func = batch_process(workers)(get_resp_func)
        df.fillna("", inplace=True)
        records = df.to_dict(orient="records")

        idx = 0
        while not overwrite and idx < len(records) and records[idx].get("response"):
            logger.info(records[idx].get("response"))
            idx += 1

        results = batch_func(records[idx:], history)

        save_batch = max(4, len(records) // save_interval)
        logger.info(idx)

        st.info(
            f"{len(records) - idx}个待处理条目,{workers}个并发,每{save_batch}条保存一次")

        stem, surfix = uploaded_file.name.split(".")

        # progress_detail = st.empty()
        for item in results:
            # item = results[idx]
            idx += 1

            cost = time.time() - t
            pct = (idx)/len(records)
            text = f"{cost/idx:.2f}s/item, [{idx}/{len(records)}], [{cost:.2f}s/{cost/pct:.2f}s]"
            st.progress(value=pct, text=text)
            for k, v in item.items():
                st.info(f"{k}:{v}")
            if idx % save_batch == 0:
                save_file()

        if idx % save_batch != 0:
            save_file()
        st.markdown("任务完成")
