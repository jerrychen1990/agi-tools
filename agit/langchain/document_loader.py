#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/13 10:40:06
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

from langchain.docstore.document import Document
from langchain.document_loaders.base import BaseLoader

from agit.doc_tool import DocumentReader


class SmartDocumentLoader(BaseLoader):
    def __init__(self, file_path: str):
        self.read_func = {
            "html": self.read_html,
            "htm": self.read_html,
        }
        self.file_path = file_path

    def read_html(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        import html2text
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.mark_code = True

        text = h.handle(content)

        return text

    def load(self):
        surfix = self.path.split(".")[-1]
        if surfix not in self.read_func:
            raise ValueError(f"unsupported file suffix: {surfix}")
        func = self.read_func[surfix]
        content = func(self.path)
        metadata = {"source": self.file_path}
        return [Document(page_content=content, metadata=metadata)]
