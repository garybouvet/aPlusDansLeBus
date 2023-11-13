#-----------------------------------------------------#
#                      Imports                        #
#-----------------------------------------------------#

import streamlit as st
import pandas as pd
from PIL import Image
import folium
from streamlit_folium import folium_static
import seaborn as sns
import geopandas as gpd
from babel.dates import format_date
from streamlit_option_menu import option_menu  # For creating a custom option menu


#-----------------------------------------------------#
#                   Page Configuration                #
#-----------------------------------------------------#

# Setting the page configuration with a title, icon and layout
st.set_page_config(
    page_title="TBM : un diaporama du réseau",
    page_icon="🚲🚌🚃⛴️",
    layout="wide",
)

#-----------------------------------------------------#
#                   Global Variables                  #
#-----------------------------------------------------#

# Defining the tile URL for the map
new_tile = "https://api.maptiler.com/maps/openstreetmap/{z}/{x}/{y}.jpg?key=f3oINQCFQ6bcHd6xbwMB"
# Loading the logo image from file
logo = Image.open('./Logo2_aPlusDansLeBus.png')

#-----------------------------------------------------#
#                     Functions                       #
#-----------------------------------------------------#

def convert_to_linestring(multilinestring):
    """Convert MultiLineString to LineString"""
    # Checking the geometry type and converting if it's a MultiLineString
    if multilinestring.geom_type == 'LineString':
        return multilinestring
    elif multilinestring.geom_type == 'MultiLineString':
        return multilinestring.geoms[0]



@st.cache_data(show_spinner=False)
def load_data_and_create_geodataframe():
    """Load data and create a GeoDataFrame"""
    # Reading CSV file and converting the 'geometry' column to a GeoSeries
    df = pd.read_csv("./gdfbustrambat.csv")
    gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['geometry']))
    return gdf

@st.cache_data(show_spinner=False)
def load_v3_data():
    """Load V3 data"""
    # Loading data from CSV, converting 'mdate' to datetime and formatting the date and time
    data = pd.read_csv("./station_vCube_10.csv")
    data['mdate'] = pd.to_datetime(data['mdate'])
    data['time'] = data['mdate'].dt.strftime('%H:%M')
    data['formatted_date'] = data['mdate'].apply(lambda x: format_date(x, 'EEEE d MMMM y', locale='fr'))
    return data

def create_v3_map(filtered_data, selected_tile):
    """Create V3 map"""
    # Creating a folium map with specified location, zoom and tile style
    m = folium.Map(
        location=[44.8378, -0.5792],
        zoom_start=13,
        tiles=selected_tile,
        attr='Map data © OpenStreetMap contributors'
    )
    # Iterating through the filtered data to add markers to the map
    for index, row in filtered_data.iterrows():
        # Extracting information from the current row
        nom = row['nom']  # Station name
        nbvelos = row['nbvelos']  # Number of bikes available
        latitude = row['latitude']  # Latitude of the station
        longitude = row['longitude']  # Longitude of the station
        etat = row['etat']  # Status of the station
        nbelec = row['nbelec']  # Number of electric bikes
        nbclassiq = row['nbclassiq']  # Number of classic bikes
        nbplaces = row['nbplaces']  # Number of available places

        # Determining the color based on the status of the station
        if etat == 'CONNECTEE':
            color = '#E37222'
        elif etat == 'MAINTENANCE':
            color = '#0A8A9F'
        elif etat == 'DECONNECTEE':
            color = 'red'

        # Setting the radius of the marker based on the number of bikes available
        radius = nbvelos * 1.5

        # Determining whether to fill the marker based on the selected tile
        fill = True if selected_tile in ['Stamen Toner', 'OpenStreetMap'] else False
        fill_color = color if fill else None

        # Creating a string for the popup text
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
        popup = folium.Popup(popup_text, max_width=250)  # Creating a popup with the text

        # Creating a marker and adding it to the map
        marker = folium.CircleMarker(
            location=[latitude, longitude], 
            color=color, 
            fill=fill, 
            fill_color=fill_color,
            radius=radius,
            weight=1,
            popup=popup  # Adding the popup to the marker
        )
        marker.add_to(m)  # Adding the marker to the map

    return m  # Returning the map object


#-----------------------------------------------------#
#                 Data Preparation                    #
#-----------------------------------------------------#

# Loading data and converting geometry column
gdf = load_data_and_create_geodataframe()
gdf['geometry'] = gdf['geometry'].apply(convert_to_linestring)

#-----------------------------------------------------#
#                       Sidebar                       #
#-----------------------------------------------------#

# Creating a sidebar with the logo and a radio button for page selection
with st.sidebar:
    st.image(logo, use_column_width=True)
    selected = option_menu(None, ['HOME', 'V3', 'BUS • TRAM • BAT3'],
                           icons=['house', 'bicycle', 'geo-alt'], 
                           menu_icon="cast", default_index=0)

#-----------------------------------------------------#
#                        Pages                        #
#-----------------------------------------------------#

# Checking the selected page and rendering content accordingly
if selected == 'HOME':
    # Loading and displaying an image for the HOME page
    image = Image.open('./Logo_aPlusDansLeBus.png')
    # Creating columns and displaying the image in the middle column
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.image(image, use_column_width=True)

