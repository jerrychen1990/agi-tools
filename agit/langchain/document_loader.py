#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/13 10:40:06
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import logging

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

logger = logging.getLogger(__name__)


class SmartDocumentLoader(BaseLoader):
    def __init__(self, file_path: str):
        self.read_func = {
            "html": self.read_html,
            "htm": self.read_html,
            "txt": self.read_text,
        }
        self.file_path = file_path

    def read_text(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content

    def read_html(self, path: str) -> str:
        content = self.read_text(path=path)
        import html2text
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.mark_code = True
        text = h.handle(content)
        return text

    def load(self):
        surfix = self.file_path.split(".")[-1]
        if surfix not in self.read_func:
            logger.warning(
                f"unsupported file suffix: {surfix}, try to read as txt")
            func = self.read_text
        func = self.read_func[surfix]
        content = func(self.file_path)
        metadata = {"source": self.file_path}
        return [Document(page_content=content, metadata=metadata)]
