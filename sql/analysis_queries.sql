-- Requetes d'analyse simples pour le dashboard energetique.
--
-- Rappel : chaque ligne de buildings_energy correspond a un batiment POUR UNE
-- ANNEE de declaration. On compte donc les batiments avec
-- COUNT(DISTINCT building_id), et les comparaisons portent sur l'annee la plus
-- recente pour ne pas additionner plusieurs annees d'un meme batiment.
-- energy_star_score peut etre NULL (non renseigne) : AVG() ignore ces lignes.
-- La mediane n'etant pas standard en SQL, on utilise ici la moyenne du Site EUI
-- (le notebook 03 utilise la mediane, plus robuste).

-- 1. Vue globale des principaux KPI (annee la plus recente)
SELECT
    data_year,
    COUNT(DISTINCT building_id) AS number_of_buildings,
    ROUND(SUM(site_energy_use), 2) AS total_energy_use,
    ROUND(AVG(site_eui), 2) AS average_site_eui,
    ROUND(SUM(total_ghg_emissions), 2) AS total_ghg_emissions,
    ROUND(AVG(energy_star_score), 2) AS average_energy_star_score
FROM buildings_energy
WHERE data_year = (SELECT MAX(data_year) FROM buildings_energy)
GROUP BY data_year;

-- 1b. Taille du jeu de donnees
SELECT
    COUNT(DISTINCT building_id) AS number_of_buildings,
    COUNT(*) AS number_of_reports
FROM buildings_energy;

-- 2. Consommation et emissions par type de batiment (annee la plus recente)
SELECT
    building_type,
    COUNT(DISTINCT building_id) AS number_of_buildings,
    ROUND(AVG(site_eui), 2) AS average_site_eui,
    ROUND(SUM(site_energy_use), 2) AS total_energy_use,
    ROUND(SUM(total_ghg_emissions), 2) AS total_ghg_emissions
FROM buildings_energy
WHERE data_year = (SELECT MAX(data_year) FROM buildings_energy)
GROUP BY building_type
ORDER BY total_energy_use DESC;

-- 3. Top 10 des batiments les plus consommateurs (annee la plus recente)
SELECT
    building_name,
    building_type,
    neighborhood,
    ROUND(site_energy_use, 2) AS site_energy_use,
    ROUND(site_eui, 2) AS site_eui,
    ROUND(total_ghg_emissions, 2) AS total_ghg_emissions
FROM buildings_energy
WHERE data_year = (SELECT MAX(data_year) FROM buildings_energy)
ORDER BY site_energy_use DESC
LIMIT 10;

-- 4. Emissions de CO2 par quartier (annee la plus recente)
SELECT
    neighborhood,
    COUNT(DISTINCT building_id) AS number_of_buildings,
    ROUND(SUM(total_ghg_emissions), 2) AS total_ghg_emissions,
    ROUND(AVG(ghg_emissions_intensity), 2) AS average_ghg_intensity
FROM buildings_energy
WHERE data_year = (SELECT MAX(data_year) FROM buildings_energy)
GROUP BY neighborhood
ORDER BY total_ghg_emissions DESC;

-- 5. Batiments par statut de conformite (annee la plus recente)
SELECT
    compliance_status,
    COUNT(DISTINCT building_id) AS number_of_buildings
FROM buildings_energy
WHERE data_year = (SELECT MAX(data_year) FROM buildings_energy)
GROUP BY compliance_status
ORDER BY number_of_buildings DESC;

-- 6. Batiments prioritaires pour une premiere investigation (annee la plus recente)
-- priority_score est calcule par annee (voir src/indicators.py).
SELECT
    building_name,
    building_type,
    neighborhood,
    data_year,
    ROUND(site_eui, 2) AS site_eui,
    ROUND(total_ghg_emissions, 2) AS total_ghg_emissions,
    ROUND(energy_star_score, 2) AS energy_star_score,
    ROUND(priority_score, 4) AS priority_score
FROM buildings_energy
WHERE data_year = (SELECT MAX(data_year) FROM buildings_energy)
ORDER BY priority_score DESC
LIMIT 10;

-- 7. Evolution annuelle
-- Le nombre de batiments declares varie chaque annee : comparer les totaux avec prudence.
SELECT
    data_year,
    COUNT(DISTINCT building_id) AS number_of_buildings,
    ROUND(SUM(site_energy_use), 2) AS total_energy_use,
    ROUND(AVG(site_eui), 2) AS average_site_eui,
    ROUND(SUM(total_ghg_emissions), 2) AS total_ghg_emissions
FROM buildings_energy
GROUP BY data_year
ORDER BY data_year;

-- 8. Repartition par categorie ENERGY STAR (annee la plus recente)
-- La categorie 'Non renseigne' regroupe les batiments sans score.
SELECT
    energy_star_category,
    COUNT(DISTINCT building_id) AS number_of_buildings,
    ROUND(AVG(site_eui), 2) AS average_site_eui,
    ROUND(SUM(total_ghg_emissions), 2) AS total_ghg_emissions
FROM buildings_energy
WHERE data_year = (SELECT MAX(data_year) FROM buildings_energy)
GROUP BY energy_star_category
ORDER BY number_of_buildings DESC;

-- 9. Qualite des donnees
SELECT
    SUM(energy_star_score_was_missing) AS missing_energy_star_scores,
    SUM(natural_gas_was_missing) AS completed_natural_gas_values,
    ROUND(AVG(energy_star_score_was_missing) * 100, 2) AS missing_energy_star_rate,
    ROUND(AVG(natural_gas_was_missing) * 100, 2) AS completed_natural_gas_rate
FROM buildings_energy;
