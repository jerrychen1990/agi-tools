#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/13 10:25:05
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


from typing import List

from langchain.embeddings.base import Embeddings
from pydantic import BaseModel
from tqdm import tqdm

from agit.backend.zhipuai_bk import call_embedding_api


class ZhipuAIEmbeddings(BaseModel, Embeddings):
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        rs = []
        for text in tqdm(texts):
            emb = call_embedding_api(text=text)
            rs.append(emb)
        return rs

    def embed_query(self, text: str) -> List[float]:
        emb = call_embedding_api(text)
        return emb
