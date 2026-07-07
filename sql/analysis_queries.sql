-- Requetes d'analyse simples pour le dashboard energetique.

-- 1. Vue globale des principaux KPI
SELECT
    COUNT(*) AS number_of_buildings,
    ROUND(SUM(site_energy_use), 2) AS total_energy_use,
    ROUND(AVG(site_eui), 2) AS average_site_eui,
    ROUND(SUM(total_ghg_emissions), 2) AS total_ghg_emissions,
    ROUND(AVG(energy_star_score), 2) AS average_energy_star_score
FROM buildings_energy;

-- 2. Consommation et emissions par type de batiment
SELECT
    building_type,
    COUNT(*) AS number_of_buildings,
    ROUND(AVG(site_eui), 2) AS average_site_eui,
    ROUND(SUM(site_energy_use), 2) AS total_energy_use,
    ROUND(SUM(total_ghg_emissions), 2) AS total_ghg_emissions
FROM buildings_energy
GROUP BY building_type
ORDER BY total_energy_use DESC;

-- 3. Top 10 des batiments les plus consommateurs
SELECT
    building_name,
    building_type,
    neighborhood,
    ROUND(site_energy_use, 2) AS site_energy_use,
    ROUND(total_ghg_emissions, 2) AS total_ghg_emissions
FROM buildings_energy
ORDER BY site_energy_use DESC
LIMIT 10;

-- 4. Emissions de CO2 par quartier
SELECT
    neighborhood,
    COUNT(*) AS number_of_buildings,
    ROUND(SUM(total_ghg_emissions), 2) AS total_ghg_emissions,
    ROUND(AVG(ghg_emissions_intensity), 2) AS average_ghg_intensity
FROM buildings_energy
GROUP BY neighborhood
ORDER BY total_ghg_emissions DESC;

-- 5. Batiments par statut de conformite
SELECT
    compliance_status,
    COUNT(*) AS number_of_buildings
FROM buildings_energy
GROUP BY compliance_status
ORDER BY number_of_buildings DESC;

-- 6. Batiments prioritaires pour une premiere investigation
SELECT
    building_name,
    building_type,
    neighborhood,
    data_year,
    ROUND(site_energy_use, 2) AS site_energy_use,
    ROUND(total_ghg_emissions, 2) AS total_ghg_emissions,
    ROUND(energy_star_score, 2) AS energy_star_score,
    ROUND(priority_score, 4) AS priority_score
FROM buildings_energy
ORDER BY priority_score DESC
LIMIT 10;

-- 7. Evolution annuelle
SELECT
    data_year,
    COUNT(*) AS number_of_buildings,
    ROUND(SUM(site_energy_use), 2) AS total_energy_use,
    ROUND(AVG(site_eui), 2) AS average_site_eui,
    ROUND(SUM(total_ghg_emissions), 2) AS total_ghg_emissions
FROM buildings_energy
GROUP BY data_year
ORDER BY data_year;

-- 8. Repartition par categorie ENERGY STAR
SELECT
    energy_star_category,
    COUNT(*) AS number_of_buildings,
    ROUND(AVG(site_eui), 2) AS average_site_eui,
    ROUND(SUM(total_ghg_emissions), 2) AS total_ghg_emissions
FROM buildings_energy
GROUP BY energy_star_category
ORDER BY number_of_buildings DESC;

-- 9. Qualite des donnees completees pendant le nettoyage
SELECT
    SUM(energy_star_score_was_missing) AS completed_energy_star_scores,
    SUM(natural_gas_was_missing) AS completed_natural_gas_values,
    ROUND(AVG(energy_star_score_was_missing) * 100, 2) AS completed_energy_star_rate,
    ROUND(AVG(natural_gas_was_missing) * 100, 2) AS completed_natural_gas_rate
FROM buildings_energy;
