# Methodologie

Ce document resume la demarche analytique utilisee pour transformer le jeu de donnees brut sur la performance energetique des batiments de Seattle en fichier exploitable pour un tableau de bord et en analyse metier.

## 1. Collecte des donnees

Le projet utilise le jeu de donnees public `Building Energy Benchmarking Data, 2015-Present`.

Emplacement des donnees brutes :

`data/raw/Building_Energy_Benchmarking_Data,_2015-Present_20260704.csv`

## 2. Nettoyage des donnees

Le nettoyage vise a preparer des variables fiables pour l'analyse :

- standardisation des noms de colonnes ;
- selection des variables utiles pour l'analyse metier ;
- conservation des libelles d'origine pour les types de batiment (`Multifamily LR (1-4)`, `SPS-District K-12`...) ;
- suppression des lignes incompletes ou incoherentes (surface, consommation ou nombre d'etages nuls, annee de construction posterieure a l'annee de declaration) ;
- suppression des valeurs aberrantes : `site_eui` hors de l'intervalle [1 ; 1000] kBtu/sf (29 lignes, erreurs de declaration probables) ;
- scores ENERGY STAR manquants laisses vides (pas d'imputation par la mediane, qui aurait gonfle la categorie `Bon`) ;
- gaz naturel manquant remplace par 0 (batiment sans gaz) ;
- preparation d'un fichier nettoye pour l'analyse.

Chaque ligne correspond a un batiment pour une annee de declaration (3 806 batiments distincts, 33 239 declarations). Les comptes de batiments utilisent donc un compte distinct de `building_id`.

Emplacement des donnees nettoyees :

`data/cleaned/buildings_clean.csv`

## 3. Creation d'indicateurs

Des indicateurs complementaires ont ete crees pour faciliter l'analyse dans le tableau de bord :

- `building_age`;
- `energy_use_per_floor`;
- `energy_per_sqft`;
- `energy_star_category`;
- `priority_score`.

Ces indicateurs sont calcules dans `src/indicators.py`, utilise a la fois par l'analyse (notebook 03) et l'export Tableau (notebook 04).

Le `priority_score` combine l'intensite energetique (40 %), les emissions de CO2 (40 %) et un score ENERGY STAR faible (20 %). Les rangs sont calcules a l'interieur de chaque annee, ce qui permet de classer les batiments d'une meme annee sans doublons. Un score proche de 1 indique qu'un batiment doit etre analyse en priorite.

## 4. Analyse exploratoire

L'analyse compare la performance energetique selon :

- les annees de declaration ;
- les types de batiments ;
- les quartiers ;
- les categories ENERGY STAR ;
- les statuts de conformite.

## 5. Conception du tableau de bord

Le tableau de bord final est construit a partir du fichier :

`dashboard/building_energy_performance_dashboard.csv`

Il permet de suivre les indicateurs cles, l'evolution de la consommation d'energie, les comparaisons par type de batiment, les emissions de CO2 par quartier et les batiments prioritaires.

## 6. Analyse metier

Les resultats du tableau de bord sont synthetises dans :

`docs/Rapport_Analyse_Metier.pdf`

Le rapport transforme les constats du tableau de bord en recommandations metier pour les audits energetiques, les actions de reduction carbone et le suivi annuel des indicateurs cles.
