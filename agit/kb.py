#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/12 15:44:36
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

class KB:
    def __init__(self,doc_reader, text_cutter) -> None:
        self.doc_reader=doc_reader
        self.text_cutter=text_cutter
        
    
    def add_doc(self, doc_path: str):
        text = self.doc_reader.read_doc(doc_path)
        pieces = self.text_cutter.cut(text)
        
        
    


