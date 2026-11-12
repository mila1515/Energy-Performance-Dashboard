"""Indicateurs de suivi et detection d'alertes.

Toutes les fonctions prennent le fichier du tableau de bord
(dashboard/building_energy_performance_dashboard.csv) : une ligne par
batiment et par annee de declaration. Elles n'utilisent pas Streamlit, ce qui
permet de les tester et de les reutiliser (rapport, notifications...).
"""

from dataclasses import dataclass

import pandas as pd

SEVERITY_ORDER = {'Haute': 0, 'Moyenne': 1, 'Basse': 2}

ALERT_EUI_DRIFT = "Dérive de l'intensité"
ALERT_STAR_DROP = 'ENERGY STAR sous 50'
ALERT_NON_COMPLIANT = 'Devenu non conforme'
ALERT_MISSING = 'Déclaration manquante'
ALERT_PEERS = 'Très au-dessus des pairs'
ALERT_TYPES = [ALERT_EUI_DRIFT, ALERT_STAR_DROP, ALERT_NON_COMPLIANT, ALERT_MISSING, ALERT_PEERS]


@dataclass(frozen=True)
class AlertSettings:
    eui_drift: float = 0.25        # hausse du Site EUI d'une annee sur l'autre (25 %)
    min_prev_eui: float = 5.0      # ignore les hausses calculees sur une base quasi nulle
    peer_ratio: float = 3.0        # Site EUI >= 3 x la mediane du meme type de batiment
    star_threshold: float = 50.0   # score ENERGY STAR qui passe sous ce seuil


def yearly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """KPI par annee (perimetre de chaque annee)."""
    return (
        df.groupby('data_year')
        .agg(
            buildings=('building_id', 'nunique'),
            energy=('site_energy_use', 'sum'),
            ghg=('total_ghg_emissions', 'sum'),
            median_eui=('site_eui', 'median'),
            mean_star=('energy_star_score', 'mean'),
        )
        .reset_index()
    )


def like_for_like(df: pd.DataFrame, year: int) -> dict[str, float] | None:
    """Variations entre year-1 et year sur les seuls batiments declares les deux annees.

    Comparer les totaux bruts melangerait l'effet des batiments qui entrent ou
    sortent du perimetre : on compare donc a perimetre constant.
    """
    cur = df[df['data_year'] == year].set_index('building_id')
    prev = df[df['data_year'] == year - 1].set_index('building_id')
    common = cur.index.intersection(prev.index)
    if common.empty:
        return None
    cur, prev = cur.loc[common], prev.loc[common]
    return {
        'buildings': len(common),
        'energy_pct': cur['site_energy_use'].sum() / prev['site_energy_use'].sum() - 1,
        'ghg_pct': cur['total_ghg_emissions'].sum() / prev['total_ghg_emissions'].sum() - 1,
        'median_eui_diff': cur['site_eui'].median() - prev['site_eui'].median(),
        'mean_star_diff': cur['energy_star_score'].mean() - prev['energy_star_score'].mean(),
    }


def peer_medians(df: pd.DataFrame) -> pd.DataFrame:
    """Site EUI median par annee et par type de batiment (reference des pairs)."""
    return df.groupby(['data_year', 'building_type'], as_index=False).agg(
        peer_median_eui=('site_eui', 'median')
    )


