#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/13 10:36:06
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
from typing import List

from langchain.text_splitter import TextSplitter

from agit.doc_tool import TextCutter


class SmartTextSplitter(TextSplitter):
    def __init__(self):
        super().__init__()
        self.text_cutter = TextCutter()

    def split_text(self, text: str, **kwargs) -> List[str]:
        pieces = self.text_cutter.cut(text, **kwargs)
        return pieces
