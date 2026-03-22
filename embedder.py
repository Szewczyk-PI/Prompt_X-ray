import re
import ollama
import numpy as np
from sklearn.decomposition import PCA

def split_sentences(text: str) -> list[str]:
    lines = re.split(r'\n', text)
    return [re.sub(r'[\n\t\r]+', ' ', l).strip() for l in lines if l.strip()]

def get_colors(sentences: list[str]) -> list[str]:
    batch = ollama.embed(model="bge-m3:latest", input=sentences)
    embeddings = np.array(batch['embeddings'])

    n_components = min(3, len(sentences))
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(embeddings)

    def normalize(arr):
        return (arr - arr.min()) / (arr.max() - arr.min()) * 255

    rgb = normalize(reduced).astype(int)

    if n_components == 3:
        return [f"#{r:02x}{g:02x}{b:02x}" for r, g, b in rgb]
    elif n_components == 2:
        return [f"#{r:02x}{g:02x}00" for r, g in rgb]
    else:
        return [f"#{r:02x}0000" for r in rgb]


def compare(doc1: str, doc2: str) -> dict:
    s1 = split_sentences(doc1)
    s2 = split_sentences(doc2)

    colors = get_colors(s1 + s2)  # jeden batch, wspólna skala

    c1 = colors[:len(s1)]
    c2 = colors[len(s1):]

    return {
        "doc1": [{"text": t, "color": c} for t, c in zip(s1, c1)],
        "doc2": [{"text": t, "color": c} for t, c in zip(s2, c2)],
    }
