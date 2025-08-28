"""
GHG Emissions Dashboard Package
A comprehensive Streamlit dashboard for analysing greenhouse gas emissions data.
"""

__version__ = "1.0.0"
__author__ = "Hodan Abdi"
__description__ = "Interactive dashboard for GHG emissions analysis and visualization"

from .data_loader import (
    load_country_data,
    load_weather_data,
    load_temperature_data,
    load_global_emission,
    load_geojson,
    load_all_total_emissions,
    get_country_folders,
    preload_all_data
)

from .utils import (
    get_ghg_map_sidebar,
    get_country_sidebar,
    get_sector_sidebar,
    get_co2_column,
    get_other_gas_columns,
    create_complete_map_figure
)

__all__ = [
    'load_country_data',
    'load_weather_data', 
    'load_temperature_data',
    'load_global_emission',
    'load_geojson',
    'load_all_total_emissions',
    'get_country_folders',
    'preload_all_data',
    'get_ghg_map_sidebar',
    'get_country_sidebar',
    'get_sector_sidebar',
    'get_co2_column',
    'get_other_gas_columns',
    'create_complete_map_figure'
]
