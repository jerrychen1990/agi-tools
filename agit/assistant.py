#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/16 10:56:19
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


from lib2to3 import pytree
import os

from typing import List, Union, Generator
from agit import AGIT_ENV, assistant_default_prompt_template, AGIT_TEMP_DIR

from agit.backend import call_llm_api
from agit.tool import Tool, get_tool
from agit.utils import ConfigMixin
from snippets import getlog, jdumps
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
                 system=None,
                 tools: List[Union[str, Tool]] = [],
                 kb_config=dict()) -> None:
        self.name = name
        self.llm_model = llm_model
        self.history = []
        self.prompt_template = prompt_template
        self.system = system
        self._init_tools(tools)

        if "name" not in kb_config:
            kb_config["name"] = f"{self.name}_kb"
        if not tmp_dir:
            tmp_dir = os.path.join(AGIT_TEMP_DIR, "temp_knowledge")
        self.tmp_dir = tmp_dir
        self.kb = KnowledgeBase.from_config(kb_config)

    def _init_tools(self, tools: List[Union[str, Tool]]):
        self.tools: List[Tool] = []
        for tool in tools:
            if isinstance(tool, str):
                try:
                    tool = get_tool(tool)
                    self.tools.append(tool)
                except Exception as e:
                    print(e)
                    pass
            else:
                self.tools.append(tool)

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

    def _build_tool_info(self):
        return [t.model_dump(exclude={"func"}) for t in self.tools]

    def chat(self, message: str, stream=False, use_history=True, llm_model=None,
             use_tool=False, use_kb=True,
             temperature=0.7, top_k=4, threshold=None, **kwargs) -> AssistantResp:

        if use_kb:
            chunks = self.kb.search(
                message, top_k=top_k, threshold=threshold)
            logger.info("references details")
            for idx, chunk in enumerate(chunks):
                logger.debug(f"[{idx+1}] - {chunk}")
            prompt = self._build_prompt(message, chunks)

        else:
            chunks = []
            prompt = message

        tools = self._build_tool_info() if use_tool else None

        resp = call_llm_api(prompt=prompt, model=llm_model if llm_model else self.llm_model,
                            history=self.history if use_history else [],
                            system=self.system, tools=tools,
                            verbose=logger.level,  temperature=temperature, stream=stream,
                            do_search=True, search_query=message, **kwargs)

        self.history.append(dict(role="user", content=message))
        if isinstance(resp, str):
            self.history.append(dict(role="assistant", content=resp))

        tool_name, kwargs = self.tool_parse(resp)
        logger.info(f"{tool_name=}, {kwargs=}")

        if tool_name:
            tool_resp = self.tool_call(tool_name, **kwargs)
            logger.info(f"tool_resp: {tool_resp}")
            if tool_resp:
                message = jdumps(tool_resp)
                resp = self.chat(message=message, stream=stream, use_history=use_history,
                                 use_tool=use_tool, use_kb=use_kb, temperature=0.7, top_k=4, threshold=None, **kwargs, role="observation")
                return resp

        # TODO resp是迭代器时的特殊处理

        # logger.info(f"chunks: {chunks}")
        resp = AssistantResp(content=resp, references=chunks)
        return resp

    def tool_call(self, tool_name, *args, **kwargs):
        logger.debug(f"try to call {tool_name} with {kwargs=}")

        tool_map = {t.name: t.func for t in self.tools}
        if tool_name not in tool_map:
            logger.warning(f"tool not found: {tool_name}")
            resp = {}
        else:
            func = tool_map[tool_name]
            resp = func(*args, **kwargs)
        return resp

    def learn(self, knowledge_or_path: str):
        if os.path.exists(knowledge_or_path):
            self.kb.add_document(knowledge_or_path)
        else:
            self.kb.learn(knowledge_or_path)

    def store(self):
        import re
        re.DT
        re.findall
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

    def add_tool(self, tool: Tool):
        self.tools.append(tool)

    def tool_parse(self, content: str):
        import re
        pattern = '''(.*?)\s+```python\s+tool_call(.*?)\s+```'''
        for item in re.findall(pattern, content, re.DOTALL):
            func_name, kwargs = item
            try:
                kwargs = "dict"+kwargs
                kwargs = eval(kwargs)
                func_name, kwargs
                return func_name, kwargs
            except Exception as e:
                pass
        return None, None
