#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/11/01 15:27:35
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

from typing import Callable, List
from pydantic import BaseModel
import tushare as ts
from agit import AGIT_ENV
from snippets.logs import getlog

logger = getlog(AGIT_ENV, __file__)


class Parameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool


class Tool(BaseModel):
    name: str
    description: str
    parameters: List[Parameter]
    func: Callable


def track_stock(symbol):
    try:
        df = ts.get_realtime_quotes(symbol)
        return dict(price=df["price"][0])
    except Exception as e:
        logger.error(e)
        return {}


TRACK_STOCK = Tool(name="track_stock", description="追踪指定股票的实时价格", func=track_stock,
                   parameters=[Parameter(name="symbol", type="str", description="股票代码", required=True)])

ALL_TOOLS = [TRACK_STOCK]

_TOOL_DICT = {t.name: t for t in ALL_TOOLS}


def get_tool(tool_name: str) -> Tool:
    if tool_name not in _TOOL_DICT:
        raise Exception(f"tool {tool_name} not found")
    return _TOOL_DICT[tool_name]


if __name__ == "__main__":
    print(track_stock("000001"))
