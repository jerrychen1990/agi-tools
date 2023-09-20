import agit.backend.openai_bk as openai_bk
import agit.backend.zhipuai_bk as zhipuai_bk


def call_llm_api(prompt: str, model: str, **kwargs):
    if "chatglm" in model:
        return zhipuai_bk.call_llm_api(prompt=prompt, model=model, **kwargs)
    else:
        return openai_bk.call_llm_api(prompt=prompt, model=model, **kwargs)
