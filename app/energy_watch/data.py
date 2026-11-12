"""Chargement des donnees et mise en forme partagee par les pages."""

from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / 'dashboard' / 'building_energy_performance_dashboard.csv'


@st.cache_data(ttl='1h')
def load_reports() -> pd.DataFrame:
    """Une ligne par batiment et par annee (fichier produit par le notebook 04)."""
    return pd.read_csv(DATA_PATH)


def fmt_number(value: float, decimals: int = 1) -> str:
    """18289573028 -> '18,3 Md' ; 422958 -> '423 k' (notation francaise)."""
    if pd.isna(value):
        return '—'
    for factor, suffix in ((1e9, ' Md'), (1e6, ' M'), (1e3, ' k')):
        if abs(value) >= factor:
            return f'{value / factor:,.{decimals}f}{suffix}'.replace(',', ' ').replace('.', ',')
    return f'{value:,.{decimals}f}'.replace(',', ' ').replace('.', ',')


def fmt_pct(value: float | None) -> str | None:
    if value is None or pd.isna(value):
        return None
    return f'{value:+.1%}'.replace('.', ',')
