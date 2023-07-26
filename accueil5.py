import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import locale

# Set wide mode
st.set_page_config(layout="wide")

video_file = open('/Users/garybouvet/Desktop/Streamlit_projet_3/output_acceléré.mp4', 'rb')
video_bytes = video_file.read()

st.video(video_bytes)

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

# Load the data from the CSV file.
data = pd.read_csv("/Users/garybouvet/Desktop/PROJET_DATA_3/Gary_all_data/station_vCube_10.csv")

# Convert 'mdate' to datetime.
data['mdate'] = pd.to_datetime(data['mdate'])  # Convert to datetime

# Extract date and time in the format HH:mm
data['formatted_date'] = data['mdate'].dt.strftime('%A %d %B %Y') # This will give day in French, i.e., Lundi, Mardi, etc.
data['time'] = data['mdate'].dt.strftime('%H:%M')

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

# Create a basic map.
m = folium.Map(location=[44.8378, -0.5792], zoom_start=13, tiles=tile_url, attr=tile_attr)

# Add markers for each station.
for index, row in filtered_data.iterrows():
    nom = row['nom']
    nbvelos = row['nbvelos']
    latitude = row['latitude']
    longitude = row['longitude']
    etat = row['etat']
    nbelec = row['nbelec']
    nbclassiq = row['nbclassiq']

    if etat == 'CONNECTEE':
        color = '#E37222'
    elif etat == 'MAINTENANCE':
        color = '#0A8A9F'
    elif etat == 'DECONNECTEE':
        color = 'red'

    radius = nbvelos * 1.5

    fill = True if selected_tile in ['Stamen Toner', 'OpenStreetMap'] else False
    #weight = 2 if selected_tile in ['Stamen Toner', 'OpenStreetMap'] else 1  # Set line thickness based on tile type.

    fill_color = color if fill else None

    marker = folium.CircleMarker(
        location=[latitude, longitude], 
        color=color, 
        fill=fill, 
        fill_color=fill_color,
        radius=radius,
        weight=1   #weight  # use the new weight variable here
    )
    marker.add_to(m)

m.get_root().html.add_child(folium.Element(legend_html))

# Display the dynamic map using folium_static
folium_static(m, width=945, height=450)
