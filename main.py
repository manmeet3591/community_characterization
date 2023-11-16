import streamlit as st
import ee
import folium
from datetime import datetime, timedelta

# Initialize the Earth Engine module.
from streamlit_folium import folium_static

# Get the environment variable or default to an empty string
service_account_key_str = os.environ.get('GEE_SERVICE_ACCOUNT_KEY', '')


# Retrieve the service account key from Streamlit's secrets
service_account_key = st.secrets["GEE_SERVICE_ACCOUNT_KEY"]
# Use the service account for authentication
credentials = ee.ServiceAccountCredentials(email=service_account_key['client_email'], key_data=service_account_key['private_key'])
ee.Initialize(credentials)


# Function to compute NDBI
def compute_NDBI(image):
    ndbi = image.normalizedDifference(['SWIR1', 'NIR']).rename('NDBI')
    return image.addBands(ndbi)

# Function to load and process images
def load_process_images(start_date, end_date):
    # Filter Sentinel-2 imagery for the given date range and region (Nigeria in this case)
    collection = (ee.ImageCollection('COPERNICUS/S2')
                  .filterDate(start_date, end_date)
                  .filterBounds(ee.Geometry.Rectangle([2.676932, 4.27021, 14.680664, 13.892723]))
                  .map(compute_NDBI))

    # Process the image collection as needed (e.g., composite, median, etc.)
    processed_image = collection.median()

    return processed_image

# Function to display map
def display_map(image, zoom_start=6):
    map = folium.Map(location=[9.0820, 8.6753], zoom_start=zoom_start)  # Centered on Nigeria
    mapid = image.getMapId({'bands': ['NDBI'], 'min': -1, 'max': 1, 'palette': ['blue', 'white', 'red']})
    folium.TileLayer(tiles=mapid['tile_fetcher'].url_format, attr='Google Earth Engine').add_to(map)
    return map

# Streamlit UI
st.title("NDBI Analysis over Nigeria using Sentinel-2C Data")

# Sidebar for date selection
start_year = st.sidebar.selectbox("Select Start Year", list(range(2017, datetime.now().year)))
end_year = st.sidebar.selectbox("Select End Year", list(range(start_year, datetime.now().year + 1)))

# Compute NDBI and display map
if st.button('Show NDBI Map'):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 1, 1) - timedelta(days=1)
    image = load_process_images(start_date, end_date)
    st_folium_map = display_map(image)
    folium_static(st_folium_map)
