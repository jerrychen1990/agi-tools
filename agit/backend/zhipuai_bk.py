#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/11 10:19:27
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


import copy
import itertools
import logging
import os
from typing import Any, Union
from loguru import logger

import numpy as np
import zhipuai
from agit import AGIT_LOG_HOME
from snippets import retry, jdumps


from agit.utils import gen_req_id

fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <level>{level: <8}</level>|  - <level>[{extra[request_id]}]{message}</level>"

logger.add(os.path.join(AGIT_LOG_HOME,"zhipuai_bk.log"), retention="365 days", rotation=" 00:00", level="DEBUG", filter=__name__, format=fmt) 

default_logger = logger

def check_api_key(api_key):
    if api_key is None:
        api_key = os.environ.get("ZHIPUAI_API_KEY", None)
    if not api_key:
        raise ValueError("未设置api_key且未设置ZHIPUAI_API_KEY环境变量")
    zhipuai.api_key = api_key


def resp_generator(events, max_len=None, err_resp=None):
    token_left = max_len if max_len else None
    for event in events:
        if event.event == "add":
            if token_left:
                if len(event.data) > token_left:
                    data = event.data[:token_left]
                else:
                    data = event.data
                token_left -= len(data)
                yield data
                if token_left == 0:
                    break
            else:
                yield event.data
        elif event.event == "finish":
            pass
        else:
            default_logger.error(
                f"zhipu api resp failed with event:{event.event}, data:{event.data}")
            yield err_resp if err_resp else event.data


def support_system(model: str):
    return model.startswith("chatglm3") or model in ["glm-4", "glm-3-turbo"]


# sdk请求模型
def call_llm_api_v1(prompt: str, model: str, history=[], logger=None,
                    api_key=None, stream=True, max_len=None, max_history_len=None,
                    verbose=logging.INFO, max_single_history_len=None,
                    do_search=True, search_query=None,
                    system=None, **kwargs) -> Any:
    check_api_key(api_key)

    if logger is None:
        the_logger = default_logger
        the_logger.setLevel(verbose)
    else:
        the_logger = logger

    if max_history_len:
        the_logger.debug(
            f"history length:{len(history)}, cut to {max_history_len}")
        history = history[-max_history_len:]
    if max_single_history_len:
        the_logger.debug(
            f"cut each history's length to {max_single_history_len}")
        history = [dict(role=e['role'], content=e['content']
                        [:max_single_history_len]) for e in history]
    zhipu_prompt = history + [dict(role="user", content=prompt)]
    if system:
        if not support_system(model):
            the_logger.warn(f"{model} not support system")
        else:
            zhipu_prompt = [dict(role="system", content=system)] + zhipu_prompt

    total_words = sum([len(e['content']) for e in zhipu_prompt])
    the_logger.debug(f"zhipu prompt:")
    detail_msgs = []

    for idx, item in enumerate(zhipu_prompt):
        detail_msgs.append(f"[{idx+1}].{item['role']}:{item['content']}")
    the_logger.debug("\n"+"\n".join(detail_msgs))

    if "ref" not in kwargs:
        ref = dict(enable=do_search, query=search_query if search_query else prompt)
        kwargs.update(ref=ref)
    if "request_id" not in kwargs:
        request_id = gen_req_id(prompt=prompt, model=model)
        kwargs.update(request_id=request_id)
    show_kwargs = copy.copy(kwargs)
    del show_kwargs["ref"]

    the_logger.debug(
        f"api_version:[v1], {model=}, {stream=}, history_len={len(history)}, words_num={total_words}, {show_kwargs=}")
    response = zhipuai.model_api.sse_invoke(
        model=model,
        prompt=zhipu_prompt,
        **kwargs
    )
    generator = resp_generator(response.events(), max_len=max_len)
    if stream:
        return generator
    else:
        resp = "".join(list(generator)).strip()
        if max_len:
            resp = resp[:max_len]
        return resp


def resp2generator_v4(resp, logger, request_id):
    tool_calls = None
    acc_chunks = []

    for chunk in resp:
        choices = chunk.choices
        if choices:
            choice = choices[0]
            tool_calls = choice.delta.tool_calls
            acc_chunks.append(chunk)
        break
    # print(acc_chunks)

    def gen():
        acc = []
        for chunk in itertools.chain(acc_chunks, resp):
            choices = chunk.choices                
            if choices:
                choice = choices[0]
                if choice.delta.content:
                    delta_content = choice.delta.content
                    yield delta_content
                    acc.append(delta_content)
        resp_msg = "".join(acc).strip()
        with logger.contextualize(request_id=request_id):
            logger.debug(f"model generate answer:{resp_msg}")
                    
            
    return tool_calls, gen()