# Option V3
elif selected == 'V3':
    
    st.markdown("<h1 style='color: black;'>Respiration V3 (14 jours)</h1>", unsafe_allow_html=True)
    # Code for first page goes here
    video_file = open('./output.mp4', 'rb')
    video_bytes = video_file.read()

    st.video(video_bytes)

    # Loading V3 data and creating selections for date and time
    data = load_v3_data()
    st.markdown("<h1 style='color: black;'>Selectionnez une respiration V3 :</h1>", unsafe_allow_html=True)
    date_format_mapping = pd.Series(data.formatted_date.values,index=data.mdate.dt.date).to_dict()
    unique_dates = sorted(date_format_mapping.items())[1:]
    selected_date = st.selectbox('Selectionnez une date :', unique_dates, format_func=lambda x: x[1] if x != 'Selectionnez une date..' else x)
    unique_times = sorted(data['time'].unique())
    selected_time = st.selectbox('Selectionnez une heure :', options=unique_times)

    # Checking the selected time to decide the tile style for the map
    if '06:20' <= selected_time < '21:40':
        selected_tile = new_tile
    else:
        selected_tile = 'CartoDB dark_matter'

    # Filtering data based on selected date and time and creating a map
    filtered_data = data[(data['mdate'].dt.date == selected_date[0]) & (data['time'] == selected_time)] if selected_date != 'Selectionnez une date..' else pd.DataFrame()
    m = create_v3_map(filtered_data, selected_tile)
    # Displaying the map and a dashboard
    folium_static(m, width=945, height=450)
    st.markdown("<h1 style='text-align: center; color: black;'>DashBoard V3</h1>", unsafe_allow_html=True)
    st.markdown(
        """
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
        """, unsafe_allow_html=True,
    )


elif selected == 'BUS • TRAM • BAT3':

    #-----------------------------------------------------#
    #             Header for BUS TRAM BAT3 Page           #
    #-----------------------------------------------------#
    st.markdown("<h1 style='color: black;'>Réseau TRAM • BUS • BAT3</h1>", unsafe_allow_html=True)
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
    
    #-----------------------------------------------------#
    #             Vehicle Type and Delay Toggle           #
    #-----------------------------------------------------#
    # Setting up a radio button for vehicle type selection and a checkbox for showing delays
    vehicle_type = st.radio('', ['ALL', '🚃TRAM', '🚌BUS', '⛴️BATEAU'])
    show_retard = st.checkbox('RETARD')

    # Mapping emoji to vehicle type
    vehicle_dict = {'🚃TRAM': 'TRAM', '🚌BUS': 'BUS', '⛴️BATEAU': 'BATEAU'}
    if vehicle_type != 'ALL':
        gdf = gdf[gdf['vehicule'] == vehicle_dict[vehicle_type]]  # Filtering the data based on selected vehicle type

    #-----------------------------------------------------#
    #                  Map Initialization                 #
    #-----------------------------------------------------#
    # Initializing a map with specified location, zoom, tile style, and attribution
    m = folium.Map(
        location=[44.841424, -0.570334],
        tiles=new_tile,
        zoom_start=13,
        attr='Map data © OpenStreetMap contributors'
    )

    #-----------------------------------------------------#
    #                   Line Color Setup                  #
    #-----------------------------------------------------#
    # Defining the lines and their color palette
    lines = ['Tram B', 'Tram C', 'Tram A', 'Tram D', 'Lianes 1', 'Lianes 2', 'Lianes 3', 'Lianes 4', 'Lianes 5', 'Lianes 9', 'Lianes 10', 'Lianes 11', 'Lianes 15', 'Lianes 16', 'BAT3']
    palette = sns.color_palette('husl', len(lines)).as_hex()
    color_dict = dict(zip(lines, palette))  # Mapping line names to colors

    emoji_dict = {'TRAM': u'\U0001F68B', 'BUS': u'\U0001F68C', 'BATEAU': u'\U0001F6A2'}  # Mapping vehicle types to emojis

    n = 20000  # Step size for placing vehicle icons along the lines

    #-----------------------------------------------------#
    #              Map Markers and Polylines              #
    #-----------------------------------------------------#
    # Iterating through the GeoDataFrame to add markers and polylines to the map
    for index, row in gdf.iterrows():
        # Setting color and weight based on delay
        if show_retard and row['retard'] > 100:
            line_color = 'red'
            line_weight = 20
        else:
            line_color = color_dict.get(row['ligne_com'], 'white')
            line_weight = 2.5

        line_emoji = emoji_dict.get(row['vehicule'], '')  # Getting the emoji for the vehicle type
        retard_moyen_minutes = row['retard'] / 60  # Convert seconds to minutes for display

        # Creating a popup text with vehicle and line information
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
        popup = folium.Popup(popup_text, max_width=300)  # Creating a popup with the text

        # Checking the geometry type and adding markers and polylines accordingly
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

    # Displaying the map
    folium_static(m, width=945, height=450)

    #-----------------------------------------------------#
    #                 Dashboard Display                   #
    #-----------------------------------------------------#
    st.markdown("<h1 style='text-align: center; color: black;'>DashBoard TRAM • BUS • BAT3</h1>", unsafe_allow_html=True)
    st.markdown(
        """
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
        """, unsafe_allow_html=True
    )
