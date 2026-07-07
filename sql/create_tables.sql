-- Creation d'une table simple pour analyser la performance energetique.


CREATE TABLE buildings_energy (
    building_id INTEGER,
    data_year INTEGER,
    building_name VARCHAR(255),
    building_type VARCHAR(100),
    neighborhood VARCHAR(100),
    year_built INTEGER,
    number_of_floors INTEGER,
    property_gfa_total FLOAT,
    energy_star_score FLOAT,
    site_eui FLOAT,
    site_energy_use FLOAT,
    electricity_kwh FLOAT,
    natural_gas_therms FLOAT,
    total_ghg_emissions FLOAT,
    ghg_emissions_intensity FLOAT,
    compliance_status VARCHAR(100),
    energy_star_score_was_missing INTEGER,
    natural_gas_was_missing INTEGER,
    building_age INTEGER,
    energy_use_per_floor FLOAT,
    energy_per_sqft FLOAT,
    energy_star_category VARCHAR(50),
    priority_score FLOAT
);
