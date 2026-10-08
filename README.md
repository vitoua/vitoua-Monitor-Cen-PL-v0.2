# Monitor Cen PL v0.2
Wersja Playwright + Chromium dla Render Docker.

1. Zastąp zawartość repozytorium plikami z pakietu.
2. Upewnij się, że są wgrane: Dockerfile, render.yaml, .dockerignore, app.py, requirements.txt, products.xlsx i parsers/.
3. W Render utwórz nowy Blueprint z repozytorium. `render.yaml` ustawi runtime Docker.
4. Po deployu wykonaj Ctrl+Shift+R.
5. Pierwszy test wykonaj dla 2 produktów i 2 źródeł.
