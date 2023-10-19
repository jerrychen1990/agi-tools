#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/16 10:56:19
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


import os

from typing import List, Union, Generator
from agit import AGIT_ENV, assistant_default_prompt_template, AGIT_TEMP_DIR

from agit.backend import call_llm_api
from agit.utils import ConfigMixin
from snippets import getlog
from pydantic import BaseModel
from agit.kb import Chunk, KnowledgeBase


logger = getlog(AGIT_ENV, __file__)


class AssistantResp(BaseModel):
    content: Union[str, Generator]
    references: List = []


class Assistant(ConfigMixin):
    def __init__(self, name: str,
                 llm_model="chatglm_lite",
                 prompt_template=assistant_default_prompt_template,
                 tmp_dir=None,
                 kb_config=dict()) -> None:
        self.name = name
        self.llm_model = llm_model
        self.history = []
        self.prompt_template = prompt_template
        if "name" not in kb_config:
            kb_config["name"] = f"{self.name}_kb"
        if not tmp_dir:
            tmp_dir = os.path.join(AGIT_TEMP_DIR, "temp_knowledge")
        self.tmp_dir = tmp_dir

        self.kb = KnowledgeBase.from_config(kb_config)

    def __call__(self, *args, **kwargs):
        return self.chat(*args, **kwargs)

    def _build_prompt(self, message: str, chunks: List[Chunk]) -> str:
        prompt = self.prompt_template.replace("{{message}}", message)
        reference = ""
        for idx, chunk in enumerate(chunks):
            reference += f"{idx+1}.{chunk.page_content}"
            reference += "\n\n"

        prompt = prompt.replace("{{reference}}", reference)
        return prompt

    def chat(self, message: str, stream=False, use_history=True, llm_model=None,
             use_kb=True, temperature=0.7, top_k=4, threshold=None) -> AssistantResp:

        if use_kb:
            chunks = self.kb.search(
                message, top_k=top_k, threshold=threshold)
            logger.info("references details")
            for idx, chunk in enumerate(chunks):
                logger.debug(f"[{idx+1}] - {chunk}")
        else:
            chunks = []

        prompt = self._build_prompt(message, chunks)

        resp = call_llm_api(prompt=prompt, model=llm_model if llm_model else self.llm_model, history=self.history if use_history else [],
                            verbose=logger.level,  temperature=temperature, stream=stream)

        self.history.append(dict(role="user", content=message))
        if isinstance(resp, str):
            self.history.append(dict(role="assistant", content=resp))

            # TODO resp是迭代器时的特殊处理

        logger.info(f"chunks: {chunks}")
        resp = AssistantResp(content=resp, references=chunks)
        return resp

    def learn(self, knowledge_or_path: str):
        if os.path.exists(knowledge_or_path):
            self.kb.add_document(knowledge_or_path)
        else:
            self.kb.learn(knowledge_or_path)

    def store(self):
        self.kb.store()

    @property
    def chunk_num(self):
        return self.kb.chunk_num

    def search_db(self, *args, **kwargs):
        return self.kb.search(*args, **kwargs)

    def clear_history(self):
        self.history = []

    def add_document(self, doc_path, **kwargs):
        self.kb.update_document(doc_path, **kwargs)
        self.kb.store()

    # TODO 暴露这个接口不安全
    def add_resp(self, resp: str):
        self.history.append(dict(role="assistant", content=resp))
