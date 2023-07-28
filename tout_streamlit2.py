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
from babel.dates import format_date


st.set_page_config(
    page_title = "TBM : un diaporama du réseau",
    page_icon = "🚲🚌🚃⛴️",
    layout="wide",
)


@st.cache_data
def load_data_and_create_geodataframe():
    df = pd.read_csv('./gdfbustrambat.csv')
    gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['geometry']))
    return gdf

gdf = load_data_and_create_geodataframe()

logo = Image.open('./LOGO_TBM.png')


with st.sidebar:
    st.image(logo)
    selected = option_menu (None, ['HOME','V3','BUS • TRAM • BAT3'], 
                            icons= ['🚲', '🚌🚃⛴️'],
                            menu_icon="🚲🚌🚃⛴️")

if selected == 'HOME':
    # Load the image
    image = Image.open('./Logo_aPlusDansLeBus.png')

    # Create columns
    col1, col2, col3 = st.columns([1,6,1])

    # Display the image in the center column
    with col2:
        st.image(image, use_column_width=True)


    # Display the image in the center of the page
    st.markdown(
        f'<div style="display: flex; justify-content: center;"><img src="temp.png" width="500"></div>',
        unsafe_allow_html=True,
    )

elif selected == 'V3':
    
    st.markdown("<h1 style='color: black;'>Respiration V3 (14 jours)</h1>", unsafe_allow_html=True)
    # Code for first page goes here
    video_file = open('./output.mp4', 'rb')
    video_bytes = video_file.read()

    st.video(video_bytes)
    @st.cache_data
    def load_data():
        # Load the data from the CSV file.
        data = pd.read_csv("./station_vCube_10.csv")
    
        # Convert 'mdate' to datetime.
        data['mdate'] = pd.to_datetime(data['mdate'])  # Convert to datetime
    
        # Extract time in the format HH:mm
        data['time'] = data['mdate'].dt.strftime('%H:%M')
    
        # Format date in French using Babel
        data['formatted_date'] = data['mdate'].apply(lambda x: format_date(x, 'EEEE d MMMM y', locale='fr'))
    
        return data


    
    #@st.cache_data
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
    st.markdown("<h1 style='color: black;'>Selectionnez une respiration V3 :</h1>", unsafe_allow_html=True)
    # Date Selectbox
    date_format_mapping = pd.Series(data.formatted_date.values,index=data.mdate.dt.date).to_dict()
    unique_dates = sorted(date_format_mapping.items())[1:]  # Skip the first date
    selected_date = st.selectbox('Selectionnez une date :', unique_dates, format_func=lambda x: x[1] if x != 'Selectionnez une date..' else x)

    # Time Selectbox
    unique_times = sorted(data['time'].unique())
    selected_time = st.selectbox('Selectionnez une heure :', options=unique_times)

    # Define tile options
    tiles_options = ['CartoDB dark_matter', 'Stamen Toner', 'OpenStreetMap']
    tiles_mapping = {
        'CartoDB dark_matter': 'CartoDB dark_matter',
        'Stamen Toner': 'Stamen Toner',
        'OpenStreetMap': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    }

    # Choose tile based on time
    if '06:20' <= selected_time < '21:40':
        selected_tile = 'Stamen Toner'
    else:
        selected_tile = 'CartoDB dark_matter'

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

    st.markdown("<h1 style='text-align: center; color: black;'>DashBoard V3</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div style="width: 1000px; height: 650px; overflow: hidden; position: relative;">
            <iframe 
                title="V3" 
                width="980" 
                height="600" 
                src="https://app.powerbi.com/reportEmbed?reportId=a5a6fa02-137c-48ca-9754-8467b7366089&autoAuth=true&ctid=5892e2db-e39d-4cc1-a179-dc66550efc30" 
                frameborder="0" 
                allowfullscreen
                style="position: absolute;">
            </iframe>
        </div>
    """, unsafe_allow_html=True)

elif selected == 'BUS • TRAM • BAT3':
    st.markdown("<h1 style='color: black;'>Réseau TRAM • BUS • BAT3</h1>", unsafe_allow_html=True)
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

    vehicle_type = st.radio('',['ALL', '🚃TRAM', '🚌BUS', '⛴️BATEAU'])
    show_retard = st.checkbox('RETARD') 

    vehicle_dict = {'🚃TRAM': 'TRAM', '🚌BUS': 'BUS', '⛴️BATEAU': 'BATEAU'}
    if vehicle_type != 'ALL':
        gdf = gdf[gdf['vehicule'] == vehicle_dict[vehicle_type]]

    m = folium.Map(location=[44.841424, -0.570334], tiles='Stamen Toner', zoom_start=13)

    lines = ['Tram B','Tram C','Tram A','Tram D','Lianes 1', 'Lianes 2', 'Lianes 3', 'Lianes 4', 'Lianes 5', 'Lianes 9', 'Lianes 10', 'Lianes 11', 'Lianes 15', 'Lianes 16', 'BAT3']
    palette = sns.color_palette('husl', len(lines)).as_hex()
    color_dict = dict(zip(lines, palette))

    emoji_dict = {'TRAM': u'\U0001F68B', 'BUS': u'\U0001F68C', 'BATEAU': u'\U0001F6A2'}

    n = 20000

    for index, row in gdf.iterrows():
        if show_retard and row['retard'] > 100:
            line_color = 'red'
            line_weight = 20
        else:
            line_color = color_dict.get(row['ligne_com'], 'white')
            line_weight = 2.5
        line_emoji = emoji_dict.get(row['vehicule'], '')
    
        retard_moyen_minutes = row['retard'] / 60  # Convert seconds to minutes
    
        popup_text = f"""
        <div style="font-size:12px; padding:10px; background-color: #F8F9F9; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.25); min-width: 300px;">
        <h4 style="color:{line_color};margin-bottom:10px">{row['ligne_com']}</h4>
        <p style="margin-bottom:5px"><b>Terminus:</b> {row['libelle']}</p>
        <p style="margin-bottom:5px"><b>Vehicule:</b> {line_emoji} {row['vehicule']}</p>
        <p style="margin-bottom:5px"><b>Retard Moyen:</b> {retard_moyen_minutes:.2f} minutes</p>
        <p style="margin-bottom:5px"><b>Vitesse Moyenne (km/h):</b> {row['vitesse']}</p>
        <p style="margin-bottom:5px"><b>Nombre de véhicule/ligne:</b> {row['nb_vehicule']}</p>
        </div>
        """
        popup = folium.Popup(popup_text, max_width=300)  # Adjust the max_width as required
    
        if row['geometry'].geom_type == 'MultiLineString':
            for line in row['geometry'].geoms:
                line_coords = [(y, x) for x, y in list(line.coords)]
                for i in range(0, len(line_coords), n):
                    icon_html = f'<div style="font-size: 12pt;">{line_emoji}</div>'
                    icon = folium.DivIcon(html=icon_html)
                    folium.Marker(line_coords[i], icon=icon).add_to(m)
    
                folium.PolyLine(line_coords, color=line_color, weight=2.5, opacity=1).add_child(folium.Popup(popup_text)).add_to(m)
    
        elif row['geometry'].geom_type == 'LineString':
            line_coords = [(y, x) for x, y in list(row['geometry'].coords)]
            for i in range(0, len(line_coords), n):
                icon_html = f'<div style="font-size: 12pt;">{line_emoji}</div>'
                icon = folium.DivIcon(html=icon_html)
                folium.Marker(line_coords[i], icon=icon).add_to(m)
            folium.PolyLine(line_coords, color=line_color, weight=2.5, opacity=1).add_child(folium.Popup(popup_text)).add_to(m)
    
    folium_static(m, width=945, height=450)
    st.markdown("<h1 style='text-align: center; color: black;'>DashBoard TRAM • BUS • BAT3</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div style="width: 1000px; height: 1200px; overflow: hidden; position: relative;">
            <iframe 
                title="TRAM • BUS • BATEAU" 
                width="945" 
                height="2000" 
                src="https://app.powerbi.com/reportEmbed?reportId=7f601950-66d2-4060-840b-21740784a6dc&autoAuth=true&ctid=5892e2db-e39d-4cc1-a179-dc66550efc30" 
                frameborder="0" 
                allowfullscreen
                style="position: absolute;">
            </iframe>
        </div>
    """, unsafe_allow_html=True)