def call_llm_api_v4(prompt: Union[str, dict], model: str, api_key=None, role="user",
                    system=None, history=[], tools=[], do_search=False, search_query=None,
                    logger=None, stream=True, return_origin=False, return_tool_call=False, **kwargs) -> Any:
    from zhipuai import ZhipuAI
    import inspect
    client = ZhipuAI(api_key=api_key or os.environ.get("ZHIPU_API_KEY"))
    if "request_id" not in kwargs:
        request_id = gen_req_id(prompt=prompt, model=model)
        kwargs.update(request_id=request_id)   
    request_id = kwargs["request_id"]
    the_logger = logger if logger else default_logger

    
    with the_logger.contextualize(request_id=request_id):
        valid_keys = dict(inspect.signature(client.chat.completions.create).parameters).keys()

        
        if isinstance(prompt, dict):
            messages = history + [prompt]
        else:
            messages = history + [dict(role=role, content=prompt)]
        if system:
            if support_system(model):
                messages = [dict(role="system", content=system)] + messages
            else:
                the_logger.warning(f"{model} not support system message, system argument will not work")

        detail_msgs = []
        for idx, item in enumerate(messages):
            detail_msgs.append(f"[{idx+1}].{item['role']}:{item['content']}")
        the_logger.debug("\n"+"\n".join(detail_msgs))

        tools = copy.copy(tools)

            
        if not do_search:
            close_search_tool = {'type': 'web_search', 'web_search': {'enable': False, 'search_query': search_query}}
            tools.append(close_search_tool)
            # the_logger.debug(f"adding close search tool")
            
        kwargs = {k: v for k, v in kwargs.items() if k in valid_keys}
        # 处理temperature=0的特殊情况
        if kwargs.get("temperature") == 0:
            kwargs.pop("temperature")
            kwargs["do_sample"]=False
        

        api_inputs = dict(model=model,
            messages=messages,
            tools=tools,
            stream=stream,
            **kwargs)
        the_logger.debug(f"api_inputs:\n{jdumps(api_inputs)}")
        

        
        if return_origin:
            resp =  client.chat.completions.create(
                **api_inputs
            )
            logger.info(f"api origin resp:{resp}")
            return resp

        api_inputs.update(stream=True)
        response = client.chat.completions.create(
            **api_inputs
        )
        # usage = response.usage
        # the_logger.debug(f"token usage: {usage}")

        tool_call, resp_gen = resp2generator_v4(response, logger=the_logger, request_id=request_id)

        if not stream:
            resp_gen = "".join(resp_gen)
        if return_tool_call:
            return tool_call, resp_gen
        
        return resp_gen


def call_llm_api(*args, **kwargs):
    if "__version__" in vars(zhipuai):
        version = zhipuai.__version__
        # default_logger.debug(f"using version {version}")
        return call_llm_api_v4(*args, **kwargs)
    else:
        # default_logger.debug(f"using version v1")
        return call_llm_api_v1(*args, **kwargs)


def call_character_api(prompt: str, user_name, user_info, bot_name, bot_info,
                       history=[], model="characterglm", api_key=None, stream=True, max_len=None, **kwargs):
    check_api_key(api_key)
    zhipu_prompt = history + [dict(role="user", content=prompt)]
    total_words = sum([len(e['content']) for e in zhipu_prompt])
    default_logger.debug(f"zhipu prompt:")
    detail_msgs = []

    for idx, item in enumerate(zhipu_prompt):
        detail_msgs.append(f"[{idx+1}].{item['role']}:{item['content']}")
    default_logger.debug("\n"+"\n".join(detail_msgs))
    default_logger.debug(
        f"{model=},{kwargs=}, history_len={len(history)}, words_num={total_words}")
    meta = {
        "user_info": user_info,
        "bot_info": bot_info,
        "bot_name": bot_name,
        "user_name": user_name
    }
    response = zhipuai.model_api.sse_invoke(
        model=model,
        meta=meta,
        prompt=zhipu_prompt,
        incremental=True,
        ** kwargs
    )
    generator = resp_generator(response.events(), max_len=None)
    if stream:
        return generator
    else:
        resp = "".join(list(generator)).strip()
        if max_len:
            resp = resp[:max_len]
        return resp


def call_embedding_api(*args, **kwargs):
    if "__version__" in vars(zhipuai):
        version = zhipuai.__version__
        # default_logger.debug(f"using version {version}")
        return call_embedding_api_v4(*args, **kwargs)
    else:
        # default_logger.debug(f"using version v1")
        return call_embedding_api_v1(*args, **kwargs)


def call_embedding_api_v4(text: str, api_key=None, model="text_embedding_v2",
                          norm=None, retry_num=2, wait_time=1):

    from zhipuai import ZhipuAI

    client = ZhipuAI(api_key=api_key or os.environ.get("ZHIPU_API_KEY"))

    def attempt():
        resp = client.embeddings.create(
            model=model,  # 填写需要调用的模型名称
            input=text,
        )
        embedding = resp.data[0].embedding
        if norm is not None:
            _norm = 2 if norm == True else norm
            embedding = embedding / np.linalg.norm(embedding, _norm)
        return embedding

    if retry_num:
        attempt = retry(retry_num=retry_num, wait_time=wait_time)(attempt)
    return attempt()


def call_embedding_api_v1(text: str, api_key=None, norm=None, retry_num=2, wait_time=1):
    check_api_key(api_key)

    def attempt():
        resp = zhipuai.model_api.invoke(
            model="text_embedding",
            prompt=text
        )
        if resp["code"] != 200:
            default_logger.error(f"embedding error:{resp['msg']}")
            raise Exception(resp["msg"])
        embedding = resp["data"]["embedding"]
        if norm is not None:
            _norm = 2 if norm == True else norm
            embedding = embedding / np.linalg.norm(embedding, _norm)
        return embedding

    if retry_num:
        attempt = retry(retry_num=retry_num, wait_time=wait_time)(attempt)
    return attempt()


def call_image_gen(prompt:str, api_key:str=None)->str:
    from zhipuai import ZhipuAI
    client = ZhipuAI(api_key=api_key or os.environ.get("ZHIPU_API_KEY"))

    response = client.images.generations(
        model="cogview-3", #填写需要调用的模型名称
        prompt=prompt,
    )
    return response.data[0].url



if __name__ == "__main__":
    text = "你好"
    system = "你是孔子，请以文言文回答我"
    resp = "".join(call_llm_api(model="chatglm3_130b_int8", prompt=text, system=system, stream=False))
    print(resp)
    emb = call_embedding_api(text)
    print(len(emb))
    print(emb[:4])
