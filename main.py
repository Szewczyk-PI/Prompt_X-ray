"""
Prompt X-Ray
============
Wizualizuje semantyczne powiązania między konfiguracją agenta a jego outputem.
Podobne znaczeniowo fragmenty dostają podobny kolor po obu stronach.
"""

import requests
import numpy as np

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL_NAME = "bge-m3:latest"


def get_embeddings(texts: list[str]) -> np.ndarray:
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "input": texts
    })
    response.raise_for_status()
    return np.array(response.json()["embeddings"])


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a_norm = a / np.linalg.norm(a, axis=1, keepdims=True)
    b_norm = b / np.linalg.norm(b, axis=1, keepdims=True)
    return a_norm @ b_norm.T


sentences = [
    'The weather is lovely today.',
    "It's so sunny outside!",
    'He drove to the stadium.',
]

embeddings = get_embeddings(sentences)
print(embeddings.shape)

similarities = cosine_similarity(embeddings, embeddings)
print(similarities.shape)
print(similarities)