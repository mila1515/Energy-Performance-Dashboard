import pandas as pd
import streamlit as st

from energy_watch.data import fmt_number, fmt_pct, load_reports
from energy_watch.monitoring import building_history, detect_alerts


@st.cache_data
def building_options(reports: pd.DataFrame) -> dict[int, str]:
    """building_id -> libelle, d'apres la declaration la plus recente de chaque batiment."""
    latest = reports.sort_values('data_year').groupby('building_id').last()
    labels = latest['building_name'] + ' · ' + latest['neighborhood'] + ' (#' + latest.index.astype(str) + ')'
    return labels.sort_values().to_dict()


reports = load_reports()
year = st.session_state.year
options = building_options(reports)

# Le choix est conserve pendant la session (y compris depuis la page Alertes).
building_id = st.selectbox(
    'Bâtiment',
    list(options),
    format_func=lambda b: options[b],
    key='building',
    persist_state='session',
    index=None,
    placeholder='Rechercher un bâtiment par nom ou quartier',
)

if building_id is None:
    st.info(
        'Choisissez un bâtiment, ou ouvrez une fiche depuis la page Alertes.',
        icon=':material/search:',
    )
    st.stop()

hist = building_history(reports, building_id)
last = hist.iloc[-1]
prev = hist.iloc[-2] if len(hist) > 1 else None

st.subheader(last['building_name'], anchor=False)
st.caption(
    f'{last["building_type"]} · {last["neighborhood"]} · construit en {int(last["year_built"])} · '
    f'{int(last["number_of_floors"])} étages · {fmt_number(last["property_gfa_total"], 0)} sf · '
    f'déclaré {len(hist)} fois ({int(hist["data_year"].min())}–{int(last["data_year"])})'
)

if int(last['data_year']) != year:
    st.warning(
        f'Pas de déclaration en {year} : les indicateurs ci-dessous portent sur {int(last["data_year"])}.',
        icon=':material/history:',
    )


def change(column: str):
    if prev is None:
        return None
    return fmt_pct(last[column] / prev[column] - 1)


with st.grid(5, min_column_width=170, gap='small'):
    st.metric(
        'Site EUI', f'{last["site_eui"]:.1f}'.replace('.', ','), change('site_eui'),
        delta_color='inverse', border=True, height='stretch',
        chart_data=hist['site_eui'].tolist(),
        help='kBtu par pied carré. Variation par rapport à la déclaration précédente.',
    )
    st.metric(
        'Consommation', f'{fmt_number(last["site_energy_use"])} kBtu', change('site_energy_use'),
        delta_color='inverse', border=True, height='stretch',
        chart_data=hist['site_energy_use'].tolist(),
    )
    st.metric(
        'Émissions de CO2', f'{fmt_number(last["total_ghg_emissions"], 0)} t', change('total_ghg_emissions'),
        delta_color='inverse', border=True, height='stretch',
        chart_data=hist['total_ghg_emissions'].tolist(),
    )
    star = last['energy_star_score']
    st.metric(
        'ENERGY STAR', '—' if pd.isna(star) else f'{star:.0f}',
        None if prev is None or pd.isna(star) or pd.isna(prev['energy_star_score'])
        else round(star - prev['energy_star_score']),
        border=True, height='stretch',
        chart_data=hist['energy_star_score'].fillna(0).tolist(),
    )
    st.metric(
        'Rang de priorité',
        f'{int(last["priority_rank"])} / {int(last["buildings_in_year"])}'.replace(',', ' '),
        None if prev is None else int(prev['priority_rank'] - last['priority_rank']),
        border=True, height='stretch',
        help='1 = bâtiment le plus prioritaire de l’année. Une hausse signifie que le bâtiment remonte dans le classement.',
        delta_color='inverse',
    )

left, right = st.columns(2)
with left:
    with st.container(border=True):
        st.subheader('Intensité comparée aux pairs', anchor=False)
        st.caption(f'Médiane des bâtiments « {last["building_type"]} » de la même année.')
        chart = hist[['data_year', 'site_eui', 'peer_median_eui']].rename(
            columns={'site_eui': 'Ce bâtiment', 'peer_median_eui': 'Médiane des pairs'}
        )
        st.line_chart(
            chart, x='data_year', y=['Ce bâtiment', 'Médiane des pairs'],
            x_label='Année', y_label='Site EUI (kBtu/sf)',
            alt='Site EUI du bâtiment comparé à la médiane de son type, par année',
        )
with right:
    with st.container(border=True):
        st.subheader('Consommation et émissions', anchor=False)
        st.caption('Consommation en millions de kBtu, émissions en tonnes de CO2e.')
        energy = hist.assign(
            **{'Consommation (M kBtu)': hist['site_energy_use'] / 1e6, 'Émissions (t CO2e)': hist['total_ghg_emissions']}
        )
        st.line_chart(
            energy, x='data_year', y=['Consommation (M kBtu)', 'Émissions (t CO2e)'],
            x_label='Année', y_label='',
            alt='Consommation et émissions du bâtiment par année',
        )

building_alerts = detect_alerts(reports, int(last['data_year']))
building_alerts = building_alerts[building_alerts['building_id'] == building_id]
with st.container(border=True):
    st.subheader(f'Alertes {int(last["data_year"])}', anchor=False)
    if building_alerts.empty:
        st.success('Aucune alerte pour ce bâtiment.', icon=':material/check_circle:')
    for _, alert in building_alerts.iterrows():
        icon = {'Haute': ':material/error:', 'Moyenne': ':material/warning:'}.get(alert['severity'], ':material/info:')
        st.markdown(f'{icon} **{alert["alert"]}** ({alert["severity"].lower()}) : {alert["detail"]}')

with st.expander('Toutes les déclarations'):
    st.dataframe(
        hist[['data_year', 'site_eui', 'peer_median_eui', 'site_energy_use', 'total_ghg_emissions',
              'energy_star_score', 'compliance_status', 'priority_score']],
        hide_index=True,
        column_config={
            'data_year': st.column_config.NumberColumn('Année', format='%d'),
            'site_eui': st.column_config.NumberColumn('Site EUI', format='%.1f'),
            'peer_median_eui': st.column_config.NumberColumn('Médiane des pairs', format='%.1f'),
            'site_energy_use': st.column_config.NumberColumn('Consommation (kBtu)', format='localized'),
            'total_ghg_emissions': st.column_config.NumberColumn('CO2 (t)', format='%.1f'),
            'energy_star_score': st.column_config.NumberColumn('ENERGY STAR', format='%.0f'),
            'compliance_status': st.column_config.TextColumn('Conformité'),
            'priority_score': st.column_config.ProgressColumn('Priorité', min_value=0, max_value=1, format='%.2f'),
        },
        alt='Historique des déclarations du bâtiment',
    )
