#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 17:43:15
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import enum
import imp
import os
import re
import time

import pandas as pd
from snippets import get_current_time_str
from tqdm import tqdm

from agit.backend.zhipuai_bk import call_llm_api
from agit.utils import save_csv_xls

model_cands = ["chatglm_lite", "chatglm_std", "chatglm_pro"]
view_name = "batch_llm"
tmp_dir = "/tmp/streamlit"
if not os.path.exists(tmp_dir):
    os.makedirs(tmp_dir)


def load_view():
    import streamlit as st
    prompt_template = st.sidebar.text_area(key=f"{view_name}_prompt_template", label="套在prompt上的模板,用{{content}}槽位表示",
                                           value="{{content}}")
    temperature = st.sidebar.slider(key=f"{view_name}_temperature", label="temperature",
                                    min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    top_p = st.sidebar.slider(key=f"{view_name}_top_p", label="top_p", min_value=0.01,
                              max_value=1.0, value=0.7, step=0.01)
    multi_turn = st.sidebar.checkbox(
        key=f"{view_name}_multi_turn", label="是否开启多轮对话", value=False)
    if multi_turn:
        history_len = st.sidebar.slider(key=f"{view_name}_history_len", label="历史长度（轮），一对问答为一轮",
                                        min_value=0, max_value=10, value=5, step=1)
    else:
        history_len = 0

    model = st.sidebar.selectbox(
        key=f"{view_name}_models", label="选择模型", options=model_cands)

    uploaded_file = st.file_uploader(
        label=f"上传文件，xlsx,csv类型，必须有一列名称是prompt", type=["xlsx", "csv"])
    submit = st.button(label='批量测试')
    t = time.time()
    if submit:
        history = []
        dataframe = pd.read_csv(uploaded_file)
        results = []
        records = dataframe.to_dict(orient="records")
        total = len(records)
        for idx, item in tqdm(enumerate(records)):
            prompt = item["prompt"]
            prompt_with_template = prompt_template.replace(
                "{{content}}", prompt)
            history_start = max(0, len(history) - 2*history_len)
            resp = call_llm_api(
                prompt=prompt_with_template, history=history[history_start:], temperature=temperature, top_p=top_p, model=model, stream=False)
            rs_item = dict(prompt=prompt, prompt_with_template=prompt_with_template, response=resp,
                           settings=dict(temperature=temperature, top_p=top_p, model=model))
            results.append(rs_item)
            cost = time.time() - t
            avg_cost = cost/(idx+1)
            st.markdown(f"**第{idx+1}条**")
            st.markdown(f"**prompt**:{prompt}")
            st.markdown(f"**resp**:{resp}")
            st.markdown(
                f"进度[{idx+1}/{total}], 耗时{cost:2.2f}s, 平均单条耗时{avg_cost:2.2f}s, 预估剩余{avg_cost*(total-idx-1):2.2f}s")
            st.markdown("*"*30)
            history.extend([dict(role="user", content=prompt),
                            dict(role="assistant", content=resp)])
        st.markdown("任务完成")

        stem, surfix = uploaded_file.name.split(".")
        dst_file_name = f"{stem}_{get_current_time_str('%Y%m%d%H%M%S')}.{surfix}"
        st.info(f"writing file to {dst_file_name}")
        rs_df = pd.DataFrame.from_records(results)
        # st.table(rs_df)
        dst_file_path = f"{tmp_dir}/{dst_file_name}"
        save_csv_xls(rs_df, dst_file_path)
        with open(dst_file_path) as f:
            download = st.download_button(
                "下载文件", data=f, file_name=dst_file_name)
