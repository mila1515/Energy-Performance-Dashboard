# Energy Watch

Application Streamlit de **suivi continu** de la performance energetique des batiments de Seattle. Elle prolonge le tableau de bord Tableau Public : au lieu d'une photo d'une annee, elle detecte les batiments qui derivent et aide a prioriser les actions.

Prototype (v1) : il lit le fichier `dashboard/building_energy_performance_dashboard.csv` produit par les notebooks, sans modifier le reste du projet.

## Pages

| Page | Contenu |
|---|---|
| Vue d'ensemble | KPI de l'annee choisie, variations **a perimetre constant** (batiments declares les deux annees), tendances, top 10 des priorites |
| Alertes | Batiments qui derivent, avec seuils reglables, filtres par type et quartier, export CSV, ouverture de la fiche du batiment |
| Fiche batiment | Historique d'un batiment compare a la mediane des batiments du meme type, rang de priorite, alertes |
| Qualite des donnees | Completude (ENERGY STAR, gaz) et continuite des declarations par annee |

L'annee analysee se choisit dans la barre laterale et s'applique a toutes les pages.

## Regles d'alerte

| Alerte | Regle par defaut | Severite |
|---|---|---|
| Derive de l'intensite | Site EUI en hausse d'au moins 25 % par rapport a l'annee precedente (base >= 5 kBtu/sf) | Haute au-dela de 50 %, sinon moyenne |
| ENERGY STAR sous 50 | Score >= 50 l'annee precedente, < 50 cette annee | Moyenne |
| Devenu non conforme | Conforme l'annee precedente, non conforme cette annee | Moyenne |
| Declaration manquante | Declare l'annee precedente, absent cette annee | Basse |
| Tres au-dessus des pairs | Site EUI >= 3 x la mediane des batiments du meme type | Basse |

Les seuils sont dans `energy_watch/monitoring.py` (`AlertSettings`). Les deux premiers sont reglables dans la page Alertes.

## Lancer l'application

### Avec Docker (recommande)

Depuis le dossier `app/` :

```bash
docker compose up --build -d     # construit l'image et lance le conteneur
```

Puis ouvrir http://localhost:8530. Pour arreter : `docker compose down`.

Le port 8530 evite les conflits avec d'autres applis Streamlit (8501 par defaut). Pour en choisir un autre : `ENERGY_WATCH_PORT=8600 docker compose up -d`, ou une ligne `ENERGY_WATCH_PORT=8600` dans un fichier `app/.env`.

Sans Compose, depuis la racine du projet :

```bash
docker build -f app/Dockerfile -t energy-watch .
docker run -d -p 8530:8501 --name energy-watch energy-watch
```

L'image (`python:3.13-slim`) contient uniquement l'appli et le CSV du tableau de bord. Elle tourne avec un utilisateur sans privileges et expose un controle de sante (`/_stcore/health`). Apres une mise a jour du CSV par les notebooks, il suffit de reconstruire l'image.

### En local, avec Python

Depuis la racine du projet :

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows (macOS/Linux : source .venv/bin/activate)
pip install -r app/requirements.txt
streamlit run app/streamlit_app.py
```

## Organisation

```text
app/
|-- streamlit_app.py        # Point d'entree : navigation et choix de l'annee
|-- app_pages/              # Une page par fichier
|-- energy_watch/
|   |-- data.py             # Chargement du CSV (mis en cache) et formats
|   |-- monitoring.py       # KPI, perimetre constant, pairs, alertes (pandas pur, testable)
|-- .streamlit/config.toml  # Theme clair/sombre
|-- requirements.txt        # Versions figees (image reproductible)
|-- Dockerfile              # Image de l'appli (contexte de build : racine du projet)
|-- Dockerfile.dockerignore # N'envoie au build que app/ et le CSV
|-- compose.yaml            # docker compose up --build
```

## Limites et suite

- Les donnees de Seattle sont **annuelles** : le suivi se met a jour une fois par an. Un vrai suivi continu demande des releves mensuels ou des compteurs (etape suivante).
- Pistes : recuperation automatique des nouvelles donnees, releves mensuels et reference corrigee de la meteo, notifications, suivi des actions et mesure des gains.
