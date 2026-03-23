# Prompt X-Ray

Narzędzie do wizualizacji semantycznych powiązań między dwoma dokumentami lub promptami. Fragmenty o podobnym znaczeniu otrzymują podobne kolory po obu stronach — pozwala to na intuicyjne porównanie treści bez konieczności ręcznego szukania zależności.

## Jak to działa

1. Oba dokumenty są dzielone na linie.
2. Wszystkie zdania trafiają do jednego batcha embeddings (model `bge-m3` via Ollama).
3. Wektory są redukowane do 3 wymiarów przez PCA i mapowane na kolory RGB.
4. Ponieważ oba dokumenty przetwarzane są we wspólnej skali, semantycznie podobne fragmenty lądują blisko siebie w przestrzeni i dostają zbliżone kolory.

## Wymagania

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) (menadżer pakietów)
- [Ollama](https://ollama.com) uruchomiony lokalnie z załadowanym modelem `bge-m3`

## Instalacja i uruchomienie

```bash
# Pobierz model embeddingowy (jednorazowo)
ollama pull bge-m3:latest

# Zainstaluj zależności
uv sync

# Uruchom serwer
uvicorn main:app --reload
```

Serwer startuje pod adresem `http://127.0.0.1:8000`.

Otwórz `index.html` w przeglądarce, wklej dwa dokumenty i kliknij **Porównaj**.

## API

`POST /compare`

```json
{
  "doc1": "Pierwszy dokument...",
  "doc2": "Drugi dokument..."
}
```

Odpowiedź:

```json
{
  "doc1": [{ "text": "zdanie", "color": "#a3c2f0" }, ...],
  "doc2": [{ "text": "inne zdanie", "color": "#a1bfee" }, ...]
}
```

## Stos technologiczny

| Warstwa     | Technologia                        |
|-------------|-------------------------------------|
| Backend     | FastAPI + Uvicorn                   |
| Embeddings  | Ollama (`bge-m3:latest`)            |
| Redukcja    | PCA (scikit-learn)                  |
| Frontend    | Vanilla JS / HTML / CSS             |
| Pakiety     | uv                                  |
