"""Energy Watch : suivi continu de la performance energetique des batiments.

Lancement depuis la racine du projet :
    streamlit run app/streamlit_app.py
"""

import streamlit as st

from energy_watch.data import load_reports

st.set_page_config(page_title='Energy Watch', page_icon=':material/bolt:', layout='wide')

page = st.navigation(
    [
        st.Page(
            'app_pages/overview.py',
            title="Vue d'ensemble",
            icon=':material/dashboard:',
            default=True,
            help="KPI de l'année choisie, évolution à périmètre constant et bâtiments prioritaires.",
        ),
        st.Page(
            'app_pages/alerts.py',
            title='Alertes',
            icon=':material/notifications_active:',
            help="Bâtiments qui dérivent par rapport à l'année précédente ou à leurs pairs. "
                 'Filtrer, exporter et ouvrir la fiche d’un bâtiment.',
        ),
        st.Page(
            'app_pages/building.py',
            title='Fiche bâtiment',
            icon=':material/apartment:',
            help="Historique d'un bâtiment comparé à la médiane des bâtiments du même type.",
        ),
        st.Page(
            'app_pages/data_quality.py',
            title='Qualité des données',
            icon=':material/fact_check:',
            help='Complétude et continuité des déclarations, année par année.',
        ),
    ],
    position='top',
)

reports = load_reports()
years = sorted(reports['data_year'].unique().tolist(), reverse=True)

with st.sidebar:
    st.header('Energy Watch', anchor=False)
    # Partage entre les pages et conserve dans l'URL (?year=2023)
    st.selectbox(
        'Année analysée',
        years,
        key='year',
        bind='query-params',
        help="Les variations sont calculées par rapport à l'année précédente.",
    )
    st.caption(
        f'{reports["building_id"].nunique():,} bâtiments · {len(reports):,} déclarations '
        f'· {min(years)}–{max(years)}'.replace(',', ' ')
    )
    st.caption('Source : Building Energy Benchmarking, Ville de Seattle.')

st.title(page.title, icon=page.icon, anchor=False)
page.run()
