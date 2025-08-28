"""
Data loading functions for the GHG Emissions Dashboard.
Contains all data loading and caching functionality.
"""

import streamlit as st
import pandas as pd
import os
import glob
import json


@st.cache_data(max_entries=50) 
def load_country_data(country_code):
    """Load data for a specific country with hierarchy levels"""
    country_path = f"data/processed_data/{country_code}"
    data_dict = {
        'Total': None,
        'Sectors': None,
        'Subsectors': None,
        'Sub-subsectors': None
    }
    
    for level in data_dict.keys():
        level_path = os.path.join(country_path, level.lower())
        if os.path.exists(level_path):
            files = glob.glob(os.path.join(level_path, "*.parquet"))
            if files:
                data_dict[level] = pd.concat([pd.read_parquet(f) for f in files])
    
    return data_dict


@st.cache_data
def load_weather_data():
    """Load extreme weather events data"""
    try:
        weather_data = pd.read_parquet('data/EM-DATA/summary_extreme_weather_all_countries.parquet')
        return weather_data
    except:
        return None


@st.cache_data
def load_temperature_data():
    """Load global temperature anomaly data"""
    try:
        temp_data = pd.read_parquet('data/EM-DATA/global_temp_anomalies.parquet')
        return temp_data
    except:
        return None   


def load_global_emission():
    """Load global emissions data"""
    try:
        global_emissions = pd.read_parquet("data/EM-DATA/global_emissions.parquet")
        return global_emissions
    except:
        return None


def load_geojson():
    """Load the GeoJSON data for world countries"""
    try:
        with open('data/countries.geo.json') as f:
            geojson = json.load(f)
        return geojson
    except:
        return None


@st.cache_data
def load_all_total_emissions():
    """Load all countries' total emissions data"""
    all_country_folders = [
        name for name in os.listdir("data/processed_data")
        if os.path.isdir(os.path.join("data/processed_data", name))
    ]
    
    all_data = []
    for country_folder in all_country_folders:
        country_path = f"data/processed_data/{country_folder}/total"
        if os.path.exists(country_path):
            files = glob.glob(os.path.join(country_path, "*.parquet"))
            for f in files:
                df = pd.read_parquet(f)
                df = df[df['Year'] >= 1990]  
                df["Country"] = country_folder  # Keep track of country
                all_data.append(df)

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return None


def get_country_folders():
    """Get list of available country folders"""
    data_root = "data/processed_data"
    country_folders = sorted([
        name for name in os.listdir(data_root)
        if os.path.isdir(os.path.join(data_root, name))
    ])
    return country_folders


@st.cache_data
def preload_all_data():
    """Pre-load all data to trigger caching at startup"""
    data = {}
    
    # Get country labels
    country_labels = get_country_folders()
    
    # Load global datasets
    data['all_emissions'] = load_all_total_emissions()
    data['weather'] = load_weather_data()
    data['temperature'] = load_temperature_data()
    data['global_emissions'] = load_global_emission()
    data['geojson'] = load_geojson()
    
    # Pre-load data for all countries
    for country in country_labels:
        data[f'country_{country}'] = load_country_data(country)
    
    return data
