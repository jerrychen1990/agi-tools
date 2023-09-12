#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/09/12 14:54:19
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


import re
from snippets import batchify, flat


class DocumentReader:
    def __init__(self) -> None:
        self.read_func = {
            "html": self.read_html,
            "htm": self.read_html,
        }

        pass

    def read(self, path: str) -> str:
        surfix = path.split(".")[-1]
        if surfix not in self.read_func:
            raise ValueError(f"unsupported file suffix: {surfix}")
        func = self.read_func[surfix]
        return func(path)

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


class TextCutter:
    def __init__(self) -> None:
        pass

    def cut(self, text: str, spliter="[,，。?\？！!\n]|\.{3+}"):
        pieces = re.split(spliter, text)
        pieces = [e.strip() for e in pieces if e.strip()]
        merged = self.merge(pieces)
        return merged
    
    
    def _cut2maxlen(self, text, max_len):
        if len(text) < max_len:
            return [text]
        
        
        return ["".join(e) for e in batchify(text, max_len)]

    def merge(self, pieces: list[str], joiner=",", min_len=10, max_len=100,overlap=0.3):
        pieces = flat([self._cut2maxlen(e, max_len)for e in pieces ])
        result = []
        
        idx = 0
        acc = []
        sum_len = 0
        while idx< len(pieces):
            p = pieces[idx]
            if not acc:
                acc.append(p)
                sum_len += len(p)
                idx+=1
            else:
                if sum_len + len(p) > max_len:
                    result.append(joiner.join(acc))
                    acc.clear()
                    sum_len = 0
                else:
                    acc.append(p)
                    sum_len += len(p)
                    idx += 1
        if acc:
            result.append(joiner.join(acc))
        return result
        
                    
                
                
                    
                
                
            
            
            
            
        
        
        
        
        
        
        
        
    
    
    


