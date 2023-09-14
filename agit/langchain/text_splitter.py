#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/13 10:36:06
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
import re
from typing import List

from langchain.text_splitter import TextSplitter
from snippets import batchify, flat


def _cut2maxlen(text, max_len):
    if len(text) < max_len:
        return [text]
    return ["".join(e) for e in batchify(text, max_len)]


def merge(pieces: list[str], joiner=",", min_len=10, max_len=100, overlap=0.3):
    pieces = flat([_cut2maxlen(e, max_len)for e in pieces])
    result = []

    idx = 0
    acc = []
    sum_len = 0
    while idx < len(pieces):
        p = pieces[idx]
        if not acc:
            acc.append(p)
            sum_len += len(p)
            idx += 1
        else:
            if sum_len + len(p) > max_len:
                result.append(joiner.join(acc))
                acc.clear()
                sum_len = 0
            else:
                acc.append(p)
                sum_len += len(p)
                idx += 1
    if acc:
        result.append(joiner.join(acc))
    return result


class SmartTextSplitter(TextSplitter):
    def __init__(self, split_pattern="[,，。?\？！!\n]|\.{3+}"):
        super().__init__()
        self.split_pattern = split_pattern

    def split_text(self, text: str, **kwargs) -> List[str]:
        pieces = re.split(self.split_pattern, text)
        pieces = [e.strip() for e in pieces if e.strip()]
        merged = merge(pieces,  **kwargs)
        return merged


if __name__ == "__main__":
    text = "你好，哈哈哈，这是一段很长很长很长很长很长很长很长很长很长很长很长很长很长很长的 文本呀，啦啦啦"
    splitter = SmartTextSplitter()
    pieces = splitter.split_text(text, min_len=5, max_len=20, overlap=0.3)
    for p in pieces:
        print(p)
