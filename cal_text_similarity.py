import click
from scipy import spatial
from tqdm import tqdm

from agit.agents.zhipuai import ZhipuAIAgent


def cal_similarity(text1, text2, agent, sim_type="cosine"):
    emb1 = agent.embedding(prompt=text1)
    emb2 = agent.embedding(prompt=text2)
    if sim_type == "cosine":
        cos_sim = 1 - spatial.distance.cosine(emb1, emb2)
        return cos_sim


def sort_similarity(text, cands, agent, sim_type="cosine"):
    resp = []
    for cand in tqdm(cands):
        smi = cal_similarity(text, cand, agent, sim_type)
        resp.append((cand, smi))
    resp.sort(key=lambda x: x[1], reverse=True)
    return resp


@click.command()
@click.option('--model', '-m', default="zhipu_api", help='模型名称')
@click.option('--sim_type', '-s',  default="cosine",  help='相似度计算方法')
@click.argument("text")
@click.argument("cands")
def main(text, cands, model, sim_type):
    pass


if __name__ == "__main__":
    agent = ZhipuAIAgent()
    resp = sort_similarity("中国的城市", ["北京", "上海", "杭州", "东京", "华盛顿"], agent)
    print(resp)
