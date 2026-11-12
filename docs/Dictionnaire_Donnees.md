# Dictionnaire des donnees

Description des principales colonnes utilisees dans le projet.

Les colonnes jusqu'a `natural_gas_was_missing` viennent du fichier nettoye. Les colonnes `building_age`, `energy_use_per_floor`, `energy_per_sqft`, `energy_star_category` et `priority_score` sont des colonnes calculees pour faciliter l'analyse et le tableau de bord.

| Colonne | Description |
| --- | --- |
| building_id | Identifiant du batiment |
| data_year | Annee de declaration |
| building_name | Nom du batiment |
| building_type | Type de batiment |
| neighborhood | Quartier |
| year_built | Annee de construction |
| number_of_floors | Nombre d'etages |
| property_gfa_total | Surface totale du batiment |
| energy_star_score | Score ENERGY STAR (1 a 100). Vide si non renseigne dans la source (environ 24 % des lignes) |
| site_eui | Intensite energetique du site (kBtu/sf), calculee par la source sur la surface des batiments hors parking |
| site_energy_use | Consommation totale d'energie |
| electricity_kwh | Consommation d'electricite en kWh |
| natural_gas_therms | Consommation de gaz naturel |
| total_ghg_emissions | Emissions totales de CO2 |
| ghg_emissions_intensity | Intensite des emissions de CO2 |
| compliance_status | Statut de conformite |
| energy_star_score_was_missing | Indique si le score ENERGY STAR etait manquant avant nettoyage |
| natural_gas_was_missing | Indique si la consommation de gaz naturel etait manquante avant nettoyage |
| building_age | Colonne calculee : age du batiment (`data_year - year_built`) |
| energy_use_per_floor | Colonne calculee : consommation moyenne par etage (`site_energy_use / number_of_floors`) |
| energy_per_sqft | Colonne calculee : consommation par unite de surface totale, parking inclus (`site_energy_use / property_gfa_total`). Peut differer de `site_eui`, qui exclut le parking : preferer `site_eui` pour comparer l'efficacite |
| energy_star_category | Colonne calculee : categorie simple du score ENERGY STAR : A verifier (0-50), Moyen (51-75), Bon (76-100) ou Non renseigne |
| priority_score | Colonne calculee : score de priorite entre 0 et 1, calcule a l'interieur de chaque annee : 40 % rang du `site_eui`, 40 % rang des emissions totales, 20 % rang d'un score ENERGY STAR faible (0,5 si non renseigne). Voir `src/indicators.py` |

Note : chaque ligne correspond a un batiment pour une annee. Pour compter des batiments, utiliser un compte distinct de `building_id` (`COUNTD` dans Tableau).
