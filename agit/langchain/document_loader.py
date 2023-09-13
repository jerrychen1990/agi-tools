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
        self.reader = DocumentReader()
        self.file_path = file_path

    def load(self):
        content = self.reader.read(self.file_path)
        metadata = {"source": self.file_path}
        return [Document(page_content=content, metadata=metadata)]
