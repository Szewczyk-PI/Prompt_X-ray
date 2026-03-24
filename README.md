# Prompt X-Ray

Narzędzie do wizualizacji semantycznych powiązań między dwoma dokumentami lub promptami. Fragmenty o podobnym znaczeniu otrzymują podobne kolory po obu stronach — pozwala to na intuicyjne porównanie treści bez konieczności ręcznego szukania zależności.

## Jak to działa

1. Oba dokumenty są dzielone na linie.
2. Wszystkie zdania trafiają do jednego batcha embeddings (model `bge-m3` via Ollama).
3. Wektory są redukowane do 3 wymiarów przez PCA i mapowane na kolory RGB.
4. Ponieważ oba dokumenty przetwarzane są we wspólnej skali, semantycznie podobne fragmenty lądują blisko siebie w przestrzeni i dostają zbliżone kolory.

## Uruchomienie lokalne

### Wymagania

- Python 3.14+
- [uv](https://github.com/astral-sh/uv)
- [Ollama](https://ollama.com) uruchomiony lokalnie

```bash
# Pobierz model embeddingowy (jednorazowo)
ollama pull bge-m3:latest

# Zainstaluj zależności
uv sync

# Uruchom serwer
uvicorn main:app --reload
```

Serwer startuje pod adresem `http://127.0.0.1:8000`.

## Uruchomienie przez Docker

### Wymagania

- Docker

```bash
# Wystartuj kontenery
docker compose up -d --build

# Pobierz model (jednorazowo, ~1.5 GB)
docker compose exec ollama ollama pull bge-m3:latest
```

Otwórz `http://localhost:8000` w przeglądarce.

## Deploy na VPS

### Wymagania na serwerze

- Docker
- Nginx (host)
- Certbot
- Otwarte porty: 80, 443

```bash
# 1. Sklonuj repo
git clone -b docker https://github.com/Szewczyk-PI/Prompt_X-ray.git ~/prompt-xray
cd ~/prompt-xray

# 2. Pobierz certyfikat SSL
certbot certonly --standalone -d twoja-domena.pl \
  --pre-hook "systemctl stop nginx" \
  --post-hook "systemctl start nginx"

# 3. Dodaj config nginx (patrz niżej)

# 4. Wystartuj kontenery
docker compose up -d --build

# 5. Pobierz model
docker compose exec ollama ollama pull bge-m3:latest
```

### Config nginx (`/etc/nginx/sites-available/twoja-domena.pl`)

```nginx
server {
    listen 80;
    server_name twoja-domena.pl;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name twoja-domena.pl;

    ssl_certificate /etc/letsencrypt/live/twoja-domena.pl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/twoja-domena.pl/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/twoja-domena.pl /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

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
| Container   | Docker + Docker Compose             |
| Reverse proxy | Nginx                             |
