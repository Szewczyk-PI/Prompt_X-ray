import re
import ollama
from sklearn.decomposition import PCA
import numpy as np 

path = './Test/'

with open(path + "Expert-First-Contact-Customer-Assistant-Authorized_User.md", "r", encoding='utf-8') as file:
    plik = file.read()

# Dzielenie na każdym znaku nowej linii — każda linia jako osobny element
elementy = re.split(r'\n', plik)

# Normalizacja każdego elementu osobno
plik_end = [re.sub(r'[\n\t\r]+', ' ', e).strip() for e in elementy if e.strip()]

batch = ollama.embed(
    model="bge-m3:latest",
    input=plik_end
)

embeddings = np.array(batch['embeddings'])
pca = PCA(n_components=3)
reduced = pca.fit_transform(embeddings)

# Normalizacja każdej osi do 0-255
def normalize(arr):
    return (arr - arr.min()) / (arr.max() - arr.min()) * 255

rgb = normalize(reduced).astype(int)
for (r, g, b), zdanie in zip(rgb, plik_end):
    print(f"\033[38;2;{r};{g};{b}m{zdanie}\033[0m")


