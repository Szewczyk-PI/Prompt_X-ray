import json
import re
import webbrowser
import tempfile
from pathlib import Path

import yaml
import numpy as np
import requests
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity


# ─── KONFIGURACJA ──────────────────────────────────────────────────────────────

OLLAMA_URL   = "http://localhost:11434/api/embed"
MODEL_NAME   = "bge-m3:latest"       # sprawdź przez: ollama list
SIMILARITY_THRESHOLD = 0.55   # próg dopasowania; podkręć jeśli za dużo/mało matchuje
MAX_CONFIG_SENTENCES = 200    # zabezpieczenie przed gigantycznymi konfig.


# ─── 1. ŁADOWANIE DANYCH ───────────────────────────────────────────────────────

def load_config(path: str) -> list[tuple[str, str]]:
    """
    Wczytuje konfigurację z JSON lub YAML.
    Zwraca listę (tekst_sentencji, źródło).
    """
    p = Path(path)
    raw = p.read_text(encoding="utf-8")

    if p.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(raw)
    else:
        data = json.loads(raw)

    sentences = []
    _extract_text_from_dict(data, sentences, source_prefix="config")
    return sentences[:MAX_CONFIG_SENTENCES]


def _extract_text_from_dict(obj, result: list, source_prefix: str, depth: int = 0):
    """Rekurencyjnie wyciąga ciągi tekstowe ze słownika/listy."""
    if isinstance(obj, str) and len(obj.strip()) > 20:
        for s in split_sentences(obj):
            result.append((s, source_prefix))
    elif isinstance(obj, dict):
        for key, val in obj.items():
            _extract_text_from_dict(val, result, f"{source_prefix}.{key}", depth + 1)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _extract_text_from_dict(item, result, f"{source_prefix}[{i}]", depth + 1)


def load_output(text: str) -> list[tuple[str, str]]:
    """Dzieli output agenta na zdania. Zwraca listę (tekst, 'output')."""
    return [(s, "output") for s in split_sentences(text)]


def split_sentences(text: str) -> list[str]:
    """Prosty splitter na zdania."""
    text = text.strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 15]


# ─── 2. EMBEDDINGI (OLLAMA) ────────────────────────────────────────────────────

def embed(sentences: list[str]) -> np.ndarray:
    """Wysyła zdania do lokalnej Ollamy, zwraca macierz embeddingów."""
    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "input": sentences
    })
    response.raise_for_status()
    vectors = response.json()["embeddings"]
    return np.array(vectors, dtype=np.float32)


# ─── 3. PRZYPISANIE KOLORÓW ────────────────────────────────────────────────────

def assign_colors_to_config(embeddings: np.ndarray) -> list[str]:
    """
    Redukuje embeddingi do 2D przez PCA, mapuje na koło HSL.
    Każda sentencja konfigu dostaje unikalny kolor.
    """
    if len(embeddings) == 1:
        return ["hsl(200, 80%, 60%)"]

    n_components = min(2, len(embeddings) - 1)
    pca = PCA(n_components=n_components)
    coords = pca.fit_transform(embeddings)  # (N, 2)

    if coords.shape[1] == 1:
        coords = np.hstack([coords, np.zeros((len(coords), 1))])

    # Normalizacja do [-1, 1]
    for i in range(2):
        rng = coords[:, i].max() - coords[:, i].min()
        if rng > 0:
            coords[:, i] = (coords[:, i] - coords[:, i].min()) / rng * 2 - 1

    colors = []
    for x, y in coords:
        hue = int((np.degrees(np.arctan2(y, x)) + 180) % 360)
        r = min(1.0, np.sqrt(x**2 + y**2))
        saturation = int(50 + r * 40)       # 50–90%
        lightness  = int(55 + (1 - r) * 15) # 55–70% – czytelne na białym tle
        colors.append(f"hsl({hue}, {saturation}%, {lightness}%)")

    return colors


def match_output_to_config(
    config_embeddings: np.ndarray,
    output_embeddings: np.ndarray,
    threshold: float = SIMILARITY_THRESHOLD,
) -> list[int | None]:
    """
    Dla każdego zdania outputu zwraca indeks najlepiej pasującego zdania konfigu
    lub None jeśli podobieństwo poniżej progu.
    """
    sim_matrix = cosine_similarity(output_embeddings, config_embeddings)  # (O, C)
    matches = []
    for row in sim_matrix:
        best_idx = int(np.argmax(row))
        matches.append(best_idx if row[best_idx] >= threshold else None)
    return matches


