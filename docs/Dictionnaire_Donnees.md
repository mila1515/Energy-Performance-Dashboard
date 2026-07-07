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
| energy_star_score | Score ENERGY STAR |
| site_eui | Intensite energetique du site |
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
| energy_per_sqft | Colonne calculee : consommation par unite de surface (`site_energy_use / property_gfa_total`) |
| energy_star_category | Colonne calculee : categorie simple du score ENERGY STAR, avec les valeurs A verifier, Moyen ou Bon |
| priority_score | Colonne calculee : score de priorite entre 0 et 1 base sur la consommation, les emissions et le score ENERGY STAR |
