"""
Main application file for the GHG Emissions Dashboard.
Handles navigation, session state, and page routing.
"""

import streamlit as st
import plotly.io as pio
from data_loader import preload_all_data
from utils import get_ghg_map_sidebar, get_country_sidebar, get_sector_sidebar
from views.ghg_map import render_ghg_map_page
from views.emissions_trends import render_emissions_trends_page
from views.sector_distribution import render_sector_distribution_page
from views.climate_impact import render_climate_impact_page
from views.data_view import render_data_view_page

# Set page configuration
st.set_page_config(
    page_title="GHG Emissions Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Increase plotly performance
pio.renderers.default = "browser" 

# Trigger pre-loading immediately when app starts
if 'preloaded_data' not in st.session_state:
    with st.spinner("Loading dashboard data... Please wait"):
        st.session_state.preloaded_data = preload_all_data()

# Initialize session state for current page
if "current_page" not in st.session_state:
    st.session_state.current_page = "GHG Map"

# Top Navigation Bar
st.markdown("### 🌍 GHG Emissions Dashboard")

# Create navigation columns
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🗺️ GHG Map", use_container_width=True):
        st.session_state.current_page = "GHG Map"

with col2:
    if st.button("📈 Emissions Trends", use_container_width=True):
        st.session_state.current_page = "Emissions Trends"

with col3:
    if st.button("🏭 Sector Distribution", use_container_width=True):
        st.session_state.current_page = "Sector Distribution"

with col4:
    if st.button("🌡️ Climate Impact", use_container_width=True):
        st.session_state.current_page = "Climate Impact"

with col5:
    if st.button("📊 Data View", use_container_width=True):
        st.session_state.current_page = "Data View"

st.markdown("---")


def main():
    """Main App Logic"""
    # Get current page from session state
    current_page = st.session_state.current_page
    
    # Load appropriate sidebar based on current page
    if current_page == "GHG Map":
        sidebar_data = get_ghg_map_sidebar()
        render_ghg_map_page(sidebar_data)
    elif current_page == "Emissions Trends":
        sidebar_data = get_country_sidebar("emissions_trends")
        render_emissions_trends_page(sidebar_data)
    elif current_page == "Sector Distribution":
        sidebar_data = get_sector_sidebar()
        render_sector_distribution_page(sidebar_data)
    elif current_page == "Climate Impact":
        sidebar_data = get_country_sidebar("climate_impact")
        render_climate_impact_page(sidebar_data)
    elif current_page == "Data View":
        sidebar_data = get_country_sidebar("data_view")
        render_data_view_page(sidebar_data)


# Run the app
if __name__ == "__main__":
    main()

# Footer
st.markdown("---")
st.markdown("Data source: National Greenhouse Gas Inventory Submissions")
