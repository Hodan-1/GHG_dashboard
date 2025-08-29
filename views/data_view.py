"""
Data View page for the GHG Emissions Dashboard.
Provides data exploration and download functionality.
"""

import streamlit as st
import pandas as pd
import os


def render_data_view_page(sidebar_data):
    """Render the Data View page
    Args:
        sidebar_data (dict): Dictionary containing:
            - total_emissions_df (pd.DataFrame): Total emissions data
            - data_dict (dict): Dictionary of sector-level data
            - year_range (tuple): Selected year range (start_year, end_year)
            - selected_country_folder (str): Currently selected country
            - selected_hierarchy (str): Selected sector hierarchy level
            - selected_sectors (list): List of selected sectors to display

    Returns:
        None - Renders content directly to Streamlit page
    """
    # Get required data
    selected_country_folder = sidebar_data['selected_country_folder']
    year_range = sidebar_data['year_range']
    
    # page header and description
    st.header("Data Explorer & Download")
    st.markdown("Browse and download datasets including GHG emissions, gas species, temperature anomalies, and extreme weather events.")

    # root directory
    data_root = "data/processed_data"
    
    dataset_options = {
        "Total Emissions": os.path.join(data_root, selected_country_folder, "total", f"{selected_country_folder}_total_combined.parquet"),
        "Sector Emissions": os.path.join(data_root, selected_country_folder, "sectors", f"{selected_country_folder}_sectors_combined.parquet"),
        "Subsector Emissions": os.path.join(data_root, selected_country_folder, "subsectors", f"{selected_country_folder}_subsectors_combined.parquet"),
        "Sub-subsector Emissions": os.path.join(data_root, selected_country_folder, "sub_subsectors", f"{selected_country_folder}_sub_subsectors_combined.parquet"),
        "Extreme Weather": "data/climate/processed_/summary_extreme_weather_all_countries.parquet",
        "Temperature Anomalies": "data/climate/processed_/global_temp_anomalies.parquet",
        "Global Emissions": "data/climate/processed_/global_emissions.parquet"
    }

    
    # Add gas versions of each hierarchy level
    gas_species_folder = os.path.join(data_root, selected_country_folder)
    if os.path.exists(gas_species_folder):
        for gas_folder in os.listdir(gas_species_folder):
            gas_path = os.path.join(gas_species_folder, gas_folder)
            if not os.path.isdir(gas_path):
                continue

            gas = gas_folder.upper()
            for level in ["total", "sectors", "subsectors", "sub_subsectors"]:
                combined_file = os.path.join(gas_path, level, f"{selected_country_folder}_{level}_{gas.lower()}_combined.parquet")
                if os.path.exists(combined_file):
                    key = f"{gas} - {level.capitalize()} Emissions"
                    dataset_options[key] = combined_file

    selected_dataset_name = st.selectbox("Select a dataset to explore", list(dataset_options.keys()))
    dataset_path = dataset_options[selected_dataset_name]

    if os.path.exists(dataset_path):
        df = pd.read_parquet(dataset_path)

        if 'Year' in df.columns:
            years = sorted(df['Year'].dropna().unique())
            year_filter = st.slider("Filter by Year", min_value=int(min(years)), max_value=int(max(years)),
                                    value=(int(min(years)), int(max(years))))
            df = df[df['Year'].between(year_filter[0], year_filter[1])]

        st.write(f"Preview of **{selected_dataset_name}**")
        st.dataframe(df.head(100))

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=f"Download {selected_dataset_name} as CSV",
            data=csv,
            file_name=f"{selected_dataset_name.replace(' ', '_').lower()}.csv",
            mime='text/csv'
        )
    else:
        st.warning("Dataset not found.")

    st.markdown("---")
    st.subheader("Dataset Descriptions")
    
    # Add dataset descriptions
    descriptions = {
        "Total Emissions": "Complete greenhouse gas emissions data aggregated at the national level.",
        "Sector Emissions": "Emissions broken down by major economic sectors (Energy, Industry, Agriculture, etc.).",
        "Subsector Emissions": "More detailed breakdown within each major sector.",
        "Sub-subsector Emissions": "Most granular level of sectoral breakdown available.",
        "Extreme Weather": "Records of extreme weather events including deaths, affected populations, and economic damages.",
        "Temperature Anomalies": "Global temperature deviations from the 20th century average (1951-1980 baseline).",
        "Global Emissions": "Global Emissions from Our World in Data."
    }
    
    # Display expandable sections in description
    for dataset_name, description in descriptions.items():
        if dataset_name in dataset_options:
            with st.expander(f" {dataset_name}"):
                st.write(description)
                if dataset_name in ["Total Emissions", "Sector Emissions", "Subsector Emissions", "Sub-subsector Emissions"]:
                    st.write(f"**Country**: {selected_country_folder}")
                    st.write("**Source**: UNFCCC National Inventory Submissions")
                elif dataset_name == "Extreme Weather":
                    st.write("**Source**: EM-DAT International Disaster Database")
                elif dataset_name == "Temperature Anomalies":
                    st.write("**Source**: Global temperature records")
