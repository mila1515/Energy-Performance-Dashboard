import streamlit as st

from energy_watch.data import fmt_number, fmt_pct, load_reports
from energy_watch.monitoring import detect_alerts, like_for_like, yearly_summary

reports = load_reports()
year = st.session_state.year
summary = yearly_summary(reports)
history = summary[summary['data_year'] <= year]
current = summary.set_index('data_year').loc[year]
lfl = like_for_like(reports, year)
current_reports = reports[reports['data_year'] == year]

if lfl:
    panel = f'{lfl["buildings"]:,}'.replace(',', ' ')
    st.caption(
        f'Variations par rapport à {year - 1}, calculées sur les {panel} bâtiments '
        'déclarés les deux années (périmètre constant).'
    )
else:
    st.caption(f'{year} est la première année disponible : pas de comparaison possible.')


def delta(key: str, kind: str = 'pct'):
    if not lfl:
        return None
    if kind == 'pct':
        return fmt_pct(lfl[key])
    return round(lfl[key], 1)


with st.grid(5, min_column_width=180, gap='small'):
    previous_count = summary.set_index('data_year')['buildings'].get(year - 1)
    st.metric(
        'Bâtiments déclarés',
        f'{int(current["buildings"]):,}'.replace(',', ' '),
        None if previous_count is None else int(current['buildings'] - previous_count),
        delta_color='off',
        border=True,
        chart_data=history['buildings'].tolist(),
        chart_type='bar',
        height='stretch',
    )
    st.metric(
        'Consommation totale',
        f'{fmt_number(current["energy"])} kBtu',
        delta('energy_pct'),
        delta_color='inverse',
        border=True,
        chart_data=history['energy'].tolist(),
        height='stretch',
    )
    st.metric(
        'Émissions de CO2',
        f'{fmt_number(current["ghg"], 0)} t',
        delta('ghg_pct'),
        delta_color='inverse',
        border=True,
        chart_data=history['ghg'].tolist(),
        height='stretch',
    )
    st.metric(
        'Site EUI médian',
        f'{current["median_eui"]:.1f} kBtu/sf'.replace('.', ','),
        delta('median_eui_diff', 'abs'),
        delta_color='inverse',
        border=True,
        chart_data=history['median_eui'].tolist(),
        help="Intensité énergétique : consommation par unité de surface. Plus bas = plus efficace.",
        height='stretch',
    )
    st.metric(
        'ENERGY STAR moyen',
        f'{current["mean_star"]:.1f}'.replace('.', ','),
        delta('mean_star_diff', 'abs'),
        border=True,
        chart_data=history['mean_star'].tolist(),
        help='Moyenne des bâtiments qui ont un score (1 à 100). Plus haut = mieux.',
        height='stretch',
    )

# Resume des alertes
alerts = detect_alerts(reports, year)
counts = alerts['severity'].value_counts()
with st.container(border=True, horizontal=True, vertical_alignment='center'):
    st.markdown(
        f"**{len(alerts)} alertes en {year}** · "
        f":red-badge[{counts.get('Haute', 0)} hautes] "
        f":orange-badge[{counts.get('Moyenne', 0)} moyennes] "
        f":gray-badge[{counts.get('Basse', 0)} basses]"
    )
    st.page_link('app_pages/alerts.py', label='Voir les alertes', icon=':material/arrow_forward:')

left, right = st.columns(2)
with left:
    with st.container(border=True):
        st.subheader('Intensité énergétique médiane', anchor=False)
        st.line_chart(
            summary,
            x='data_year',
            y='median_eui',
            x_label='Année',
            y_label='Site EUI médian (kBtu/sf)',
            alt="Site EUI médian par année, en baisse depuis 2017",
        )
    with st.container(border=True):
        st.subheader(f'Consommation par type de bâtiment ({year})', anchor=False)
        by_type = (
            current_reports.groupby('building_type', as_index=False)['site_energy_use'].sum()
            .assign(energy_bn=lambda d: d['site_energy_use'] / 1e9)
        )
        st.bar_chart(
            by_type,
            x='building_type',
            y='energy_bn',
            horizontal=True,
            sort='-energy_bn',
            x_label='',
            y_label='Consommation (milliards de kBtu)',
            alt=f'Consommation {year} par type de bâtiment, Nonresidential en tête',
        )

with right:
    with st.container(border=True):
        st.subheader(f'Émissions de CO2 par quartier ({year})', anchor=False)
        by_area = (
            current_reports.groupby('neighborhood', as_index=False)['total_ghg_emissions'].sum()
            .assign(ghg_k=lambda d: d['total_ghg_emissions'] / 1e3)
        )
        st.bar_chart(
            by_area,
            x='neighborhood',
            y='ghg_k',
            horizontal=True,
            sort='-ghg_k',
            x_label='',
            y_label='Émissions (milliers de t CO2e)',
            alt=f'Émissions {year} par quartier, Downtown en tête',
        )
    with st.container(border=True):
        st.subheader(f'Bâtiments prioritaires ({year})', anchor=False)
        top = current_reports.nlargest(10, 'priority_score')[
            ['building_name', 'building_type', 'site_eui', 'priority_score']
        ]
        st.dataframe(
            top,
            hide_index=True,
            column_config={
                'building_name': st.column_config.TextColumn('Bâtiment'),
                'building_type': st.column_config.TextColumn('Type'),
                'site_eui': st.column_config.NumberColumn('Site EUI', format='%.0f'),
                'priority_score': st.column_config.ProgressColumn(
                    'Priorité', min_value=0, max_value=1, format='%.2f'
                ),
            },
            alt=f'Dix bâtiments les plus prioritaires en {year}',
        )
