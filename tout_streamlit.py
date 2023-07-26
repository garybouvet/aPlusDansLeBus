import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from PIL import Image
import streamlit_folium as folium_st
from streamlit_folium import folium_static
import folium
import seaborn as sns
import geopandas as gpd
import locale
from datetime import datetime, timedelta

st.set_page_config(
    page_title = "TBM : un diaporama du réseau",
    page_icon = "🚲🚌🚃⛴️",
    layout="wide",
)

@st.cache_data
def load_data_and_create_geodataframe():
    df = pd.read_csv('/Users/garybouvet/Desktop/Streamlit_projet_3/gdfbustrambat.csv')
    gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['geometry']))
    gdf['geometry'] = gdf['geometry'].simplify(0.01, preserve_topology=False)  # Adjust the tolerance as needed
    return gdf


gdf = load_data_and_create_geodataframe()

logo = Image.open('/Users/garybouvet/Desktop/Streamlit_projet_3/LOGO_TBM.png')

with st.sidebar:
    st.image(logo)
    selected = st.selectbox('Choose a page', ['Home', 'V3', 'BUS/TRAM/BAT3'])

if selected == 'Home':
    # Code for first page goes here
    video_file = open('/Users/garybouvet/Desktop/Streamlit_projet_3/output_acceléré.mp4', 'rb')
    video_bytes = video_file.read()

    st.video(video_bytes)

    @st.cache_data
    def load_data():
        # Load the data from the CSV file.
        data = pd.read_csv("/Users/garybouvet/Desktop/PROJET_DATA_3/Gary_all_data/station_vCube_10.csv")

        # Convert 'mdate' to datetime.
        data['mdate'] = pd.to_datetime(data['mdate'])  # Convert to datetime

        # Extract date and time in the format HH:mm
        data['formatted_date'] = data['mdate'].dt.strftime('%A %d %B %Y') # This will give day in French, i.e., Lundi, Mardi, etc.
        data['time'] = data['mdate'].dt.strftime('%H:%M')
        return data

    def create_map(filtered_data, selected_tile):
        # Create a basic map.
        m = folium.Map(location=[44.8378, -0.5792], zoom_start=13, tiles=selected_tile, attr='Map data © OpenStreetMap contributors')

        # Add markers for each station.
        for index, row in filtered_data.iterrows():
            nom = row['nom']
            nbvelos = row['nbvelos']
            latitude = row['latitude']
            longitude = row['longitude']
            etat = row['etat']
            nbelec = row['nbelec']
            nbclassiq = row['nbclassiq']
            nbplaces = row['nbplaces']  # Assuming 'nbplaces' is a column in your data

            if etat == 'CONNECTEE':
                color = '#E37222'
            elif etat == 'MAINTENANCE':
                color = '#0A8A9F'
            elif etat == 'DECONNECTEE':
                color = 'red'

            radius = nbvelos * 1.5

            fill = True if selected_tile in ['Stamen Toner', 'OpenStreetMap'] else False
            fill_color = color if fill else None

            # Create a string with the data to be included in the popup
            popup_text = f"""
            <div style="font-size:12px">
            <h4 style="color:{color};margin-bottom:0">{nom}</h4>
            <p style="margin-bottom:0"><b>État:</b> {etat}</p>
            <p style="margin-bottom:0"><b>Places disponible:</b> {nbplaces}</p>
            <p style="margin-bottom:0"><b>Vélos disponible:</b> {nbvelos}</p>
            <p style="margin-bottom:0"><b>Vélos électriques:</b> {nbelec}</p>
            <p style="margin-bottom:0"><b>Vélos lassiques:</b> {nbclassiq}</p>
            </div>
            """
            popup = folium.Popup(popup_text, max_width=250)

            marker = folium.CircleMarker(
                location=[latitude, longitude], 
                color=color, 
                fill=fill, 
                fill_color=fill_color,
                radius=radius,
                weight=1,
                popup=popup  # Add the popup to the marker
            )
            marker.add_to(m)

        return m


    # Load data
    data = load_data()

    # Set locale to French
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

    # Custom styles, including the custom font
    st.markdown(
        """
        <style>
        .leaflet-pane {
            filter: brightness(200%);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Date Selectbox
    date_format_mapping = pd.Series(data.formatted_date.values,index=data.mdate.dt.date).to_dict()
    unique_dates = sorted(date_format_mapping.items())[1:]  # Skip the first date
    selected_date = st.selectbox('Select a date', ['Selectionnez une date..'] + unique_dates, format_func=lambda x: x[1] if x != 'Selectionnez une date..' else x)

    # Time Selectbox
    unique_times = sorted(data['time'].unique())
    selected_time = st.selectbox('Select a time', options=unique_times)

    # Tiles Selectbox
    tiles_options = ['CartoDB dark_matter', 'Stamen Toner', 'OpenStreetMap']
    tiles_mapping = {
        'CartoDB dark_matter': 'CartoDB dark_matter',
        'Stamen Toner': 'Stamen Toner',
        'OpenStreetMap': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    }

    selected_tile = st.selectbox('Select a tile', options=tiles_options)
    tile_url = tiles_mapping[selected_tile]
    tile_attr = 'Map data © OpenStreetMap contributors'

    # Filter data based on the selected date and time.
    filtered_data = data[(data['mdate'].dt.date == selected_date[0]) & (data['time'] == selected_time)] if selected_date != 'Selectionnez une date..' else pd.DataFrame()

    # Create map
    m = create_map(filtered_data, tile_url)

    # Add legend
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 50px;
        left: 50px;
        width: 100px;
        height: 90px; 
        z-index:9999;
        font-size:14px;
        ">
        <p><a style="color:#E37222;font-size:150%;margin-left:20px;">•</a>&emsp;CONNECTEE</p>
        <p><a style="color:#0A8A9F;font-size:150%;margin-left:20px;">•</a>&emsp;MAINTENANCE</p>
        <p><a style="color:red;font-size:150%;margin-left:20px;">•</a>&emsp;DECONNECTEE</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Display the dynamic map using folium_static
    folium_static(m, width=945, height=450)

elif selected == 'V3':
    # Code for 'V3' option goes here
    st.markdown('<iframe title="v3" width="945" height="450" src="https://app.powerbi.com/reportEmbed?reportId=a5a6fa02-137c-48ca-9754-8467b7366089&autoAuth=true&ctid=5892e2db-e39d-4cc1-a179-dc66550efc30" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)

elif selected == 'BUS/TRAM/BAT3':
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    # Adding the radio button
    vehicle_type = st.radio('',['ALL', 'TRAM', 'BUS', 'BATEAU'])
    show_retard = st.checkbox('RETARD')

    # Filter the GeoDataFrame based on the selected vehicle type
    if vehicle_type != 'ALL':
        gdf = gdf[gdf['vehicule'] == vehicle_type]

    # Redraw the map based on the filtered GeoDataFrame
    m = folium.Map(location=[44.841424, -0.570334], tiles='Stamen Toner', zoom_start=13)

    # Define color and emoji dictionary
    lines = ['Tram B','Tram C','Tram A','Tram D','Lianes 1', 'Lianes 2', 'Lianes 3', 'Lianes 4', 'Lianes 5', 'Lianes 9', 'Lianes 10', 'Lianes 11', 'Lianes 15', 'Lianes 16', 'BAT3']
    palette = sns.color_palette('husl', len(lines)).as_hex()  # Generate a color palette with as many colors as there are lines
    color_dict = dict(zip(lines, palette))  # Create a dictionary mapping each line to a color

    emoji_dict = {'TRAM': u'\U0001F68B', 'BUS': u'\U0001F68C', 'BATEAU': u'\U0001F6A2'}  # Define emoji dictionary

    n = 5000  # Place a marker every nth point
    
     # Add lines
    for index, row in gdf.iterrows():
        # Get color and weight based on line, default to white if line not found in color_dict
        if show_retard and row['retard'] > 100:
            line_color = 'red'
            line_weight = 20  # Increase weight for retard lines
        else:
            line_color = color_dict.get(row['ligne_com'], 'white')
            line_weight = 2.5  # Default weight for other lines
        line_emoji = emoji_dict.get(row['vehicule'], '')  # Get emoji based on vehicle type

        # If geometry type is MultiLineString
        if row['geometry'].geom_type == 'MultiLineString':
            for line in row['geometry'].geoms:
                line_coords = [(y, x) for x, y in list(line.coords)]
                for i in range(0, len(line_coords), n):  # Add a marker every nth point
                    folium.Marker(line_coords[i], icon=folium.DivIcon(html=f"<div style='font-size: 12pt'>{line_emoji}</div>")).add_to(m)

                popup_text = f"Ligne: {row['ligne_com']}<br>Terminus: {row['libelle']}<br>Vehicule: {line_emoji} {row['vehicule']}<br>Retard Moyen: {row['retard']}<br>Vitesse Moyenne: {row['vitesse']}<br>Nombre de véhicule/ligne: {row['nb_vehicule']}"
                folium.PolyLine(line_coords, color=line_color, weight=2.5, opacity=1).add_child(folium.Popup(popup_text)).add_to(m)
        # If geometry type is LineString
        elif row['geometry'].geom_type == 'LineString':
            line_coords = [(y, x) for x, y in list(row['geometry'].coords)]
            for i in range(0, len(line_coords), n):  # Add a marker every nth point
                folium.Marker(line_coords[i], icon=folium.DivIcon(html=f"<div style='font-size: 12pt'>{line_emoji}</div>")).add_to(m)

            popup_text = f"Ligne: {row['ligne_com']}<br>Terminus: {row['libelle']}<br>Vehicule: {line_emoji} {row['vehicule']}<br>Retard Moyen: {row['retard']}<br>Vitesse Moyenne: {row['vitesse']}<br>Nombre de véhicule/ligne: {row['nb_vehicule']}"
            folium.PolyLine(line_coords, color=line_color, weight=2.5, opacity=1).add_child(folium.Popup(popup_text)).add_to(m)

    folium_static(m, width=945, height=450)
    st.markdown('<iframe title="BTB_fin" width="945" height="450" src="https://app.powerbi.com/reportEmbed?reportId=7f601950-66d2-4060-840b-21740784a6dc&autoAuth=true&ctid=5892e2db-e39d-4cc1-a179-dc66550efc30" frameborder="0" allowfullscreen></iframe>', unsafe_allow_html=True)
