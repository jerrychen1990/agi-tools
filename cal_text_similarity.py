import click
from scipy import spatial
from tqdm import tqdm

from agit.backend.zhipuai_bk import call_embedding_api


def _get_emb_func(model_type):
    if model_type == "zhipu_api":
        return call_embedding_api
    raise ValueError("model_type must be zhipu_api")


def cal_similarity(text1, text2, model_type="zhipu_api", sim_type="cosine"):
    emb_func = _get_emb_func(model_type)
    emb1 = emb_func(text1)
    emb2 = emb_func(text2)
    if sim_type == "cosine":
        cos_sim = 1 - spatial.distance.cosine(emb1, emb2)
        return cos_sim


def sort_similarity(text, cands, model_type="zhipu_api", sim_type="cosine"):
    resp = []
    for cand in tqdm(cands):
        smi = cal_similarity(text, cand, model_type, sim_type)
        resp.append((cand, smi))
    resp.sort(key=lambda x: x[1], reverse=True)
    return resp


@click.command()
@click.option('--model_type', '-m', default="zhipu_api", help='模型名称')
@click.option('--sim_type', '-s',  default="cosine",  help='相似度计算方法')
@click.argument("text")
@click.argument("cands", nargs=-1)
def main(text, cands, model_type, sim_type):
    print(cands)
    resp = sort_similarity(text, cands, model_type, sim_type)
    for k, v in resp:
        print(f"{k}:sim:{v:2.3f}")


if __name__ == "__main__":
    main()
    # python cal_text_similarity.py 中国的城市 北京 上海