def with_peers(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute la mediane des pairs et l'ecart relatif a cette mediane."""
    out = df.merge(peer_medians(df), on=['data_year', 'building_type'], how='left')
    out['peer_ratio'] = out['site_eui'] / out['peer_median_eui']
    return out


def detect_alerts(df: pd.DataFrame, year: int, settings: AlertSettings = AlertSettings()) -> pd.DataFrame:
    """Liste les alertes de l'annee `year` (une ligne par batiment et par alerte)."""
    columns = ['building_id', 'building_name', 'building_type', 'neighborhood',
               'alert', 'severity', 'detail', 'site_eui', 'eui_change']
    cur = with_peers(df[df['data_year'] == year]).set_index('building_id')
    prev = df[df['data_year'] == year - 1].set_index('building_id')
    alerts: list[pd.DataFrame] = []

    def collect(frame: pd.DataFrame, alert: str, severity, detail) -> None:
        if frame.empty:
            return
        part = frame.reset_index()[['building_id', 'building_name', 'building_type', 'neighborhood']].copy()
        part['alert'] = alert
        part['severity'] = severity(frame).values if callable(severity) else severity
        part['detail'] = detail(frame).values
        part['site_eui'] = frame['site_eui'].values if 'site_eui' in frame else float('nan')
        part['eui_change'] = frame['eui_change'].values if 'eui_change' in frame else float('nan')
        alerts.append(part)

    common = cur.index.intersection(prev.index)
    both = cur.loc[common].copy()
    both['prev_eui'] = prev.loc[common, 'site_eui']
    both['prev_star'] = prev.loc[common, 'energy_star_score']
    both['prev_status'] = prev.loc[common, 'compliance_status']
    both['eui_change'] = both['site_eui'] / both['prev_eui'] - 1

    # 1. Derive : l'intensite energetique augmente fortement d'une annee sur l'autre
    drift = both[(both['eui_change'] >= settings.eui_drift) & (both['prev_eui'] >= settings.min_prev_eui)]
    collect(
        drift, ALERT_EUI_DRIFT,
        lambda f: (f['eui_change'] >= 2 * settings.eui_drift).map({True: 'Haute', False: 'Moyenne'}),
        lambda f: f.apply(lambda r: f"Site EUI {r.prev_eui:.0f} → {r.site_eui:.0f} kBtu/sf "
                                    f"(+{r.eui_change * 100:.0f} %)", axis=1),
    )

    # 2. Le score ENERGY STAR passe sous le seuil
    star = both[(both['prev_star'] >= settings.star_threshold)
                & (both['energy_star_score'] < settings.star_threshold)]
    collect(
        star, ALERT_STAR_DROP, 'Moyenne',
        lambda f: f.apply(lambda r: f"Score {r.prev_star:.0f} → {r.energy_star_score:.0f}", axis=1),
    )

    # 3. Le batiment devient non conforme
    nc = both[(both['compliance_status'] == 'Not Compliant') & (both['prev_status'] != 'Not Compliant')]
    collect(nc, ALERT_NON_COMPLIANT, 'Moyenne',
            lambda f: pd.Series('Conforme en N-1, non conforme cette année', index=f.index))

    # 4. Declare l'annee precedente mais pas cette annee
    missing = prev.loc[prev.index.difference(cur.index)].copy()
    collect(missing, ALERT_MISSING, 'Basse',
            lambda f: pd.Series(f'Déclaré en {year - 1}, absent en {year}', index=f.index))

    # 5. Tres au-dessus de la mediane des batiments du meme type
    peers = cur[cur['peer_ratio'] >= settings.peer_ratio]
    collect(
        peers, ALERT_PEERS, 'Basse',
        lambda f: f.apply(lambda r: f"Site EUI {r.site_eui:.0f} = {r.peer_ratio:.1f} × la médiane ".replace('.', ',')
                                    + f"des {r.building_type} ({r.peer_median_eui:.0f})", axis=1),
    )

    if not alerts:
        return pd.DataFrame(columns=columns)
    out = pd.concat(alerts, ignore_index=True)[columns]
    return (
        out.assign(_order=out['severity'].map(SEVERITY_ORDER))
        .sort_values(['_order', 'eui_change'], ascending=[True, False])
        .drop(columns='_order')
        .reset_index(drop=True)
    )


def building_history(df: pd.DataFrame, building_id: int) -> pd.DataFrame:
    """Historique d'un batiment avec la mediane de ses pairs et son rang de priorite."""
    ranked = df.assign(
        priority_rank=df.groupby('data_year')['priority_score'].rank(ascending=False, method='min'),
        buildings_in_year=df.groupby('data_year')['building_id'].transform('nunique'),
    )
    hist = with_peers(ranked)
    return hist[hist['building_id'] == building_id].sort_values('data_year').reset_index(drop=True)


def data_quality_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Completude et continuite des declarations par annee."""
    ids_by_year = df.groupby('data_year')['building_id'].apply(set).sort_index()
    rows = []
    previous: set | None = None
    for year, ids in ids_by_year.items():
        sub = df[df['data_year'] == year]
        rows.append({
            'data_year': year,
            'declarations': len(sub),
            'missing_star_pct': sub['energy_star_score_was_missing'].mean() * 100,
            'gas_filled_pct': sub['natural_gas_was_missing'].mean() * 100,
            'not_compliant': int((sub['compliance_status'] == 'Not Compliant').sum()),
            'new_buildings': len(ids - previous) if previous is not None else None,
            'missing_vs_prev': len(previous - ids) if previous is not None else None,
        })
        previous = set(ids)
    return pd.DataFrame(rows)
