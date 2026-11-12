import streamlit as st

from energy_watch.data import load_reports
from energy_watch.monitoring import ALERT_TYPES, AlertSettings, detect_alerts

reports = load_reports()
year = st.session_state.year

if year - 1 in reports['data_year'].values:
    st.caption(
        f"Alertes {year} : comparaison de chaque bâtiment avec sa déclaration {year - 1} "
        'et avec la médiane des bâtiments du même type.'
    )
else:
    st.caption(
        f"{year} est la première année disponible : seules les alertes « au-dessus des pairs » "
        'peuvent être calculées.'
    )

with st.container(border=True):
    with st.container(horizontal=True, vertical_alignment='bottom'):
        drift = st.slider(
            "Seuil de dérive de l'intensité",
            min_value=10,
            max_value=100,
            value=25,
            step=5,
            format='+%d %%',
            key='alerts_drift',
            persist_state='session',
            help="Alerte si le Site EUI augmente d'au moins ce pourcentage par rapport à l'année précédente. "
                 'Sévérité haute au double du seuil.',
        )
        peer_ratio = st.slider(
            'Seuil « au-dessus des pairs »',
            min_value=1.5,
            max_value=5.0,
            value=3.0,
            step=0.5,
            format='× %.1f',
            key='alerts_peer_ratio',
            persist_state='session',
            help='Alerte si le Site EUI dépasse ce multiple de la médiane des bâtiments du même type.',
        )
    types = st.pills(
        "Types d'alerte",
        ALERT_TYPES,
        selection_mode='multi',
        default=ALERT_TYPES,
        key='alerts_types',
        persist_state='session',
    )

alerts = detect_alerts(reports, year, AlertSettings(eui_drift=drift / 100, peer_ratio=peer_ratio))
neighborhoods = sorted(alerts['neighborhood'].dropna().unique())
areas = st.multiselect(
    'Quartiers',
    neighborhoods,
    placeholder='Tous les quartiers',
    key='alerts_areas',
    persist_state='session',
)

filtered = alerts[alerts['alert'].isin(types or [])]
if areas:
    filtered = filtered[filtered['neighborhood'].isin(areas)]

counts = filtered['severity'].value_counts()
with st.container(horizontal=True):
    st.metric('Alertes', len(filtered), border=True)
    st.metric('Sévérité haute', int(counts.get('Haute', 0)), border=True)
    st.metric('Sévérité moyenne', int(counts.get('Moyenne', 0)), border=True)
    st.metric('Sévérité basse', int(counts.get('Basse', 0)), border=True)
    st.metric('Bâtiments concernés', filtered['building_id'].nunique(), border=True)

if filtered.empty:
    st.info('Aucune alerte avec ces filtres.', icon=':material/check_circle:')
    st.stop()

with st.container(border=True):
    with st.container(horizontal=True, vertical_alignment='center'):
        st.subheader('Liste des alertes', anchor=False)
        st.space('stretch')
        st.download_button(
            'Exporter en CSV',
            filtered.to_csv(index=False).encode('utf-8'),
            file_name=f'energy_watch_alertes_{year}.csv',
            mime='text/csv',
            icon=':material/download:',
            on_click='ignore',
        )
    st.caption('Sélectionnez une ligne pour ouvrir la fiche du bâtiment.')
    selection = st.dataframe(
        filtered,
        hide_index=True,
        on_select='rerun',
        selection_mode='single-row',
        key='alerts_table',
        column_order=['severity', 'alert', 'building_name', 'building_type', 'neighborhood', 'detail'],
        column_config={
            'severity': st.column_config.TextColumn('Sévérité'),
            'alert': st.column_config.TextColumn('Alerte'),
            'building_name': st.column_config.TextColumn('Bâtiment'),
            'building_type': st.column_config.TextColumn('Type'),
            'neighborhood': st.column_config.TextColumn('Quartier'),
            'detail': st.column_config.TextColumn('Détail', width='large'),
        },
        alt=f'Alertes {year} triées par sévérité',
    )

rows = selection.selection.rows
if rows:
    chosen = filtered.iloc[rows[0]]
    if st.button(
        f'Ouvrir la fiche : {chosen["building_name"]}',
        type='primary',
        icon=':material/apartment:',
    ):
        st.session_state.building = int(chosen['building_id'])
        st.switch_page('app_pages/building.py')
