# Tableau de bord de performance energetique

Projet portfolio d'analyse de donnees sur la performance energetique des batiments.

L'objectif est de nettoyer des donnees publiques, construire des indicateurs simples et preparer un fichier exploitable dans Power BI ou Tableau.

## Presentation du projet

Ce projet transforme des donnees publiques de performance energetique en tableau de bord interactif. Il permet de suivre la consommation d'energie, les emissions de CO2, les differences entre types de batiments et les batiments a analyser en priorite.

## Objectif metier

Une equipe de gestion energetique souhaite suivre la consommation de ses batiments afin de :

- identifier les batiments les plus energivores ;
- suivre les emissions de CO2 ;
- comparer la performance par type de batiment et par quartier ;
- reperer les donnees manquantes ou incoherentes ;
- preparer un tableau de bord clair pour l'aide a la decision.

## Donnees utilisees

Source : jeu de donnees `Building Energy Benchmarking Data, 2015-Present`.

Fichier brut :

`data/raw/Building_Energy_Benchmarking_Data,_2015-Present_20260704.csv`

## Indicateurs suivis

- consommation totale d'energie ;
- intensite energetique par surface ;
- emissions totales de CO2 ;
- intensite carbone ;
- score ENERGY STAR moyen ;
- score de priorite des batiments ;
- nombre de batiments par type, quartier et statut de conformite.

## Apercu du tableau de bord

![Apercu du tableau de bord](images/dashboard_overview.png)

## Tableau de bord interactif

Le tableau de bord est disponible sur Tableau Public :

[Ouvrir le tableau de bord interactif](https://public.tableau.com/views/Seattle_Building_Energy_Performance_Dashboard/BuildingEnergyPerformanceDashboard?:language=fr-FR&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link)

## Analyse metier

Les batiments non residentiels representent la plus grande part de la consommation totale, avec environ 105B kBtu sur la periode analysee. Ils constituent donc la cible prioritaire pour les actions d'efficacite energetique.

Les emissions de CO2 sont principalement concentrees dans Downtown, puis East et Greater Duwamish. Ces quartiers doivent etre analyses en priorite pour les programmes de reduction carbone.

Le `priority_score` permet d'identifier les batiments combinant forte consommation, fortes emissions et faible performance ENERGY STAR. Les premiers batiments classes doivent etre consideres comme des candidats prioritaires pour des audits energetiques et des projets de renovation energetique.

Le rapport complet est disponible ici : [`docs/Rapport_Analyse_Metier.pdf`](docs/Rapport_Analyse_Metier.pdf).

## Structure du projet

```text
energy-performance-dashboard/
|-- data/
|   |-- raw/        # Donnees brutes
|   |-- cleaned/    # Donnees nettoyees et exports
|-- notebooks/
|   |-- 01_data_exploration.ipynb
|   |-- 02_data_cleaning.ipynb
|   |-- 03_data_analysis.ipynb
|   |-- 04_export_powerbi.ipynb
|-- sql/
|   |-- create_tables.sql
|   |-- analysis_queries.sql
|-- dashboard/      # Fichier CSV pret pour le tableau de bord
|-- docs/
|   |-- Dictionnaire_Donnees.md
|   |-- Methodologie.md
|   |-- Rapport_Analyse_Metier.pdf
|-- images/
|   |-- dashboard_overview.png
|-- README.md
|-- requirements.txt
```

## Outils utilises

- Python ;
- pandas ;
- Jupyter Notebook ;
- SQL ;
- Tableau Public ;
- GitHub.

## Comment utiliser le projet

1. Installer les dependances :

```bash
pip install -r requirements.txt
```

2. Executer les notebooks dans l'ordre :

```text
01_data_exploration.ipynb
02_data_cleaning.ipynb
03_data_analysis.ipynb
04_export_powerbi.ipynb
```

3. Utiliser le fichier final dans Power BI ou Tableau :

```text
dashboard/building_energy_performance_dashboard.csv
```
