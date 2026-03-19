import re
import ollama

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
#print(len(batch['embeddings'])) 
# print(f"Dane z pliku ({len(plik_end)} elementów):\n")
# for i, element in enumerate(plik_end, 1):
#     print(plik_end)
for sentenc, vector in zip(plik_end[:10], batch['embeddings'][:10]):
    print(F"Sentence: {sentenc}")
    print(f"Vector ({len(vector)} dim): {vector[:3]}...")