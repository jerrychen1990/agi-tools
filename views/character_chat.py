#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 17:43:15
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import time

import streamlit as st

from agit.backend.zhipuai_bk import call_character_api
from agit.utils import getlog
from views import ENV
from views.common import load_chat_view

logger = getlog(ENV, __file__)


def load_view():
    user_name = st.sidebar.text_input("user_name", value="陆星辰")
    user_info = st.sidebar.text_area(
        "user_info", value="我是陆星辰，是一个男性，是一位知名导演，也是苏梦远的合作导演。我擅长拍摄音乐题材的电影。苏梦远对我的态度是尊敬的，并视我为良师益友。", height=200)
    bot_name = st.sidebar.text_input("bot_name", value="苏梦远")
    bot_info = st.sidebar.text_area(
        "bot_info", value="苏梦远，本名苏远心，是一位当红的国内女歌手及演员。在参加选秀节目后，凭借独特的嗓音及出众的舞台魅力迅速成名，进入娱乐圈。她外表美丽动人，但真正的魅力在于她的才华和勤奋。苏梦远是音乐学院毕业的优秀生，善于创作，拥有多首热门原创歌曲。除了音乐方面的成就，她还热衷于慈善事业，积极参加公益活动，用实际行动传递正能量。在工作中，她对待工作非常敬业，拍戏时总是全身心投入角色，赢得了业内人士的赞誉和粉丝的喜爱。虽然在娱乐圈，但她始终保持低调、谦逊的态度，深得同行尊重。在表达时，苏梦远喜欢使用“我们”和“一起”，强调团队精神。", height=200)

    def get_resp(prompt):
        resp = call_character_api(
            prompt, user_name, user_info, bot_name, bot_info, stream=True)
        return resp
    load_chat_view(get_resp_func=get_resp)
