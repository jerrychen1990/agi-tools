#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 17:43:15
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import re
import time

from agit.backend.zhipuai_bk import call_llm_api

model_cands = ["chatglm_lite", "chatglm_std", "chatglm_pro"]


def load_view():
    import streamlit as st
    prompt = st.sidebar.text_area("请求prompt", value="你好")
    prompt_template = st.sidebar.text_area(f"套在prompt上的模板,用{{content}}槽位表示",
                                           value="{{content}}")
    temperature = st.sidebar.slider(label="temperature",
                                    min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    top_p = st.sidebar.slider(label="top_p", min_value=0.01,
                              max_value=1.0, value=0.7, step=0.01)
    models = st.sidebar.multiselect(
        label="选择模型", options=model_cands, default=model_cands[0])
    rounds = st.sidebar.number_input(
        label="生成多少个", min_value=1, max_value=10, value=1)
    submit = st.sidebar.button("生成")
    if submit:
        for round in range(rounds):
            cols = st.columns(len(models))
            for col, model in zip(cols, models):
                t = time.time()
                prompt = prompt_template.replace("{{content}}", prompt)
                resp = call_llm_api(
                    prompt, temperature=temperature, top_p=top_p, model=model)
                resp = "".join(resp)
                cost = time.time() - t
                meta = f"{model} 第[{round+1}]轮，耗时:{cost:2.2f}s，{len(resp)}字"
                col.markdown(meta)
                col.info("".join(resp))
