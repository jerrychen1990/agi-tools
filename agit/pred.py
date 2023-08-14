#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/08/14 16:46:37
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


from typing import List

from snippets import batch_process
from tqdm import tqdm

from agit.zhipu import ZhipuAgent


def batch_predict(prompts: List[str], agent, params, work_num) -> List:
    batch_func = batch_process(work_num=work_num)(lambda x: agent(x, **params))
    return batch_func(prompts)


if __name__ == "__main__":
    prompts = ["你好", "你是谁", "谁是世界上最聪明的人"]
    agent = ZhipuAgent()
    rs = batch_predict(prompts, agent, dict(stream=False), 2)
    for q, a in zip(prompts, rs):
        print(f"{q} -> {a}")
