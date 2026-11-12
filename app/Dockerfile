# Energy Watch : image de l'application Streamlit.
# Le contexte de build est la RACINE du projet (l'appli lit dashboard/*.csv) :
#   docker build -f app/Dockerfile -t energy-watch .
# ou, depuis app/ :
#   docker compose up --build

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /project

# Dependances d'abord : cette couche reste en cache tant que requirements.txt ne change pas
COPY app/requirements.txt app/requirements.txt
RUN pip install -r app/requirements.txt

# Code de l'appli et donnees du tableau de bord (meme arborescence que le projet)
COPY app/ app/
COPY dashboard/building_energy_performance_dashboard.csv dashboard/

# Utilisateur sans privileges
RUN useradd --create-home --uid 1000 energy && chown -R energy:energy /project
USER energy

# Les hebergeurs (Render, Railway, Cloud Run, Fly...) imposent le port via $PORT.
# En local, PORT vaut 8501 (voir compose.yaml pour le port de l'ordinateur).
ENV PORT=8501
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/_stcore/health', timeout=4)"

# Forme shell pour que ${PORT} soit remplace ; exec garde streamlit en processus principal
CMD exec streamlit run app/streamlit_app.py \
    --server.address=0.0.0.0 --server.port=${PORT} --server.headless=true \
    --browser.gatherUsageStats=false --server.fileWatcherType=none
