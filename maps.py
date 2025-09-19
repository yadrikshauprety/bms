import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

# ------------------- CONFIG -------------------
st.set_page_config(page_title="Nearby Clinics", page_icon="🏥", layout="wide")

st.title("🏥 Nearby Health Clinics")

# ------------------- USER INPUT -------------------
st.write("Find the nearest clinics and hospitals around you.")

# Default: Kathmandu coords (change if needed)
user_lat = st.number_input("Enter your Latitude:", value=27.7172, format="%.6f")
user_lon = st.number_input("Enter your Longitude:", value=85.3240, format="%.6f")

if st.button("🔍 Find Nearby Clinics"):
    with st.spinner("Fetching health centers near you..."):
        try:
            # Query Healthsites.io (Open API)
            url = f"https://healthsites.io/api/v1/healthsites?geometry=POINT({user_lon}%20{user_lat})&radius=5000"  
            # radius in meters → 5000m = 5km

            response = requests.get(url)
            data = response.json()

            # Initialize map
            m = folium.Map(location=[user_lat, user_lon], zoom_start=13)

            # Add user marker
            folium.Marker(
                [user_lat, user_lon],
                popup="📍 You are here",
                icon=folium.Icon(color="blue", icon="user")
            ).add_to(m)

            # Add clinics
            if "features" in data and len(data["features"]) > 0:
                for feature in data["features"]:
                    props = feature["properties"]
                    coords = feature["geometry"]["coordinates"]
                    lon, lat = coords[0], coords[1]

                    folium.Marker(
                        [lat, lon],
                        popup=f"🏥 {props.get('name', 'Unknown Clinic')}<br>Type: {props.get('amenity', 'N/A')}",
                        icon=folium.Icon(color="red", icon="plus-sign")
                    ).add_to(m)
            else:
                st.warning("No clinics found nearby. Try increasing the radius.")

            # Show map in Streamlit
            st_data = st_folium(m, width=700, height=500)

        except Exception as e:
            st.error(f"Error fetching clinics: {e}")
