import re

input1 = """
Nie mogę wykonać migracji plików za Ciebie, ponieważ wymaga to
Twoich uprawnień administratora. Mogę jednak przeprowadzić Cię przez
cały proces krok po kroku. Przeniesienie danych powinno zająć około
15 minut i nie wymaga przestoju serwisu.
""" 

input2 = """
"""
path = './Test/'
with open(path + "Expert-First-Contact-Customer-Assistant-Authorized_User.md", "r", encoding='utf-8') as file:
    lines = file.readline()


print(f"test: {lines}")


# Normalizacja
input1 = re.sub(r'[\n\t\r]+', ' ', input1)
input2 = re.sub(r'[\n\t\r]+', ' ', input2)
# Dzielenie
zdania = re.split(r'(?<=[.!?])\s+', input1)
zdania2 = re.split(r'(?<=[.!?])\s+', input2)

print(f"input 1: {zdania}")
print(f"Input 2: {zdania2}")
