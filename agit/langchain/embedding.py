#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/13 10:25:05
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


from typing import List

from langchain.embeddings.base import Embeddings
import numpy as np
from pydantic import BaseModel
from tqdm import tqdm
from agit import AGIT_ENV

from agit.backend.zhipuai_bk import call_embedding_api
from agit.utils import getlog

logger = getlog(AGIT_ENV, __file__)


class ZhipuAIEmbeddings(BaseModel, Embeddings):
    norm: int = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        rs = []
        for text in tqdm(texts):
            emb = call_embedding_api(text=text, norm=self.norm)
            logger.debug(f"embedding of chunk:{text}, len:{len(emb)}, l2:{np.linalg.norm(emb)}")

            rs.append(emb)
        return rs

    def embed_query(self, text: str) -> List[float]:
        emb = call_embedding_api(text, norm=self.norm)
        logger.debug(f"embedding of query:{text}, len:{len(emb)}, l2:{np.linalg.norm(emb)}")

        return emb
