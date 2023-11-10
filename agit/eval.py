#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/11/10 12:30:19
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
from agit.utils import getlog
from agit import AGIT_ENV
import re
import requests


logger = getlog(AGIT_ENV, __file__)


PREFIX_PROMPT_WITH_REF = "[Instruction]\nPlease act as an impartial judge and evaluate the quality of the response provided by an AI assistant to the user question displayed below. Your evaluation should consider factors such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of the response. Begin your evaluation by providing a short explanation. You will be given a high-quality reference answer and the assistant's answer. Be as objective as possible. You should first provide your explanation IN CHINESE, then you must rate the response on a scale of 1 to 10 by STRICTLY following the below MAPPING for the relation between the scores and response quality:\n1) The score 1~2 stands for very chaotic or absence of answer, and the AI assissant completely failed to address the instructions. Serious mathematical, logical and factual errors might also be included in this term. The gap between the AI assistant's answer and the high-quality reference answer is huge and insuperable.\n2) The score 3~4 indicates fragment-like responses from AI assistant's answer. It did not provide answers in proper grammar, fluency, or accuracy. There are obvious gaps between the high-quality reference answer and the AI assistant's response.\n3) The score 5~6 indicates for existence of minute disadvantage from the AI assistant's answer compared to the high-quality reference answer. Yet the AI assistant did provide an average answer. The AI assistant either did not fully satisfy instructions, or was somewhat short of helpfulness, relevance, depth, creativity, or detailedness. The disadvantages from the AI assistant's answer overwhelm its advantages.\n4) The score 7~8 indicates the AI assistant provided a good answer as well as the high-quality reference answer, satisfying the instruction, while addressing good helpfulness, relevance, accuracy, depth, creativity, and level of detail of the response. The AI assistant might have flaws compared to the reference answer, but that does not overwhelm the above advantages.\n5) The score 9~10 indicates the AI assistant responsed better than the provided reference answer in most aspects, fully achieved the instruction goal, and have unique advantages to the reference answer.\nYou should give scores around 7 if you do not find obvious advantages or disadvantages. You should seriously consider the above guide before give lowest and highest scores such as 1 or 10, and avoid such situation if you do not have sound explanations.\nAvoid any positional biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Do not favor certain names of the assistants. AND again, VERY IMPORTANTLY, after you provide your explanation IN CHINESE, you must rate the response strictly following this format: \"[[rating]]\", for example: \"Rating: [[5]]\"."


def format_prompt_with_ref(question, reference, answer):
    return PREFIX_PROMPT_WITH_REF + f"\n\n[Question]\n{question}\n\n[The Start of Reference Answer]\n{reference}\n[The End of Reference Answer]\n\n[The Start of Assistant's Answer]\n{answer}\n[The End of Assistant's Answer]"


def eval_by_ref(question, reference, answer):
    logger.debug(f"Evaluating by reference answer: {reference}")
    prompt = format_prompt_with_ref(question, reference, answer)
    data = {
        "model": "chatglm2",
        "prompt": prompt,
        "seed": 34,
        "do_sample": False,
        "max_tokens": 256,
        "stream": False
    }
    header = {
        "Host": "api-research-score-32b-0926.glm.ai"
    }
    resp = requests.post(url="https://117.161.233.25:8443/v1/completions", verify=False, headers=header, json=data)
    resp.raise_for_status()
    text = resp.json()["choices"][0]["text"]
    # logger.info(text)
    idx = text.index("评分")
    reason = text[:idx].strip()
    pattern = "\[\[(.*?)\]\]"
    score = re.findall(pattern, text[idx + 3:])
    score = eval(score[0])

    # score = eval(text[idx + 3:])[0][0]
    return {"reason": reason, "score": score}


if __name__ == "__main__":
    print(eval_by_ref(question="中国人口有多少", reference="", answer="1亿"))

    # print(eval_by_ref(question="贵州茅台营收是多少", reference="100亿", answer="10000000000"))
