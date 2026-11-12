"""Indicateurs partages par les notebooks 03 (analyse) et 04 (export Tableau).

Centraliser le calcul ici evite que l'analyse et le fichier du tableau de bord
divergent.
"""

import pandas as pd

# Poids du score de priorite.
PRIORITY_WEIGHTS = {
    'site_eui': 0.4,              # intensite energetique (kBtu/sf) : inefficacite
    'total_ghg_emissions': 0.4,   # emissions totales : impact carbone
    'low_energy_star': 0.2,       # score ENERGY STAR faible
}


def energy_star_category(score: pd.Series) -> pd.Series:
    """Categorie simple du score ENERGY STAR, 'Non renseigne' si absent."""
    category = pd.cut(
        score,
        bins=[0, 50, 75, 100],
        labels=['A verifier', 'Moyen', 'Bon'],
        include_lowest=True,
    )
    return category.astype('string').fillna('Non renseigne')


def priority_score(df: pd.DataFrame) -> pd.Series:
    """Score de priorite entre 0 et 1 (1 = a auditer en premier).

    Les rangs sont calcules **a l'interieur de chaque annee de declaration** :
    un batiment est compare aux autres batiments de la meme annee, et chaque
    annee a son propre classement (pas de doublons d'un meme batiment dans un
    top multi-annees).

    Un score ENERGY STAR absent recoit une valeur neutre (0,5) au lieu d'etre
    invente.
    """
    by_year = df.groupby('data_year')
    eui_rank = by_year['site_eui'].rank(pct=True)
    ghg_rank = by_year['total_ghg_emissions'].rank(pct=True)
    low_star_rank = (
        (100 - df['energy_star_score'])
        .groupby(df['data_year'])
        .rank(pct=True)
        .fillna(0.5)
    )
    score = (
        eui_rank * PRIORITY_WEIGHTS['site_eui']
        + ghg_rank * PRIORITY_WEIGHTS['total_ghg_emissions']
        + low_star_rank * PRIORITY_WEIGHTS['low_energy_star']
    )
    return score.round(4)


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute les colonnes calculees utilisees par l'analyse et le dashboard."""
    return df.assign(
        building_age=df['data_year'] - df['year_built'],
        energy_use_per_floor=df['site_energy_use'] / df['number_of_floors'],
        # Surface totale (parking inclus) : differe de site_eui, calcule par la
        # source sur la surface des batiments hors parking.
        energy_per_sqft=df['site_energy_use'] / df['property_gfa_total'],
        energy_star_category=energy_star_category(df['energy_star_score']),
        priority_score=priority_score(df),
    )
