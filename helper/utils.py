"""
Utility functions for the GHG Emissions Dashboard.
Contains sidebar functions and other utility functions.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from helper.data_loader import get_country_folders


def get_ghg_map_sidebar():
    """Sidebar for GHG Map page - only year range"""
    sidebar_data = {'year_range': None}
    
    # Load all emissions data to get year range
    all_emissions_df = st.session_state.preloaded_data['all_emissions']
    if all_emissions_df is not None:
        years = sorted(all_emissions_df['Year'].unique())
        sidebar_data['year_range'] = st.sidebar.slider(
            "Select Year Range",
            min_value=min(years),
            max_value=max(years),
            value=(min(years), max(years)),
            key="ghg_map_year_range"
        )
    
    return sidebar_data


def get_country_sidebar(page_key):
    """Generic sidebar for pages that need country + year range"""
    sidebar_data = {
        'selected_country_folder': None,
        'year_range': None,
        'data_dict': None,
        'total_emissions_df': None,
    }

    # Get country labels
    country_labels = get_country_folders()

    # Country selector
    selected_label = st.sidebar.selectbox(
        "Select Country",
        options=country_labels,
        key=f"{page_key}_country_selector"
    )
    
    sidebar_data['selected_country_folder'] = selected_label

    # Use pre-loaded data instead of loading fresh
    sidebar_data['data_dict'] = st.session_state.preloaded_data[f'country_{selected_label}']
    total_df = sidebar_data['data_dict']['Total']
    sidebar_data['total_emissions_df'] = total_df

    # Year slider
    years = sorted(total_df['Year'].unique())
    sidebar_data['year_range'] = st.sidebar.slider(
        "Select Year Range",
        min_value=min(years),
        max_value=max(years),
        value=(min(years), max(years)),
        key=f"{page_key}_year_range"
    )

    return sidebar_data


def get_sector_sidebar():
    """Sidebar for Sector Distribution page - country + year range + hierarchy"""
    sidebar_data = get_country_sidebar("sector_distribution")
    
    # Add hierarchy level selector
    hierarchy_options = ['Sectors', 'Subsectors', 'Sub-subsectors']  
    sidebar_data['selected_hierarchy'] = st.sidebar.radio(
        "Select Detail Level",
        options=hierarchy_options,
        key="sector_hierarchy"
    )
    # Add sector selection to sidebar
    sector_df = sidebar_data['data_dict'].get(sidebar_data['selected_hierarchy'])
    if sector_df is not None:
        available_sectors = sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].unique()
        sidebar_data['selected_sectors'] = st.sidebar.multiselect(
            "Select Sectors",
            options=available_sectors,
            default=available_sectors,
            key="sector_selection"
        )
    else:
        sidebar_data['selected_sectors'] = []

    return sidebar_data


# Gas column helper functions
def get_co2_column(df):
    """Get the CO2 column name from dataframe"""
    co2_columns = [col for col in df.columns if 'CO₂' in col]
    return co2_columns[0] if co2_columns else None


def get_other_gas_columns(df):
    """Get non-CO2 gas columns from dataframe"""
    return [col for col in df.columns if any(gas in col for gas in ['CH₄', 'N₂O', 'SF₆', 'HFCs', 'PFCs'])]


@st.cache_data(max_entries=50, ttl=3600)
def create_complete_map_figure(all_emissions_df, year_range, geojson):
    """Create and cache the complete map figure with frames"""
    frames = []
    co2_column = get_co2_column(all_emissions_df)
    
    years = range(year_range[0], year_range[1] + 1)
    
    # Create frames
    for year in years:
        year_data = all_emissions_df[all_emissions_df['Year'] == year]
        if not year_data.empty:
            emissions_df = year_data.groupby('Country')[co2_column].sum().reset_index()
            
            frame = go.Frame(
                data=[go.Choropleth(
                    locations=emissions_df['Country'],
                    z=emissions_df[co2_column],
                    geojson=geojson,
                    featureidkey="properties.name",
                    colorscale="YlOrRd",
                    zmin=0,
                    zmax=emissions_df[co2_column].max(),
                    colorbar=dict(title="CO\u2082 Emissions (kt)"),
                    hovertemplate="<b>%{location}</b><br>CO\u2082: %{z:,.0f} kt<extra></extra>"
                )],
                name=str(year)
            )
            frames.append(frame)
    
    # Create the complete figure
    fig = go.Figure()
    fig.add_trace(go.Choropleth(
        locations=frames[0].data[0].locations,
        z=frames[0].data[0].z,
        geojson=geojson,
        featureidkey="properties.name",
        colorscale="YlOrRd",
        zmin=0,
        zmax=max([frame.data[0].z.max() for frame in frames]),
        colorbar=dict(
            title="CO\u2082 Emissions (kt)",
            thickness=15,
            len=0.5
        ),
        hovertemplate="<b>%{location}</b><br>" +
                    "CO\u2082 Emissions: %{z:,.2f} kt<br>" +
                    "<i>Click for more information</i><extra></extra>"
    ))
    
    # Add layout
    fig.update_layout(
        title=f"Global CO\u2082 Emissions by Country ({year_range[0]}-{year_range[1]})",
        margin={"r":0,"t":40,"l":0,"b":0},
        geo=dict(
            showframe=False,
            showcountries=True,
            showcoastlines=True,
            countrycolor="Black",
            showocean=True,
            oceancolor="LightBlue",
            projection_type="natural earth"
        ),
        updatemenus=[{
            'buttons': [
                {
                    'args': [None, {'frame': {'duration': 500, 'redraw': True},
                                'fromcurrent': True}],
                    'label': 'Play',
                    'method': 'animate'
                },
                {
                    'args': [[None], {'frame': {'duration': 0, 'redraw': True},
                                    'mode': 'immediate',
                                    'transition': {'duration': 0}}],
                    'label': 'Pause',
                    'method': 'animate'
                }
            ],
            'direction': 'left',
            'pad': {'r': 10, 't': 87},
            'showactive': False,
            'type': 'buttons',
            'x': 0.1,
            'xanchor': 'right',
            'y': 0,
            'yanchor': 'top'
        }],
        sliders=[{
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 20},
                'prefix': 'Year:',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 300, 'easing': 'cubic-in-out'},
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.1,
            'y': 0,
            'steps': [
                {
                    'args': [[f'{year}'],
                            {'frame': {'duration': 300, 'redraw': True},
                            'mode': 'immediate',
                            'transition': {'duration': 300}}],
                    'label': f'{year}',
                    'method': 'animate'
                } for year in years
            ]
        }]
    )
    
    # Add frames to figure
    fig.frames = frames
    
    return fig
