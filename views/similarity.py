#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 17:43:10
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import re

import streamlit as st

from scripts.cal_text_similarity import sort_similarity


def load_view():
    text = st.text_input("搜索词", value="中国")
    cands = st.text_input("候选词列别，逗号隔开", value="北京，上海，东京，杭州")
    submit = st.button("排序")
    if submit:
        cands = re.split(",|，", cands)
        st.info(f"sorting {cands=}")
        rs = sort_similarity(text, cands)
        for k, v in rs:
            st.progress(v, f"{k}[{v:2.3f}]")
