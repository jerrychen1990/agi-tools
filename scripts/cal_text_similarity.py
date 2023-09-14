import click
from scipy import spatial
from tqdm import tqdm

from agit.backend.zhipuai_bk import call_embedding_api
from agit.utils import cal_vec_similarity


def _get_emb_func(model_type):
    if model_type == "zhipu_api":
        return call_embedding_api
    raise ValueError("model_type must be zhipu_api")


def cal_similarity(text1, text2, model_type="zhipu_api", normalize=True, metric="cosine"):
    emb_func = _get_emb_func(model_type)
    emb1 = emb_func(text1)
    emb2 = emb_func(text2)
    return cal_vec_similarity(emb1, emb2, normalize=normalize, metric=metric)


def sort_similarity(text, cands, model_type="zhipu_api", normalize=True, metric="cosine"):
    resp = []
    for cand in tqdm(cands):
        smi = cal_similarity(text, cand, model_type,
                             normalize=normalize, metric=metric)
        resp.append((cand, smi))
    reverse = True
    if metric in ["l2_distance"]:
        reverse = False
    resp.sort(key=lambda x: x[1], reverse=reverse)
    return resp


@click.command()
@click.option('--model_type', '-m', default="zhipu_api", help='模型名称')
@click.option('--metric', '-s',  default="cosine",  help='相似度计算方法')
@click.argument("text")
@click.argument("cands", nargs=-1)
def main(text, cands, model_type, metric):
    print(cands)
    resp = sort_similarity(text, cands, model_type=model_type, metric=metric)
    for k, v in resp:
        print(f"{k}:sim:{v:2.3f}")


if __name__ == "__main__":
    main()
    # python cal_text_similarity.py 中国的城市 北京 上海
