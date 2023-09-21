#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 17:43:10
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from scripts.cal_text_similarity import sort_similarity


def load_view():
    embedding_model = st.sidebar.selectbox(
        "embedding模型", options=["zhipu_api"])
    metric = st.sidebar.selectbox("相似度算法", options=["cosine", "l2_distance"])
    normalize = st.sidebar.checkbox("是否归一化", value=True)

    text = st.text_input("搜索词", value="足球最强的国家")
    default_cands = """巴西
==
德国
==
西班牙
==
中国
==
日本
    """
    cands = st.text_area("候选词（==）隔开", value=default_cands, height=300)

    # st.session_state.setdefault("cands", )

    # def on_add_cand():
    #     st.session_state.cands.append(st.session_state.cand)
    #     st.info(f"候选列表{st.session_state.cands}")

    # with st.container():
    #     st.text_input(label="候选词", on_change=on_add_cand, key="cand")

    submit = st.button("排序")
    if submit:
        # cands = st.session_state.cands
        cands = default_cands.split("==")
        cands = [e.strip() for e in cands if e.strip()]
        st.info(f"sorting {cands=}")
        rs = sort_similarity(text, cands, model_type=embedding_model,
                             normalize=normalize, metric=metric)

        fig = make_subplots()
        fig.update_layout(legend=dict(
            orientation="v",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ))
        fig.add_trace(go.Bar(x=[e[0] for e in rs], y=[e[1]
                      for e in rs], name="相似度/距离"))
        st.plotly_chart(fig, use_container_width=True)
