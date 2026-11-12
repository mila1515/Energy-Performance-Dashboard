import pandas as pd
import streamlit as st

from energy_watch.data import load_reports
from energy_watch.monitoring import data_quality_by_year

reports = load_reports()
year = st.session_state.year
quality = data_quality_by_year(reports)
row = quality.set_index('data_year').loc[year]
prev = quality.set_index('data_year').loc[year - 1] if year - 1 in quality['data_year'].values else None


def diff(column: str):
    if prev is None or pd.isna(row[column]) or pd.isna(prev[column]):
        return None
    return round(row[column] - prev[column], 1)


absent = row['missing_vs_prev']


with st.grid(4, min_column_width=180, gap='small'):
    st.metric('Déclarations', int(row['declarations']), diff('declarations'), delta_color='off',
              border=True, height='stretch')
    st.metric('Sans score ENERGY STAR', f'{row["missing_star_pct"]:.1f} %'.replace('.', ','),
              diff('missing_star_pct'), delta_color='inverse', border=True, height='stretch',
              help='Part des déclarations sans score ENERGY STAR : le score est laissé vide, pas estimé.')
    st.metric('Gaz complété par 0', f'{row["gas_filled_pct"]:.1f} %'.replace('.', ','),
              diff('gas_filled_pct'), delta_color='inverse', border=True, height='stretch',
              help='Part des déclarations sans consommation de gaz, considérée comme nulle.')
    st.metric('Absents par rapport à N-1',
              '—' if pd.isna(absent) else int(absent),
              diff('missing_vs_prev'),
              delta_color='inverse', border=True, height='stretch',
              help="Bâtiments déclarés l'année précédente mais pas cette année.")

left, right = st.columns(2)
with left:
    with st.container(border=True):
        st.subheader('Complétude par année', anchor=False)
        st.line_chart(
            quality.rename(columns={'missing_star_pct': 'Sans ENERGY STAR (%)',
                                    'gas_filled_pct': 'Gaz complété (%)'}),
            x='data_year', y=['Sans ENERGY STAR (%)', 'Gaz complété (%)'],
            x_label='Année', y_label='% des déclarations',
            alt='Part des valeurs manquantes par année, stable autour de 24 % et 36 %',
        )
with right:
    with st.container(border=True):
        st.subheader('Entrées et sorties du périmètre', anchor=False)
        st.bar_chart(
            quality.dropna(subset=['new_buildings']).rename(
                columns={'new_buildings': 'Nouveaux', 'missing_vs_prev': 'Absents'}),
            x='data_year', y=['Nouveaux', 'Absents'], stack=False,
            x_label='Année', y_label='Bâtiments',
            alt='Bâtiments nouveaux et absents par année, forte rotation en 2021 et 2022',
        )

with st.container(border=True):
    st.subheader('Détail par année', anchor=False)
    st.dataframe(
        quality,
        hide_index=True,
        column_config={
            'data_year': st.column_config.NumberColumn('Année', format='%d'),
            'declarations': st.column_config.NumberColumn('Déclarations'),
            'missing_star_pct': st.column_config.NumberColumn('Sans ENERGY STAR (%)', format='%.1f'),
            'gas_filled_pct': st.column_config.NumberColumn('Gaz complété (%)', format='%.1f'),
            'not_compliant': st.column_config.NumberColumn('Non conformes'),
            'new_buildings': st.column_config.NumberColumn('Nouveaux', format='%d'),
            'missing_vs_prev': st.column_config.NumberColumn('Absents vs N-1', format='%d'),
        },
        alt='Indicateurs de qualité des données par année',
    )

st.caption(
    "En amont, le nettoyage (notebook 02) a déjà écarté les déclarations incomplètes ou incohérentes, "
    'dont 29 lignes à l’intensité irréaliste (hors de 1 à 1 000 kBtu/sf).'
)