# ─── 4. HTML ───────────────────────────────────────────────────────────────────

def generate_html(
    config_items: list[tuple[str, str]],
    output_items: list[tuple[str, str]],
    config_colors: list[str],
    output_matches: list[int | None],
) -> str:

    def make_span(text: str, color: str, source: str = "") -> str:
        tooltip = f'title="{source}"' if source else ""
        style = f"background-color:{color}; border-radius:3px; padding:1px 3px;"
        return f'<span style="{style}" {tooltip}>{text}</span> '

    config_html_parts = []
    for i, (text, source) in enumerate(config_items):
        color = config_colors[i]
        config_html_parts.append(make_span(text, color, source))

    output_html_parts = []
    for i, (text, _) in enumerate(output_items):
        match_idx = output_matches[i]
        if match_idx is not None:
            color  = config_colors[match_idx]
            source = config_items[match_idx][1]
            output_html_parts.append(make_span(text, color, f"← {source}"))
        else:
            output_html_parts.append(f'<span style="opacity:0.6">{text}</span> ')

    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="UTF-8">
<title>Prompt X-Ray</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 0; background: #f8f8f8; color: #111; }}
  h1   {{ font-size: 1.2rem; padding: 16px 24px; background: #111; color: #fff; margin: 0; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; height: calc(100vh - 50px); }}
  .panel {{ padding: 24px; overflow-y: auto; line-height: 2.1; font-size: 0.95rem; }}
  .panel:first-child {{ border-right: 2px solid #ddd; background: #fff; }}
  .panel:last-child  {{ background: #fafafa; }}
  h2 {{ margin: 0 0 16px; font-size: 0.85rem; text-transform: uppercase;
        letter-spacing: .08em; color: #666; }}
</style>
</head>
<body>
<h1>🔍 Prompt X-Ray</h1>
<div class="grid">
  <div class="panel">
    <h2>Konfiguracja agenta</h2>
    {''.join(config_html_parts)}
  </div>
  <div class="panel">
    <h2>Output agenta</h2>
    {''.join(output_html_parts)}
  </div>
</div>
</body>
</html>"""


# ─── 5. ENTRY POINT ────────────────────────────────────────────────────────────

def run(config_path: str, output_text: str):
    print("📄 Parsowanie konfiguracji...")
    config_items = load_config(config_path)
    print(f"   → {len(config_items)} sentencji z konfigu")

    print("📄 Parsowanie outputu...")
    output_items = load_output(output_text)
    print(f"   → {len(output_items)} sentencji z outputu")

    all_texts = [t for t, _ in config_items + output_items]

    print(f"🧮 Generowanie embeddingów przez Ollama ({MODEL_NAME})...")
    all_embeddings = embed(all_texts)

    c = len(config_items)
    config_embeddings = all_embeddings[:c]
    output_embeddings = all_embeddings[c:]

    print("🎨 Przypisywanie kolorów...")
    config_colors  = assign_colors_to_config(config_embeddings)
    output_matches = match_output_to_config(config_embeddings, output_embeddings)

    matched = sum(1 for m in output_matches if m is not None)
    print(f"   → {matched}/{len(output_items)} zdań outputu dopasowanych do konfigu")

    print("🖥️  Generowanie HTML...")
    html = generate_html(config_items, output_items, config_colors, output_matches)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as f:
        f.write(html)
        tmp_path = f.name

    print(f"✅ Otwieram przeglądarkę: {tmp_path}")
    webbrowser.open(f"file://{tmp_path}")


# ─── PRZYKŁAD UŻYCIA ───────────────────────────────────────────────────────────

if __name__ == "__main__":

    # ← PODAJ SWOJE DANE
    CONFIG_FILE = "agent_config.yaml"   # ścieżka do twojego pliku
    AGENT_OUTPUT = """
    Nie mogę wykonać migracji plików za Ciebie, ponieważ wymaga to
    Twoich uprawnień administratora. Mogę jednak przeprowadzić Cię przez
    cały proces krok po kroku. Przeniesienie danych powinno zająć około
    15 minut i nie wymaga przestoju serwisu.
    """

    run(CONFIG_FILE, AGENT_OUTPUT)