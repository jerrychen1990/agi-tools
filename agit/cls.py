#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/18 15:53:39
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


from typing import List, Tuple

from cachetools import LRUCache, cached
from tqdm import tqdm
from agit.backend.zhipuai_bk import call_embedding_api
from agit.utils import cal_vec_similarity
from snippets import getlog
from agit import AGIT_ENV

logger = getlog(AGIT_ENV, __file__)


@cached(LRUCache(maxsize=1000))
def get_cand_embeddings(cands: Tuple):
    rs = dict()
    logger.info("calculating cand embeddins")
    for cls, desc in tqdm(cands):
        emb = call_embedding_api(text=desc, norm=2)
        rs[cls] = emb
    return rs


def cls_by_embedding(query: str, cands: dict) -> dict:
    """
    根据query和cands的embedding计算相似度, 从而达到分类的效果
    """
    query_emb = call_embedding_api(text=query, norm=2)
    cand_embs = get_cand_embeddings(tuple(cands.items()))

    resp = []
    for cls, cand_emb in tqdm(cand_embs.items()):
        sim = cal_vec_similarity(query_emb, cand_emb, normalize=False, metric="cosine")
        resp.append((cls, sim))
    resp.sort(key=lambda x: x[1], reverse=True)
    sum_score = sum(e[1] for e in resp)
    resp = [dict(cls=cls, prob=score/sum_score, score=score) for cls, score in resp]
    return resp


if __name__ == "__main__":
    query = "讲一个笑话"
    cands = {
        "chat-funny": "有趣的内容，包括笑话、相声、段子",
        "chat-other": "普通的闲聊对话",
        "chat-idom": "成语接龙",
    }
    resp = cls_by_embedding(query, cands)
    logger.info(resp)
    resp = cls_by_embedding(query, cands)
    logger.info(resp)

    query = "讲一个笑话"
    cands = {
        "chat-funny": "讲一个笑话",
        "chat-other": "普通的闲聊对话",
        "chat-idom": "成语接龙",
    }
    resp = cls_by_embedding(query, cands)
    logger.info(resp)
