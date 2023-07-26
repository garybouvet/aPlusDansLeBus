import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta
import locale

# Set locale to French
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

# Load the data from the CSV file.
data = pd.read_csv("/Users/garybouvet/Desktop/PROJET_DATA_3/Gary_all_data/station_vCube_10.csv")

# Convert 'mdate' to datetime.
data['mdate'] = pd.to_datetime(data['mdate'])  # Convert to datetime

# Extract date and time in the format HH:mm
data['formatted_date'] = data['mdate'].dt.strftime('%A %d %B %Y') # This will give day in French, i.e., Lundi, Mardi, etc.
data['time'] = data['mdate'].dt.strftime('%H:%M')

# Date Selectbox
date_format_mapping = pd.Series(data.formatted_date.values,index=data.mdate.dt.date).to_dict()
unique_dates = sorted(date_format_mapping.items())
selected_date = st.selectbox('Select a date', ['Selectionnez une date..'] + unique_dates, format_func=lambda x: x[1] if x != 'Selectionnez une date..' else x)

# Time Selectbox
unique_times = sorted(data['time'].unique())
selected_time = st.selectbox('Select a time', options=unique_times)

# Filter data based on the selected date and time.
filtered_data = data[(data['mdate'].dt.date == selected_date[0]) & (data['time'] == selected_time)] if selected_date != 'Selectionnez une date..' else pd.DataFrame()

# Create a basic map.
m = folium.Map(location=[44.8378, -0.5792], zoom_start=13, tiles="CartoDB dark_matter")

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
    else:
        color = 'gray'

    radius = nbvelos * 2

    marker = folium.CircleMarker(
        location=[latitude, longitude], 
        color=color, 
        fill=False, 
        radius=nbvelos,
        weight=1  # Set line thickness.
    )

    marker.add_to(m)

# Display it in Streamlit.
folium_static(m)
