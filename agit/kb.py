#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/16 10:55:23
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


from chunk import Chunk
import os
import hashlib
import shutil
import time

from typing import List, Optional
from agit import AGIT_ENV, AGIT_KB_DIR

from agit.langchain import (SmartDocumentLoader, SmartTextSplitter,
                            ZhipuAIEmbeddings)
from agit.utils import ConfigMixin
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from snippets import log_cost_time, log_function_info, getlog, create_dir_path
from pydantic import Field


logger = getlog(AGIT_ENV, __file__)


class Chunk(Document):
    score: Optional[float] = Field(default=None, description="检索时的相似度")

    @property
    def id(self):
        content = f"{self.page_content}&&{self.metadata['source']}"
        result = hashlib.md5(content.encode())
        return result.hexdigest()

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Chunk) and __value.id == self.id

    def to_str(self, max_content_len=100, max_source_len=50):
        file_name = os.path.basename(self.metadata['source'])

        rs = f"{self.page_content[:max_content_len]} - [{file_name[:max_source_len]}]"
        if self.score is not None:
            rs += f" [{self.score:2.3f}]"
        return rs


class KnowledgeBase(ConfigMixin):
    def __init__(self, name, splitter_config=dict(), index_config=dict()) -> None:

        self.embeddings = ZhipuAIEmbeddings(norm=2)
        self.text_splitter = SmartTextSplitter(**splitter_config)
        self.kb_path = os.path.join(AGIT_KB_DIR, name)
        self.doc_dir = os.path.join(self.kb_path, "documents")
        self.index_dir = os.path.join(self.kb_path, "index")
        self.chunks = set()
        self.index_config = index_config

        if os.path.exists(self.index_dir):
            logger.info(f"loading kb fromt {self.index_dir}")
            self.index = FAISS.load_local(folder_path=self.index_dir,
                                          embeddings=self.embeddings,  **self.index_config)

            # load from index
            self.chunks = set([Chunk(**e.dict())
                               for e in self.index.docstore._dict.values()])

        else:
            logger.info(f"{self.index_dir} not exists, will not load kb")
            self.index = None

    @log_cost_time(name="rebuild")
    def rebuild(self):
        logger.info(f"rebuild index for {self.kb_path}")
        self.chunks = set()
        self.index = None
        for file in os.listdir(self.doc_dir):
            self.update_document(doc_path=os.path.join(self.doc_dir, file))
        self.store()

    def load_and_cut(self, doc_path, max_page=None) -> List[Chunk]:
        loader = SmartDocumentLoader(doc_path, max_page=max_page)
        chunks = loader.load()
        chunks = self.text_splitter.split_documents(chunks)
        chunks = [Chunk(**e.dict()) for e in chunks]
        logger.info(f"split {len(chunks)} chunks from {doc_path}")
        return chunks

    def _deduplicate(self, chunks: List[Chunk]):
        logger.info("deduplicating chunks")
        rs_chunks = []

        for chunk in chunks:
            if chunk in self.chunks:
                continue
            rs_chunks.append(chunk)
        logger.info(f"get {len(rs_chunks)} uniq chunks from {len(chunks)} origin chunks")
        return rs_chunks

    # TODO 优雅的update的实现方式
    def update_document(self, doc_path: str, max_page=None):
        logger.info(f"updating file :{doc_path}")
        chunks = self.load_and_cut(doc_path, max_page=max_page)
        chunks = self._deduplicate(chunks)
        ids = [e.id for e in chunks]
        if not chunks:
            return
        if not self.index:
            logger.debug(f"create index")
            self.index = FAISS.from_documents(chunks, embedding=self.embeddings, ids=ids, **self.index_config)
        else:
            logger.debug(f"add {len(chunks)} chunks to {self.index}")
            self.index.add_documents(
                chunks, embedding=self.embeddings, ids=ids,  **self.index_config)
        self.chunks |= set(chunks)

        logger.info("add documents done")

    # 添加新的文档
    def add_document(self, doc_path: str, max_page=None):
        tgt_path = os.path.join(self.doc_dir, os.path.basename(doc_path))
        logger.info(f"copy document {doc_path} to {tgt_path}")
        shutil.copy(doc_path, tgt_path)
        self.update_document(tgt_path, max_page=max_page)

    def learn(self, knowledge: str):
        doc_path = os.path.join(
            self.doc_dir, "learn-" + time.strftime('%Y-%m-%d', time.localtime())+".txt")

        create_dir_path(doc_path)
        with open(doc_path, "a", encoding="utf-8") as f:
            f.write(knowledge)
            f.write("\n")

        logger.debug(f"learning knowledge in {doc_path}")
        self.update_document(doc_path)

    def store(self):
        assert self.index
        logger.info(f"store to {self.index_dir}")
        self.index.save_local(folder_path=self.index_dir)

    @property
    def chunk_num(self):
        return len(self.chunks)

    @log_cost_time(name="kb_search")
    @log_function_info()
    def search(self, query, top_k=4, threshold=None) -> List[Chunk]:
        if not self.index:
            logger.warning("kb is empty, return []")
            return []

        records = self.index.similarity_search_with_score(
            query, k=top_k, score_threshold=threshold)
        logger.info(f"{len(records)} records found")
        chunks = [(Chunk(**d.dict(), score=s)) for d, s in records]
        return chunks
