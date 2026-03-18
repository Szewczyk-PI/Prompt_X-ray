import re

input1 = """
Nie mogę wykonać migracji plików za Ciebie, ponieważ wymaga to
Twoich uprawnień administratora. Mogę jednak przeprowadzić Cię przez
cały proces krok po kroku. Przeniesienie danych powinno zająć około
15 minut i nie wymaga przestoju serwisu.
""" 

input2 = """
agent:
# agent_config.yaml
agent:
  name: SupportAgent
  rules:
    - Nie informuj klienta że możesz wykonać migrację za niego.
    - Nie przenoś plików klienta bez jego zgody.
    - Zawsze informuj o szacowanym czasie operacji.

tasks:
  - name: migration_support
    description: Pomagaj klientowi w procesie migracji krok po kroku.
    constraints:
      - Nie wykonuj migracji samodzielnie.
      - Poinformuj że migracja nie wymaga przestoju serwisu.
"""


# Normalizacja
input1 = re.sub(r'[\n\t\r]+', ' ', input1)
input2 = re.sub(r'[\n\t\r]+', ' ', input2)
# Dzielenie
zdania = re.split(r'(?<=[.!?])\s+', input1)
zdania2 = re.split(r'(?<=[.!?])\s+', input2)

print(f"input 1: {zdania}")
print(f"Input 2: {zdania2}")
