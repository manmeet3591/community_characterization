import os
import ee
import streamlit as st
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta

# Initialize the Earth Engine module with credentials
service_account_key = st.secrets["GEE_SERVICE_ACCOUNT_KEY"]
credentials = ee.ServiceAccountCredentials(email=service_account_key['client_email'], key_data=service_account_key['private_key'])
ee.Initialize(credentials)

# Function to compute NDBI
def compute_NDBI(image):
    ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI')
    return image.addBands(ndbi)

# Function to load and process images for a given year
def load_process_images_for_year(year):
    start_date = datetime(year, 1, 1)
    end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    
    collection = (ee.ImageCollection('COPERNICUS/S2')
                  .filterDate(start_date, end_date)
                  .filterBounds(ee.Geometry.Rectangle([2.676932, 4.27021, 14.680664, 13.892723]))
                  .map(compute_NDBI))
    
    return collection.median()

# Function to display map
def display_map(image, zoom_start=6):
    map = folium.Map(location=[9.0820, 8.6753], zoom_start=zoom_start)
    mapid = image.getMapId({'bands': ['NDBI'], 'min': -1, 'max': 1, 'palette': ['blue', 'white', 'red']})
    folium.TileLayer(tiles=mapid['tile_fetcher'].url_format, attr='Google Earth Engine').add_to(map)
    return map

# Streamlit UI
st.title("Yearly NDBI Analysis over Nigeria using Sentinel-2C Data")

# Sidebar for year selection
start_year = st.sidebar.selectbox("Select Start Year", list(range(2017, datetime.now().year)), index=0)
end_year = st.sidebar.selectbox("Select End Year", list(range(2017, datetime.now().year + 1)), index=1)

# # Compute NDBI and display map
# if st.button('Show NDBI Map'):
#     # Loop through each year and compute average NDBI
#     for year in range(start_year, end_year + 1):
#         image = load_process_images_for_year(year)
#         st.write(f"NDBI for the year {year}")
#         st_folium_map = display_map(image)
#         folium_static(st_folium_map)

# import geemap.eefolium as geemap
import geemap
import ee

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colorbar import ColorbarBase
from io import BytesIO

def create_colorbar_image(min_val, max_val, colors, file_name='colorbar.png'):
    # Create a figure and a set of subplots
    fig, ax = plt.subplots(figsize=(6, 1))

    # Define the colormap and normalize
    cmap = mcolors.LinearSegmentedColormap.from_list("", colors)
    norm = mcolors.Normalize(vmin=min_val, vmax=max_val)

    # Create a colorbar
    cbar = ColorbarBase(ax, cmap=cmap, norm=norm, orientation='horizontal')

    # Save the colorbar to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)

    # Save the colorbar as an image file
    with open(file_name, 'wb') as f:
        f.write(buf.getvalue())

    plt.close(fig)



def display_ndbi_difference(year1, year2):
    # Load and process images for the specified years
    image1 = load_process_images_for_year(year1)
    image2 = load_process_images_for_year(year2)

    # Compute the difference and convert to percentage
    ndbi_diff = image2.subtract(image1).divide(image1).multiply(100)

    # Ensure ndbi_diff is a single-band image
    ndbi_diff = ndbi_diff.select('NDBI')  # Replace 'NDBI' with the correct band name if different

    # # Create an interactive map
    # Map = geemap.Map()
    # Map.addLayer(ndbi_diff, {'min': -100, 'max': 100, 'palette': ['blue', 'white', 'red'], 'opacity': 0.7}, 'NDBI Difference')
    
    # # Add colorbar
    # Map.add_colorbar(colors=['blue', 'white', 'red'], vmin=-100, vmax=100, caption='NDBI Difference (%)')

    # def display_ndbi_difference(year1, year2):
    # # ... [previous code] ...

    # Create an interactive map
    Map = geemap.Map(center=[9.0820, 8.6753], zoom=6) 
    Map.addLayer(ndbi_diff, {'min': -100, 'max': 100, 'palette': ['blue', 'white', 'red'], 'opacity': 0.7}, 'NDBI Difference')

# Add colorbar
    Map.add_colorbar_branca(colors=['blue', 'white', 'red'], vmin=-100, vmax=100, caption='NDBI Difference (%)')

    
    # # Add colorbar with a correct argument
    # Map.add_colorbar(cmap='coolwarm', vmin=-100, vmax=100, caption='NDBI Difference (%)')  # adjust cmap as needed

    # Display the map
    return Map

    # # Display the map
    # return Map

# In your Streamlit UI
if st.button('Show NDBI Difference Map'):
    # Assuming start_year and end_year are selected by the user
    Map = display_ndbi_difference(start_year, end_year)
    create_colorbar_image(-100, 100, ['blue', 'white', 'red'])

    # # Display the map
    # Map.to_streamlit()
    Map.to_streamlit()
    st.image('colorbar.png', caption='NDBI Difference (%)')

