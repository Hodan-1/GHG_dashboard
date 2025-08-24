import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
import folium
from streamlit_folium import st_folium
import statsmodels.api as sm  
import json
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="GHG Emissions Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)



# Increase cache size for better performance
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
        with open('countries.geo.json') as f:
            geojson = json.load(f)
        return geojson
    except:
        return None
    
@st.cache_data
def load_all_total_emissions():
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
# Increase plotly performance
import plotly.io as pio
pio.renderers.default = "browser" 

data_root = "data/processed_data"
country_folders = sorted([
    name for name in os.listdir(data_root)
    if os.path.isdir(os.path.join(data_root, name))
])

# Display uppercase in the sidebar
country_labels = [name for name in country_folders]

# Pre-load all data at app startup to trigger caching
@st.cache_data
def preload_all_data():
    """Pre-load all data to trigger caching at startup"""
    data = {}
    
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

# Dynamic Sidebar Functions
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

@st.cache_data(max_entries=50, ttl=3600)
def create_complete_map_figure(all_emissions_df, year_range, geojson):
    """Create and cache the complete map figure with frames"""
    frames = []
    co2_column = [col for col in all_emissions_df.columns if 'CO\u2082' in col][0]
    
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

def render_ghg_map_page(sidebar_data):
    """Enhanced GHG Map page with better storytelling"""
    
    # Enhanced header with context
    st.markdown("""
    ### Welcome to the Climate Reporting Journey

    This interactive map visualises carbon dioxide (CO₂) emissions over time for UNFCCC Annex I countries.  
    Explore how these nations have shaped global emissions since 1990, data submitted under the earliest international climate agreements, when the world first united under the UNFCCC to address climate change.
    """)

    
    # Add context about what users will discover
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ###  **What You'll Discover**
        - **Emission hotspots** and their evolution
        - **Success stories** of countries reducing emissions
        - **Impact of global events** (economic crises, pandemics)
        - **Policy effectiveness** across different nations
        """)
    
    with col2:
        st.markdown("""
        ###  **The Data Story**
        - **33+ years** of official climate reporting
        - **Annex I countries**: Developed nations with binding targets
        - **Standardized reporting** through UNFCCC protocols
        - **Real policy impacts** reflected in the numbers
        """)
    
    with col3:
        st.markdown("""
        - **Press Play** to watch emissions evolve over time
        - **Hover over countries** for detailed insights
        - **Spot the trends** - which countries are leading?
        - **Connect the dots** between events and emissions
        """)
    
    st.markdown("---")
    
    # Use pre-loaded data
    all_emissions_df = st.session_state.preloaded_data['all_emissions']
    geojson = st.session_state.preloaded_data['geojson']
    year_range = sidebar_data['year_range']

    if all_emissions_df is not None and geojson is not None:
        # Add some quick stats before the map
        co2_column = [col for col in all_emissions_df.columns if 'CO\u2082' in col][0]
        
        # Calculate interesting statistics
        total_emissions_latest = all_emissions_df[all_emissions_df['Year'] == year_range[1]][co2_column].sum()
        total_emissions_earliest = all_emissions_df[all_emissions_df['Year'] == year_range[0]][co2_column].sum()
        change_percent = ((total_emissions_latest - total_emissions_earliest) / total_emissions_earliest) * 100
        
        # Top emitters
        latest_year_data = all_emissions_df[all_emissions_df['Year'] == year_range[1]]
        top_emitters = latest_year_data.nlargest(3, co2_column)['Country'].tolist()
        
        # Quick insights box
        st.info(f"""
        **Quick Insights for {year_range[0]}-{year_range[1]}**:
        
        - **Total Change**: Annex I emissions have {'increased' if change_percent > 0 else 'decreased'} by **{abs(change_percent):.1f}%**
        - **Top 3 Emitters**: {', '.join(top_emitters)}
        - **Latest Total**: {total_emissions_latest:,.0f} kt CO₂ in {year_range[1]}
        - **Countries Tracked**: {len(latest_year_data)} Annex I nations
        """)
        
        # Use cached complete figure
        fig = create_complete_map_figure(all_emissions_df, year_range, geojson)
        
        st.plotly_chart(fig, use_container_width=True)
        st.caption(" Use the play button to see emissions evolve over time, or drag the slider to jump to specific years!")

        # Enhanced expandable section with more engaging content
        with st.expander("Understanding the Climate Data "):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                ####  **How is this data collected?**
                
                Since **1992**, countries have been required to report their greenhouse gas emissions annually. 
                This dashboard shows data from **Annex I countries** - the developed nations that took on 
                binding emission reduction targets under the Kyoto Protocol.
                
                **What makes this data special?**
                -  **Standardised methodology** across all countries
                -  **Independent verification** by international experts  
                -  **Policy-relevant** - directly used for climate negotiations
                -  **Comprehensive coverage** of all major emission sources
                """)
            
            with col2:
                st.markdown("""
                ####  **Why Annex I Countries Matter**
                
                These countries represent:
                - **~60% of historical emissions** since 1850
                - **Major economies** with significant climate policies
                - **Technology leaders** in clean energy innovation
                - **First movers** in carbon pricing and regulation
                
                **Key Milestones in This Data:**
                - **1997**: Kyoto Protocol signed
                - **2008-2012**: First Kyoto commitment period
                - **2015**: Paris Agreement adopted
                - **2020**: COVID-19 impact visible
                """)
        
        # Add a "What's Next" section
        st.markdown("### Want to find out more?")
        
        next_col1, next_col2, next_col3 = st.columns(3)
        
        with next_col1:
            st.markdown("""
            **📈 Emissions Trends**
            
            Dive deep into individual country stories. See how policies, 
            economic changes, and global events shaped emission trajectories.
            """)
        
        with next_col2:
            st.markdown("""
            **🏭 Sector Analysis**
            
            Discover which sectors drive emissions in each country. 
            Compare energy, transport, industry, and agriculture impacts.
            """)
        
        with next_col3:
            st.markdown("""
            **🌡️ Climate Impact**
            
            Connect emissions to real-world consequences. Explore the 
            relationship between emissions and extreme weather events.
            """)

    else:
        st.error("Required data not available")

def render_emissions_trends_page(sidebar_data):
    """Enhanced emissions trends page with visual storytelling"""
    
    # Access data
    total_emissions_df = sidebar_data['total_emissions_df']
    selected_country_folder = sidebar_data['selected_country_folder']
    year_range = sidebar_data['year_range']
    
    st.header(f"{selected_country_folder}'s Emissions Trends")
    st.write("Greenhouse gases (GHGs) differ in how they're produced and how strongly they warm the planet. "
    "In this section, you can explore how **total emissions have changed over time** for different gases, based on national inventories submitted via the **UNFCCC Common Reporting Tables (CRTs)**.")
    
    
    
    # Get gas columns
    co2_column = [col for col in total_emissions_df.columns if 'CO\u2082' in col][0]
    other_gas_columns = [col for col in total_emissions_df.columns if any(gas in col for gas in ['CH\u2084', 'N\u2082O', 'SF\u2086', 'HFCs', 'PFCs'])]
    
    # Filter data
    filtered_total_df = total_emissions_df[
        total_emissions_df['Year'].between(year_range[0], year_range[1])
    ].copy()
    
    # Calculate key metrics for storytelling
    latest_year = filtered_total_df['Year'].max()
    earliest_year = filtered_total_df['Year'].min()
    
    latest_co2 = filtered_total_df[filtered_total_df['Year'] == latest_year][co2_column].iloc[0]
    earliest_co2 = filtered_total_df[filtered_total_df['Year'] == earliest_year][co2_column].iloc[0]
    co2_change = ((latest_co2 - earliest_co2) / earliest_co2) * 100
    
    # Calculate trend
    z = np.polyfit(filtered_total_df['Year'], filtered_total_df[co2_column], 1)
    slope = z[0]
    
    
    
    if co2_change > 0:
        st.markdown(f"""
        <strong style="color: #ff6b6b;">🔥 Emissions have increased by {co2_change:.1f}%</strong> since {earliest_year}, 
        reaching <strong>{latest_co2:,.0f} kt</strong> in {latest_year}.
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <strong style="color: #4ecdc4;"> Emissions have decreased by {abs(co2_change):.1f}%</strong> since {earliest_year}, 
        dropping to <strong>{latest_co2:,.0f} kt</strong> in {latest_year}.
        """, unsafe_allow_html=True)
    
    st.markdown("</p></div>", unsafe_allow_html=True)
    
    # Key metrics dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Peak Emissions",
            value=f"{filtered_total_df[co2_column].max():,.0f} kt",
            delta=f"in {filtered_total_df.loc[filtered_total_df[co2_column].idxmax(), 'Year']}"
        )
    
    with col2:
        st.metric(
            label="Latest Emissions",
            value=f"{latest_co2:,.0f} kt",
            delta=f"{slope:+.0f} kt/year trend"
        )
    
    with col3:
        st.metric(
            label="Total Reduction",
            value=f"{co2_change:+.1f}%",
            delta="since 1990" if earliest_year == 1990 else f"since {earliest_year}"
        )
    
    with col4:
        # Calculate years to net-zero at current rate
        if slope < 0:
            years_to_zero = int(latest_co2 / abs(slope))
            st.metric(
                label="Years to Net-Zero",
                value=f"~{years_to_zero}",
                delta="at current rate"
            )
        else:
            st.metric(
                label="Trajectory",
                value="Increasing",
                delta="action needed"
            )
    
    # Enhanced emissions trends with annotations
    # First plot - CO2 Emissions
    st.subheader("CO\u2082 Emissions Over Time")
    st.markdown("""
    Carbon dioxide (**CO₂**) is the most significant greenhouse gas globally, primarily from **burning fossil fuels**, **industrial processes**, and **deforestation**.
    This line chart shows the trend in net CO₂ emissions (including removals where land-use changes absorb CO₂) across the selected time range.
    """)
    d1, d2 = st.tabs(["Graph", "Table"])
    with d1: # Create enhanced plot with annotations
        fig = go.Figure()
        
        # Add CO2 trend line
        fig.add_trace(go.Scatter(
            x=filtered_total_df['Year'],
            y=filtered_total_df[co2_column],
            mode='lines+markers',
            name='CO₂ Emissions',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=6)
        ))
        
        # Add trend line
        years_range = np.array(filtered_total_df['Year'])
        trend_line = z[0] * years_range + z[1]
        fig.add_trace(go.Scatter(
            x=years_range,
            y=trend_line,
            mode='lines',
            name='Trend',
            line=dict(color='red', dash='dash', width=2)
        ))
        
        # Add milestone annotations
        milestones = [
            (1997, "Kyoto Protocol", "↓"),
            (2015, "Paris Agreement", "↓"),
            (2020, "COVID Impact", "↓")
        ]
        
        for year, event, symbol in milestones:
            if year_range[0] <= year <= year_range[1]:
                year_data = filtered_total_df[filtered_total_df['Year'] == year]
                if not year_data.empty:
                    value = year_data[co2_column].iloc[0]
                    fig.add_annotation(
                        x=year,
                        y=value,
                        text=event,
                        showarrow=True,
                        arrowhead=2,
                        ax=0,
                        ay=-40,
                        bgcolor="rgba(255, 255, 255, 0.8)",
                        bordercolor="black",
                        borderwidth=1
                    )
        
        fig.update_layout(
            title={
                'text': f"CO₂ Emissions Journey: {selected_country_folder}",
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="Year",
            yaxis_title="CO₂ Emissions (kt)",
            hovermode='x unified',
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with d2:  
        st.subheader("CO\u2082 Emissions Data Table")
        co2_data = filtered_total_df[['Year', co2_column]]  
        st.dataframe(co2_data)
        
        csv_co2 = co2_data.to_csv(index=False)
        st.download_button(
            label="Download CO\u2082 Data as CSV",
            data=csv_co2,
            file_name=f'co2_emissions_{selected_country_folder}.csv',
            mime='text/csv',
            key='download_co2'
        )
    # Gas comparison section
    st.subheader(" Greenhouse Gas Portfolio")
    
    # Calculate percentages
    latest_data = filtered_total_df[filtered_total_df['Year'] == latest_year]
    total_emissions = latest_data[co2_column].iloc[0]
    
    gas_data = []
    for gas in [co2_column] + other_gas_columns:
        if gas in latest_data.columns:
            value = latest_data[gas].iloc[0]
            if value > 0:
                gas_data.append({
                    'Gas': gas.replace(' (kt)', ''),
                    'Emissions': value,
                    'Percentage': (value / total_emissions) * 100
                })
    
    gas_df = pd.DataFrame(gas_data)
    d3, d4 = st.tabs(["Graph", "Table"])
    with d3:
        # Create pie chart
        fig_pie = px.pie(
            gas_df,
            values='Emissions',
            names='Gas',
            title=f"Emission Portfolio - {latest_year}",
            color_discrete_map={
                'CO₂': '#1f77b4',
                'CH₄': '#ff7f0e',
                'N₂O': '#2ca02c',
                'SF₆': '#d62728',
                'HFCs': '#9467bd',
                'PFCs': '#8c564b'
            }
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)

    with d4:  
        st.subheader("Gas Portfolio Data Table")
        st.dataframe(gas_df)
        
        csv_gas_portfolio = gas_df.to_csv(index=False)
        st.download_button(
            label="Download Gas Portfolio Data as CSV",
            data=csv_gas_portfolio,
            file_name=f'gas_portfolio_{selected_country_folder}_{latest_year}.csv',
            mime='text/csv',
            key='download_gas_portfolio'
        )

        
    # Interactive gas explorer
    st.subheader(" Explore Individual Gases")
    
    # Gas selection for other gases
    selected_gases = st.multiselect(
        "Select Gases for Emissions Trends",
        options=[co2_column] + other_gas_columns,
        default=[co2_column]
    )
    
    d5, d6 = st.tabs(["Graph", "Table"])
    with d5:
        
        fig_gas = go.Figure()
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for i, gas in enumerate(selected_gases):
            if gas in filtered_total_df.columns:
                fig_gas.add_trace(go.Scatter(
                    x=filtered_total_df['Year'],
                    y=filtered_total_df[gas],
                    mode='lines+markers',
                    name=gas.replace(' (kt)', ''),
                    line=dict(width=3, color=colors[i % len(colors)])
                ))
        
        fig_gas.update_layout(
            title=f"Selected Gases Emissions Analysis",
            xaxis_title="Year",
            yaxis_title="Emissions (kt)",
            template='plotly_white'
        )
        
        st.plotly_chart(fig_gas, use_container_width=True)
    

    with d6:  
        st.subheader("Selected Gases Emissions Data")
        selected_gases_data = filtered_total_df[['Year'] + selected_gases]
        st.dataframe(selected_gases_data)
        
        csv_selected_gases = selected_gases_data.to_csv(index=False)
        st.download_button(
            label="Download Selected Gases Data as CSV",
            data=csv_selected_gases,
            file_name=f'selected_gases_{selected_country_folder}.csv',
            mime='text/csv',
            key='download_selected_gases'
        )
    
    st.markdown("**You selected the following gases.**  "
    "Expand the sections below to learn more about their sources and environmental impact."
    "For a more detailed breakdown by emission sectors (e.g. transport, energy, agriculture), see the **Sector Distribution** page.")

    st.markdown("#### Gas Information")

    if "CO\u2082 (kt)" in selected_gases:
        with st.expander("Carbon Dioxide (CO₂)"):
            st.markdown("""
            CO₂ is the most abundant human-emitted greenhouse gas. 
            It mainly comes from **fossil fuel combustion**, **deforestation**, and **Industrial Processes**.
            While less potent per molecule than other gases, it stays in the atmosphere for **hundreds of years**.

            **Info**: CO₂ accounts for over **75% of global GHG emissions**.
            """)

    if "CH\u2084 (kt)" in selected_gases:
        with st.expander(" Methane (CH₄)"):
            st.markdown("""
            Methane is a **short-lived climate pollutant**  over **25 times stronger than CO₂** over 100 years.
            It's mainly released by **livestock**, **landfills**, and **fossil fuel extraction**.
                            
            Methane breaks down faster than CO₂ but has a **much greater global warming potential** in the short term.
            """)

    if "N\u2082O (kt)" in selected_gases:
        with st.expander("Nitrous Oxide (N₂O)"):
            st.markdown("""
            N₂O has a **global warming potential ~300 times that of CO₂**.
            It is mostly emitted from **agricultural activities**, especially **fertiliser use**, as well as **wastewater** and **industry**.
            
            It also contributes to the **depletion of the ozone layer**.
            """)

    if "HFCs (kt)" in selected_gases:
        with st.expander(" Hydrofluorocarbons (HFCs)"):
            st.markdown("""
            HFCs are synthetic gases used in **air conditioning**, **refrigeration**, and **aerosol propellants**.
            Their warming potential ranges from **hundreds to thousands of times** stronger than CO₂.
            
            Many are being phased out under international agreements like the **Kigali Amendment**.
            """)

    if "PFCs (kt)" in selected_gases:
        with st.expander(" Perfluorocarbons (PFCs)"):
            st.markdown("""
            PFCs are emitted during **aluminium production** and **semiconductor manufacturing**.
            They are extremely long-lived, lasting **up to 50,000 years**.

            Though emissions are low, their **climate impact is significant** per molecule.
            """)

    if "SF\u2086 (kt)" in selected_gases:
        with st.expander(" Sulphur Hexafluoride (SF₆)"):
            st.markdown("""
            SF₆ is mainly used as an **insulating gas** in electrical systems.
            It is the **most potent greenhouse gas**, with a GWP more than **23,000 times greater than CO₂** over 100 years.

            Despite small quantities, its **impact is large** due to its strength and long atmospheric lifetime.
            """)
    
    
    # Download section
    st.subheader(" Download Your Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Prepare comprehensive dataset
        download_df = filtered_total_df.copy()
        download_df['Country'] = selected_country_folder
        
        csv = download_df.to_csv(index=False)
        st.download_button(
            label="Download Complete Dataset",
            data=csv,
            file_name=f"{selected_country_folder}_emissions_{year_range[0]}_{year_range[1]}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Create summary statistics
        summary_stats = {
            'Metric': ['Average Annual Emissions', 'Peak Emissions', 'Latest Emissions', 'Total Change', 'Annual Trend'],
            'CO₂ (kt)': [
                f"{filtered_total_df[co2_column].mean():,.0f}",
                f"{filtered_total_df[co2_column].max():,.0f}",
                f"{latest_co2:,.0f}",
                f"{co2_change:+.1f}%",
                f"{slope:+.0f}"
            ]
        }
        
        summary_df = pd.DataFrame(summary_stats)
        csv_summary = summary_df.to_csv(index=False)
        st.download_button(
            label="Download Summary Statistics",
            data=csv_summary,
            file_name=f"{selected_country_folder}_summary_stats.csv",
            mime="text/csv"
        )


def render_sector_distribution_page(sidebar_data):
    """Render the Sector Distribution page"""
    total_emissions_df = sidebar_data['total_emissions_df']
    data_dict = sidebar_data['data_dict']
    year_range = sidebar_data['year_range']
    selected_country_folder = sidebar_data['selected_country_folder']
    selected_hierarchy = sidebar_data['selected_hierarchy']
    selected_sectors = sidebar_data['selected_sectors']  

    st.header("Sector Distribution")
    st.write("Here, you can explore a detailed breakdown of greenhouse gas emissions by sector over time. Below the charts, you'll find an overview of the specific climate policies implemented in the selected country to address these emissions.")
    
    if total_emissions_df is not None:
        co2_column = [col for col in total_emissions_df.columns if 'CO\u2082' in col][0]
        other_gas_columns = [col for col in total_emissions_df.columns if any(gas in col for gas in ['CH\u2084', 'N\u2082O', 'SF\u2086', 'HFCs', 'PFCs'])]
        
        # Get sector data
        sector_df = data_dict.get(selected_hierarchy)
        
        if sector_df is not None:
            # Filter sector data
            filtered_sector_df = sector_df[
                (sector_df['Year'].between(year_range[0], year_range[1])) &
                (sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].isin(selected_sectors))
            ]
            
            # Chart explanations
            chart_explanations = {
                'United States': (
                    "The United States has a diverse economy where **energy and transportation** are major contributors "
                    "to greenhouse gas emissions. You'll likely see large $CO_2$ emissions from power generation and "
                    "road transport, reflecting the country's reliance on fossil fuels. "
                    "**Agriculture** is also a significant sector, and this is where you would see a notable distribution of **methane** emissions from livestock. "
                    "Like Australia, the 'Land Use' sector can sometimes show negative emissions because forests and "
                    "soil act as a **carbon sink**, absorbing more carbon than they release."
                ),
                'UK': (
                    "The UK has made significant progress in decarbonizing its **energy sector**, largely by phasing out coal (last coal plant closed in 2024). "
                    "The charts will show a decreasing share of emissions from this sector over time. "
                    "**Industrial processes** and transportation remain key areas, with policies like carbon pricing "
                    "influencing their emissions distribution. The 'Land Use' sector here also functions as a **carbon sink** due to "
                    "reforestation and sustainable land management."
                ),
                'Australia': (
                    "Australia's economy is heavily reliant on resource extraction and exports, especially coal. The "
                    "charts for Australia will show a high concentration of emissions in the **energy sector** due to "
                    "its coal-fired power plants. Like the US, Australia also has a large agricultural sector, "
                    "contributing significantly to **methane** emissions from livestock. "
                    "Notably, the 'Land Use, Land-Use Change, and Forestry' sector often has negative emissions, "
                    "meaning it acts as a **carbon sink** by absorbing more carbon than it releases, thanks to "
                    "reduced land clearing and reforestation efforts."
                ),
                'Ukraine': (
                    "Ukraine's emissions profile is shaped by its heavy industry and energy sectors. The data reflects "
                    "the country's industrial past, with a focus on decarbonization efforts as it aligns with EU standards. "
                    "The charts may show emissions from **heavy manufacturing and industrial processes**, with future "
                    "trends likely to show a shift towards greener energy sources."
                ),
                'Austria': (
                    "Austria is a leader in renewable energy, particularly with its vast **hydropower resources**. The charts will "
                    "reflect this, showing a much lower share of emissions from the energy sector compared to countries "
                    "that rely on fossil fuels. The emissions distribution will likely be more concentrated in "
                    "transport and industrial sectors. The extensive forests also make the 'Land Use' sector a significant **carbon sink**."
                )
            }

            # Gas explanations
            gas_explanations = {
                'CO\u2082 (kt)': (
                    "**Carbon Dioxide (CO\u2082)** is the primary greenhouse gas, mostly from the burning of fossil fuels "
                    "in the **energy sector** (power plants, transportation) and **industrial processes**."
                ),
                'CH\u2084 (kt)': (
                    "**Methane (CH\u2084 )** is a potent greenhouse gas, and its distribution is often concentrated "
                    "in the **agriculture sector** (from livestock and land use), and the **waste sector** (from landfills)."
                ),
                'N\u2082O (kt)': (
                    "**Nitrous Oxide (N\u2082O)** primarily comes from the **agriculture sector**, particularly from soil "
                    "management and fertilizer use. It can also be a byproduct of some industrial processes."
                ),
                'HFCs (kt)': (
                    "**Hydrofluorocarbons (HFCs)** are a type of F-gas. They are not naturally occurring and are primarily "
                    "used in industrial applications like refrigeration and air conditioning. In some cases, a specific "
                    "industry's emissions might be 100% HFCs."
                ),
                'PFCs (kt)': (
                    "**Perfluorocarbons (PFCs)** are potent F-gases. They are primarily a byproduct of industrial "
                    "processes, such as aluminum smelting and semiconductor manufacturing."
                ),
                'SF\u2086 (kt)': (
                    "**Sulfur Hexafluoride (SF\u2086)** is an extremely potent F-gas with a long atmospheric lifetime. It "
                    "is most commonly used as an electrical insulator in high-voltage equipment, which falls under "
                    "the **industrial processes** sector."
                ),
            }

            # Policy data
            policy_data = {
                'United States of America': {
                    'Sectors': {
                        'Energy': {
                            'description': 'The U.S. is heavily investing in clean energy to decarbonize its grid, primarily through the Inflation Reduction Act (IRA).',
                            'policies': [
                                'IRA Tax Credits: Generous tax credits for renewable energy projects (e.g., wind, solar) and technologies like carbon capture and storage (CCS).',
                                'State-level RPS: Many states have their own Renewable Portfolio Standards, mandating a percentage of electricity from renewable sources.',
                            ]
                        },
                        'Industrial Processes & Product Use': {
                            'description': 'Policy focuses on providing financial incentives for industrial decarbonization.',
                            'policies': [
                                'IRA Funding: The IRA provides billions in funding for industrial technologies and tax credits for clean hydrogen and CCS deployment.',
                                'AIM Act: The American Innovation and Manufacturing Act phases down the use of hydrofluorocarbons (HFCs), which are potent greenhouse gases.',
                            ]
                        },
                        'Agriculture, Forestry & Other Land Use': {
                            'description': 'Policies are aimed at supporting sustainable land management practices and reducing agricultural emissions.',
                            'policies': [
                                'IRA Conservation Programs: The IRA allocates significant funding to boost conservation programs and incentivize climate-smart agriculture.',
                                'Biofuels Initiatives: Supports the production and use of biofuels to reduce emissions from the transportation sector.',
                            ]
                        },
                        'Waste': {
                            'description': 'Focuses on reducing methane emissions from landfills through collection and use.',
                            'policies': [
                                'Landfill Methane Rule: Federal regulations require large landfills to capture methane emissions.',
                            ]
                        },
                    },
                    'Subsectors': {
                        'Electricity & Heat Generation': {
                            'description': 'The IRA is the key driver, providing tax credits for renewable energy projects and carbon capture.',
                            'policies': [
                                'IRA Clean Electricity Tax Credits: Provides credits for wind, solar, and other zero-emission technologies.',
                                'Carbon Capture Tax Credits (45Q): Offers significant tax credits for companies that capture and store CO\u2082.',
                            ]
                        },
                        'Road Transport': {
                            'description': 'Federal and state policies promote the transition to electric vehicles.',
                            'policies': [
                                'EV Tax Credits: Consumers can get up to $7,500 for purchasing new electric vehicles under the IRA.',
                                'CAFE Standards: Federal regulations that mandate increasing fuel efficiency for all vehicles.',
                            ]
                        },
                    }
                },
                'United Kingdom': {
                    'Sectors': {
                        'Energy': {
                            'description': 'The UK has rapidly decarbonized its energy sector by phasing out coal and investing in offshore wind.',
                            'policies': [
                                'Offshore Wind Target: Aims for 50 GW of offshore wind capacity by 2030.',
                                'Contracts for Difference (CfD): A scheme that provides long-term price certainty for renewable energy investors.',
                            ]
                        },
                        'Industrial Processes & Product Use': {
                            'description': 'Policies are focused on industrial decarbonization and transitioning to low-carbon fuels and technologies.',
                            'policies': [
                                'Carbon Pricing: The UK Emissions Trading Scheme (ETS) places a cap and price on carbon, encouraging industries to reduce emissions.',
                                'Industrial Decarbonisation Strategy: A plan to transition to low-carbon fuels (like hydrogen) and technologies in key industrial clusters.',
                            ]
                        },
                        'Agriculture, Forestry & Other Land Use': {
                            'description': 'Policies support a move to sustainable farming practices and better land management.',
                            'policies': [
                                'Environmental Land Management Schemes (ELMs): Incentivizes farmers to adopt environmentally friendly practices.',
                                'Tree Planting Targets: Aims to increase tree cover to absorb more carbon.',
                            ]
                        },
                        'Waste': {
                            'description': 'Policy focuses on increasing recycling rates and diverting waste from landfills to reduce methane.',
                            'policies': [
                                'Waste and Resources Strategy: Sets targets for higher recycling rates and a move towards a circular economy.',
                            ]
                        },
                    },
                    'Subsectors': {
                        'Electricity & Heat Generation': {
                            'description': 'The UK has successfully phased out coal and is now focused on ramping up renewables.',
                            'policies': [
                                'Final Coal Plant Closure: The last coal-fired power plant closed in 2024.',
                                'CfD Auctions: Government-led auctions to secure investment in new renewable energy projects at a set price.',
                            ]
                        },
                        'Road Transport': {
                            'description': 'Policies are designed to accelerate the transition to electric vehicles.',
                            'policies': [
                                '2035 ICE Ban: A policy to ban the sale of new petrol and diesel cars and vans from 2035.',
                                'Zero Emission Vehicle Mandate: Requires car manufacturers to sell a rising percentage of zero-emission vehicles annually.',
                            ]
                        },
                    }
                },
                'Australia': {
                    'Sectors': {
                        'Energy': {
                            'description': 'The electricity sector is Australia\'s largest source of emissions due to its reliance on coal. Policies are aimed at a rapid transition to renewables.',
                            'policies': [
                                'Safeguard Mechanism: Sets emissions limits for Australia\'s largest industrial polluters, requiring them to reduce emissions or buy offsets.',
                                'Capacity Investment Scheme (CIS): Provides revenue certainty for new clean energy projects.',
                            ]
                        },
                        'Industrial Processes & Product Use': {
                            'description': 'Policies are focused on managing emissions from industry and chemical processes.',
                            'policies': [
                                'Safeguard Mechanism: Covers industrial facilities, encouraging them to invest in emissions reduction technologies.',
                            ]
                        },
                        'Agriculture, Forestry & Other Land Use': {
                            'description': 'Policy provides incentives for farmers to adopt sustainable practices and sequester carbon.',
                            'policies': [
                                'Carbon Farming Initiative: Supports farmers in undertaking projects to reduce emissions or store carbon in the landscape.',
                                'National Methane Program: Initiatives aimed at reducing methane from livestock through improved feed and management.',
                            ]
                        },
                        'Waste': {
                            'description': 'Policies focus on landfill gas capture and improved waste management.',
                            'policies': [
                                'Landfill Gas Capture: Regulations and incentives to capture methane from landfills for energy generation.',
                            ]
                        },
                    },
                    'Subsectors': {
                        'Electricity & Heat Generation': {
                            'description': 'The Capacity Investment Scheme is a key tool for accelerating the transition away from coal.',
                            'policies': [
                                'Capacity Investment Scheme (CIS): Provides a government-backed revenue floor for new clean energy projects.',
                                'State Renewable Energy Zones: State-level initiatives to build out infrastructure for large-scale solar and wind projects.',
                            ]
                        },
                        'Road Transport': {
                            'description': 'Policies are focused on encouraging the uptake of electric vehicles.',
                            'policies': [
                                'EV Subsidies and Tax Breaks: Provides financial incentives for purchasing EVs.',
                            ]
                        },
                    }
                },
                'Ukraine': {
                    'Sectors': {
                        'Energy': {
                            'description': 'Climate policy is heavily influenced by EU accession and the need for green post-war reconstruction.',
                            'policies': [
                                'EU Alignment: Adopting EU climate and energy policies as part of its path to joining the European Union.',
                                'Green Reconstruction: Plans to rebuild a decentralized, modern energy grid with a higher share of renewables to improve energy security.',
                            ]
                        },
                        'Industrial Processes & Product Use': {
                            'description': 'Focuses on improving energy efficiency in industry and reducing emissions from processes.',
                            'policies': [
                                'Energy Efficiency Fund: A state-run program that provides financial support for businesses to implement energy-saving measures.',
                            ]
                        },
                        'Agriculture, Forestry & Other Land Use': {
                            'description': 'Policies focus on sustainable farming and improving waste management in the agricultural sector.',
                            'policies': [
                                'Land Management Initiatives: Promotes sustainable land use to combat degradation and support biodiversity.',
                                'Biomass for Energy: Incentives for using agricultural waste for energy generation.',
                            ]
                        },
                        'Waste': {
                            'description': 'Policies aim to modernize waste management to reduce methane emissions.',
                            'policies': [
                                'National Waste Management Strategy: Aims to improve waste collection and processing, including better landfill gas management.',
                            ]
                        },
                    },
                    'Subsectors': {
                        'Electricity & Heat Generation': {
                            'description': 'Policies promote a shift to renewable energy and a more resilient, decentralized grid.',
                            'policies': [
                                'Green Tariff: A feed-in tariff system that encourages investment in renewable energy projects.',
                                'Grid Modernization: Post-war reconstruction efforts prioritize a modern, decentralized grid.',
                            ]
                        },
                        'Road Transport': {
                            'description': 'Policies are aimed at promoting the use of electric vehicles and alternative fuels.',
                            'policies': [
                                'EV Subsidies: Provides incentives for the purchase of electric vehicles.',
                            ]
                        },
                    }
                },
                'Austria': {
                    'Sectors': {
                        'Energy': {
                            'description': 'Austria is a leader in renewable electricity, with a goal of achieving 100% renewable electricity by 2030.',
                            'policies': [
                                'Renewable Energy Expansion Act: Sets a target of adding 27 TWh of renewable electricity by 2030.',
                                'EU ETS: As an EU member, heavy industry and power sectors are covered by the EU Emissions Trading System.',
                            ]
                        },
                        'Industrial Processes & Product Use': {
                            'description': 'Policies are tied to EU-wide regulations and domestic support for green technologies.',
                            'policies': [
                                'EU ETS: Regulates emissions for large industrial facilities.',
                                'Green Industrial Strategy: Initiatives to promote clean technologies and processes, such as green hydrogen.',
                            ]
                        },
                        'Agriculture, Forestry & Other Land Use': {
                            'description': 'Policies focus on sustainable agriculture and the preservation of natural landscapes.',
                            'policies': [
                                'Adaptation Strategy: The Austrian Strategy for Adaptation to Climate Change includes specific measures for the agricultural sector.',
                                'Biofuels Mandate: Policies that require a certain percentage of transport fuels to be sourced from biofuels.',
                            ]
                        },
                        'Waste': {
                            'description': 'Austria has achieved significant emissions reductions in this sector through improved management and recycling.',
                            'policies': [
                                'Waste Management Strategy: Continuous improvement in waste collection and recycling to divert waste from landfills.',
                            ]
                        },
                    },
                    'Subsectors': {
                        'Electricity & Heat Generation': {
                            'description': 'The country leverages its vast hydropower and biomass resources to achieve high levels of renewable energy.',
                            'policies': [
                                'Hydropower Investment: Ongoing investment in hydropower, a major source of renewable energy.',
                                'Renewable Energy Act: Provides financial support and a legal framework for renewable energy development.',
                            ]
                        },
                        'Road Transport': {
                            'description': 'Policies aim to shift people away from private cars and towards public transport and EVs.',
                            'policies': [
                                'Climate Ticket: An affordable, nationwide public transport pass.',
                                'EV Subsidies: Provides financial incentives for the purchase of electric vehicles and charging infrastructure.',
                            ]
                        },
                    }
                }
            }

            # Gas selector for Bar Chart (Checkboxes)
            available_gases_tab2_bar = [co2_column] + other_gas_columns
            selected_gases_tab2_bar = st.multiselect(
                "Select Gases for Bar Chart",
                options=available_gases_tab2_bar,
                default=[co2_column]  # Default to CO2
            )

            # Bar chart of emissions by gas type for each sector
            st.subheader("Emissions by Sector and Gas Type")
            latest_year = filtered_sector_df['Year'].max()
            latest_data = filtered_sector_df[filtered_sector_df['Year'] == latest_year]

            # Melt the data for the selected gases
            latest_data_melted = latest_data.melt(
                id_vars=['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'],
                value_vars=selected_gases_tab2_bar,
                var_name='Gas',
                value_name='Emissions_kt'
            )

            fig_bar = px.bar(
                latest_data_melted,
                x='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
                y='Emissions_kt',
                color='Gas',
                title=f'Emissions by Sector and Gas Type ({latest_year})',
                labels={'Emissions_kt': 'Emissions (kt)',
                        'GREENHOUSE GAS SOURCE AND SINK CATEGORIES': 'Sector'}
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True, key='Sector bar chart')

            if selected_country_folder in chart_explanations:
                st.write(chart_explanations[selected_country_folder])

            # Gas selector for Pie Chart (Dropdown)
            available_gases_tab2_pie = [co2_column] + other_gas_columns
            selected_gas_tab2_pie = st.selectbox(
                "Select Gas for Pie Chart",
                options=available_gases_tab2_pie,
                index=0  # Default to the first gas (CO2)
            )
            
            # Pie chart of emissions distribution by sector
            st.subheader("Distribution of Emissions by Sector")
            fig_pie = px.pie(
                latest_data,
                values=selected_gas_tab2_pie,
                names='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
                title=f'Distribution of {selected_gas_tab2_pie} by Sector ({latest_year})'
            )
            st.plotly_chart(fig_pie, use_container_width=True, key='Sector pie chart')

            # Display the explanation for the selected gas
            if selected_gas_tab2_pie in gas_explanations:
                st.write(gas_explanations[selected_gas_tab2_pie])

            st.markdown("---")
            
            # Stacked area chart showing emissions by sector over time
            t1, t2 = st.tabs(['Area Chart', 'Line Chart'])
            st.subheader("Emissions by Sector Over Time")
            with t1:
                fig_area = px.area(
                filtered_sector_df,
                x='Year',
                y=selected_gas_tab2_pie,
                color='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
                title=f'{selected_gas_tab2_pie} Emissions by Sector Over Time',
                labels={'value': 'Emissions (kt)'}
            )
                st.plotly_chart(fig_area, use_container_width=True, key='area chart')

            with t2:
                fig_line = px.line(
                filtered_sector_df,
                x='Year',
                y=selected_gas_tab2_pie,
                color='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
                title=f'{selected_gas_tab2_pie} Emissions by Sector Over Time',
                labels={'value': 'Emissions (kt)'}
            )
                st.plotly_chart(fig_line, use_container_width=True, key='line_chart')

            if selected_hierarchy == 'Sectors':
                st.markdown("### Sector-Level Policies")
                if selected_country_folder in policy_data and 'Sectors' in policy_data[selected_country_folder]:
                    for sector, details in policy_data[selected_country_folder]['Sectors'].items():
                        with st.expander(f"**{sector}**"):
                            st.write(details['description'])
                            st.markdown("##### Key Policies:")
                            for policy in details['policies']:
                                st.markdown(f"- {policy}")
                else:
                    st.write(f"No sector-level policy data available for {selected_country_folder}.")

            elif selected_hierarchy == 'Subsectors':
                st.markdown("### Subsector-Level Policies")
                if selected_country_folder in policy_data and 'Subsectors' in policy_data[selected_country_folder]:
                    for subsector, details in policy_data[selected_country_folder]['Subsectors'].items():
                        with st.expander(f"**{subsector}**"):
                            st.write(details['description'])
                            st.markdown("##### Key Policies:")
                            for policy in details['policies']:
                                st.markdown(f"- {policy}")
                else:
                    st.write(f"No subsector-level policy data available for {selected_country_folder}.")
            
            elif selected_hierarchy == 'Sub-subsectors':
                st.warning(
                    "The policy data for 'Sub-subsectors' is not yet available. "
                    "Please select 'Sectors' or 'Subsectors'."
                )    

            st.markdown("---")
            st.header("Global Climate Commitments & Policies by Sector")

            sector_goals = {
                "Energy Supply": """
                    - Coal phase-out by 2030 (EU pledge)
                    - Net-zero energy sector by 2050 (EU pledge)
                    - 100% clean electricity target in many NDCs
                    """,
                "Transport": """
                    - Phase-out of internal combustion engine cars (2035 in EU)
                    - 100% EV sales by 2035 in some countries
                    - CORSIA (aviation carbon offsetting)) agreement for aviation (2021). Although weekly enforced.
                    """,
                "Industry": """
                    - EU ETS (carbon market), with stricter caps post-2020
                    - Clean industrial strategy (e.g. hydrogen, CCUS)
                    """,
                "Agriculture": """
                    - Global Methane Pledge (30% reduction) by 2030
                    - Climate-smart farming & soil carbon programs
                    - Sustainable livestock and fertilizer practices
                    """,
                "Residential & Commercial": """
                    - All new buildings to be net-zero carbon by 2030 (many NDCs)
                    - Renovation wave across EU
                    """,
                "Waste": """
                    - Landfill bans, methane capture regulations
                    - Circular economy frameworks in most Annex I countries
                    """
            }

            # Filter to sectors currently selected, or all if none selected
            goals_sectors = selected_sectors if selected_sectors else list(sector_goals.keys())

            selected_sector_goal = st.selectbox(
                "Select a sector to view global climate commitments:",
                options=goals_sectors
            )

            if selected_sector_goal in sector_goals:
                st.markdown(f"### Global Climate Commitments for {selected_sector_goal}")
                st.markdown(sector_goals[selected_sector_goal])


def render_climate_impact_page(sidebar_data):
    """Enhanced Climate Impact page with better storytelling"""
    total_emissions_df = sidebar_data['total_emissions_df']
    year_range = sidebar_data['year_range']
    selected_country_folder = sidebar_data['selected_country_folder']
    co2_column = [col for col in total_emissions_df.columns if 'CO\u2082' in col][0]
    
    # Enhanced header
    st.markdown(f""" Climate Impact: The Real-World Impact!
            How emissions translate into real climate impacts.
            Explore the connection between {selected_country_folder}'s emissions and the changing climate.
        
    """)
    
    # Add context about what this page shows
    st.markdown("""
    ###  **Connecting: Emissions → Climate → Impacts**
    
    This page reveals the chain reaction from greenhouse gas emissions to climate change impacts:
    
    **1. Global Emissions** → **2. Rising Temperatures** → **3. Extreme Weather** → **4. Human Consequences**
    """)
    
    # Load all required data
    weather_data = st.session_state.preloaded_data['weather']
    temp_data = st.session_state.preloaded_data['temperature']
    emissions_data = st.session_state.preloaded_data['global_emissions']
    
    if all(data is not None for data in [weather_data, temp_data, total_emissions_df]):
        
        # Add a "Climate Story" introduction
        st.markdown("---")
        st.subheader("Effects so far")
        
        # Calculate some compelling statistics
        filtered_temp_data = temp_data[temp_data['Year'].between(year_range[0], year_range[1])].copy()

        # Fix data types - convert Temperature_Anomaly to numeric
        filtered_temp_data['Temperature_Anomaly'] = pd.to_numeric(filtered_temp_data['Temperature_Anomaly'], errors='coerce')
        filtered_temp_data = filtered_temp_data.dropna(subset=['Temperature_Anomaly'])

        try:
            temp_change = filtered_temp_data['Temperature_Anomaly'].iloc[-1] - filtered_temp_data['Temperature_Anomaly'].iloc[0]
            avg_temp = filtered_temp_data['Temperature_Anomaly'].mean()
            latest_temp = filtered_temp_data['Temperature_Anomaly'].iloc[-1]
        except Exception as e:
            st.error(f"Error calculating temperature metrics: {str(e)}")
            temp_change = 0
            avg_temp = 0
            latest_temp = 0

        country_weather = weather_data[weather_data['Country'] == selected_country_folder]
        total_events = len(country_weather)
        total_affected = country_weather['Total Affected'].sum()
        
        # Create an engaging story box
        st.markdown(f"""
        <div style="background: #f0f8ff; padding: 1.5rem; border-left: 5px solid #4682b4; margin: 1rem 0;">
            <h4> The Global Picture ({year_range[0]}-{year_range[1]})</h4>
            <p><strong>Temperature Rise:</strong> Global temperatures have risen by <strong>{temp_change:.2f}°C</strong> during this period.</p>
            <p><strong>Local Impact in {selected_country_folder}:</strong> <strong>{total_events}</strong> extreme weather events recorded, affecting <strong>{total_affected:,}</strong> people.</p>
            <p><em>Every fraction of a degree matters. The data below shows how emissions, temperature, and extreme weather are interconnected.</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        # 1. Enhanced Global Temperature Section
        st.subheader("Global Temperature Changes")
        
        # Add more context
        st.markdown("""
        **Why temperature anomalies matter:** Temperature anomalies show how much warmer or cooler each year is 
        compared to the 20th century average (1951-1980). Even small changes have massive impacts on weather patterns, 
        sea levels, and ecosystems worldwide.
        """)
        
        # Temperature metrics with better context
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Temperature Rise", f"{temp_change:.2f}°C", 
                     delta=f"Since {year_range[0]}", delta_color="inverse")
        with col2:
            avg_temp = filtered_temp_data['Temperature_Anomaly'].mean()
            st.metric("Average Anomaly", f"{avg_temp:.2f}°C", 
                     help="Average temperature above 20th century baseline")
        with col3:
            latest_temp = filtered_temp_data['Temperature_Anomaly'].iloc[-1]
            st.metric("Latest Anomaly", f"{latest_temp:.2f}°C", 
                     help=f"Temperature anomaly in {year_range[1]}")
        with col4:
            # Add a "climate urgency" indicator
            if latest_temp > 1.0:
                urgency = " Critical"
                color = "inverse"
            elif latest_temp > 0.5:
                urgency = " Concerning"
                color = "inverse"
            else:
                urgency = " Monitoring"
                color = "normal"
            st.metric("Climate Status", urgency, delta=f"{latest_temp:.2f}°C above baseline", delta_color=color)

        # Enhanced temperature visualization
        fig_temp = px.line(
            filtered_temp_data,
            x='Year',
            y='Temperature_Anomaly',
            title=' Global Temperature Anomalies: The Climate Trend',
            labels={'Temperature_Anomaly': 'Temperature Anomaly (°C)'}
        )
        
        # Add critical thresholds
        fig_temp.add_hline(y=0, line_dash="dash", line_color="blue", 
                          annotation_text="20th Century Average")
        fig_temp.add_hline(y=1.5, line_dash="dot", line_color="orange", 
                          annotation_text="Paris Agreement Target: +1.5°C")
        fig_temp.add_hline(y=2.0, line_dash="dot", line_color="red", 
                          annotation_text="Dangerous Warming: +2.0°C")
        
        # Color the line based on temperature
        fig_temp.update_traces(
            line=dict(width=3),
            marker=dict(size=6)
        )
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # Add interpretation
        if temp_change > 0:
            st.warning(f"""
            **Rising Trend**: Global temperatures have risen by {temp_change:.2f}°C since {year_range[0]}. 
            This warming is primarily driven by increasing greenhouse gas concentrations in the atmosphere.
            """)

        
        st.markdown("---")

        # 2. Enhanced Global Emissions Relationship
        st.subheader(" The Emissions-Temperature Connection")
        
        st.markdown("""
        **More CO₂ in the atmosphere traps more heat, leading to global warming.** 
        The relationship isn't always linear year-to-year due to natural variability, but the long-term trend is unmistakable.
        """)
        
        # Create combined global dataset
        global_combined = pd.merge(
            filtered_temp_data,
            emissions_data[['Year', 'CO\u2082']],
            on='Year',
            how='inner'
        )
        
        # Create tabs for different views
        tab1, tab2 = st.tabs([" Time Series", "Correlation"])

        with tab1:
            # Time series with dual y-axis
            fig_timeseries = go.Figure()
            
            fig_timeseries.add_trace(go.Scatter(
                x=global_combined['Year'], 
                y=global_combined['Temperature_Anomaly'], 
                name='Temperature Anomaly', 
                line=dict(color='red', width=3),
                yaxis='y1'
            ))
            
            fig_timeseries.add_trace(go.Scatter(
                x=global_combined['Year'], 
                y=global_combined['CO\u2082'], 
                name='Global CO₂ Emissions', 
                line=dict(color='blue', width=3),
                yaxis='y2'
            ))
            
            fig_timeseries.update_layout(
                title='Global Temperature and CO₂ Emissions Over Time',
                yaxis=dict(title='Temperature Anomaly (°C)', side='left'),
                yaxis2=dict(title='CO₂ Emissions (kt)', side='right', overlaying='y'),
                template='plotly_white'
            )
            
            st.plotly_chart(fig_timeseries, use_container_width=True)

        with tab2:
            # Correlation scatter plot
            fig_correlation = px.scatter(
                global_combined,
                x='CO\u2082',
                y='Temperature_Anomaly',
                color='Year',
                title='The Relationship: Higher Emissions → Higher Temperatures',
                labels={'CO\u2082': 'CO₂ Emissions (kt)', 'Temperature_Anomaly': 'Temperature Anomaly (°C)'},
                color_continuous_scale='Viridis'
            )
            
            # Add trend line
            fig_correlation.add_trace(go.Scatter(
                x=global_combined['CO\u2082'],
                y=global_combined['Temperature_Anomaly'],
                mode='lines',
                name='Trend',
                line=dict(color='purple', width=2),
                showlegend=True
            ))
            
            st.plotly_chart(fig_correlation, use_container_width=True)


        # Calculate and display correlation
        correlation = global_combined['Temperature_Anomaly'].corr(global_combined['CO\u2082'])
        st.info(f"""
        **Statistical Insight**: The correlation between global CO₂ emissions and temperature anomalies is **{correlation:.3f}**.
        This strong positive correlation confirms the scientific understanding that emissions drive global warming.
        """)

        st.markdown("---")

        # 3. Enhanced National Impact Section
        st.subheader(f" Local effects: Climate Impacts in {selected_country_folder}")
        
        st.markdown(f"""
        **While {selected_country_folder} contributes to global emissions, 
        it also experiences the consequences of climate change through extreme weather events.** 
        This section explores the local impacts of the changing climate.
        """)
        
        # Enhanced national overview metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Extreme Events", f"{total_events}", 
                     help="Total recorded extreme weather events")
        with col2:
            total_deaths = country_weather['Total Deaths'].sum()
            st.metric("Lives Lost", f"{total_deaths:,}", 
                     delta="Human cost", delta_color="inverse")
        with col3:
            st.metric("People Affected", f"{total_affected:,}", 
                     help="Total people impacted by extreme weather")
        with col4:
            if total_events > 0:
                avg_impact = total_affected / total_events
                st.metric("Avg. Impact per Event", f"{avg_impact:,.0f}", 
                         help="Average people affected per event")

        # Enhanced event analysis
        st.markdown("####  Extreme Weather Analysis")
        
        analysis_tabs = st.tabs([" Frequency Over Time", " Event Types", " Severity Analysis"])
        
        with analysis_tabs[0]:
            yearly_events = country_weather.groupby('Year').agg({
                'Year': 'count',
                'Total Deaths': 'sum',
                'Total Affected': 'sum'
            }).rename(columns={'Year': 'Number of Events'}).reset_index()
            
            fig_events = px.bar(
                yearly_events,
                x='Year',
                y='Number of Events',
                title=f'📈 Annual Extreme Weather Events in {selected_country_folder}',
                color='Number of Events',
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig_events, use_container_width=True)
            
            if len(yearly_events) > 1:
                trend_slope = np.polyfit(yearly_events['Year'], yearly_events['Number of Events'], 1)[0]
                if trend_slope > 0:
                    st.warning(f" **Increasing Trend**: Extreme weather events are becoming more frequent (+{trend_slope:.2f} events/year on average)")
                else:
                    st.info(f" **Stable/Decreasing Trend**: Event frequency is stable or decreasing ({trend_slope:.2f} events/year)")
        
        with analysis_tabs[1]:
            event_types = country_weather['Disaster Type'].value_counts()
            fig_types = px.pie(
                values=event_types.values,
                names=event_types.index,
                title=f' Types of Extreme Weather in {selected_country_folder}'
            )
            st.plotly_chart(fig_types, use_container_width=True)
            
            st.markdown("**Most Common Disasters:**")
            for i, (disaster_type, count) in enumerate(event_types.head(3).items()):
                st.write(f"{i+1}. **{disaster_type}**: {count} events")
        
        with analysis_tabs[2]:
            if not country_weather.empty:
                severity_data = country_weather.groupby('Disaster Type').agg({
                    'Total Deaths': 'sum',
                    'Total Affected': 'sum',
                    'Year': 'count'
                }).rename(columns={'Year': 'Event Count'}).reset_index()
                
                fig_severity = px.scatter(
                    severity_data,
                    x='Total Deaths',
                    y='Total Affected',
                    size='Event Count',
                    color='Disaster Type',
                    title=f' Disaster Severity: Deaths vs People Affected in {selected_country_folder}',
                    hover_data=['Event Count']
                )
                st.plotly_chart(fig_severity, use_container_width=True)

        # Enhanced key insights with actionable information
        st.subheader(" What does this mean")
        
        # Calculate more insights
        if not global_combined.empty and not country_weather.empty:
            global_correlation = global_combined['Temperature_Anomaly'].corr(global_combined['CO\u2082'])
            
            # Try to calculate national correlation if we have enough data
            national_combined = pd.merge(
                country_weather.groupby('Year').size().reset_index(name='Event Count'),
                total_emissions_df[['Year', co2_column]],
                on='Year',
                how='inner'
            )
            
            insights_col1, insights_col2 = st.columns(2)
            
            with insights_col1:
                st.markdown(f"""
                ####  **Global Climate Science**
                
                - **Strong Evidence**: {global_correlation:.3f} correlation between emissions and temperature
                - **Temperature Rise**: {temp_change:.2f}°C increase since {year_range[0]}
                - **Scientific Consensus**: This warming is primarily human-caused
                
                **What this means:** The relationship between emissions and warming is clear and measurable.
                """)
            
            with insights_col2:
                st.markdown(f"""
                ####  **Impact Reality**
                
                - **{total_events} extreme events** recorded in {selected_country_folder}
                - **{total_affected:,} people affected** by climate disasters
                - **Most common threat**: {country_weather['Disaster Type'].mode().iloc[0] if not country_weather.empty else 'N/A'}
                """)
        
        # Add a call to action
        st.markdown("---")
        st.markdown("""
        ### 
        **Explore more:**
        - Check the **Emissions Trends** page to see which countries are successfully reducing emissions
        - Visit **Sector Distribution** to understand where emissions come from and how to address them
        """)

    else:
        st.error("Required data not available - some climate impact data may be missing")


def render_data_view_page(sidebar_data):
    """Render the Data View page"""
    selected_country_folder = sidebar_data['selected_country_folder']
    year_range = sidebar_data['year_range']
    
    st.header("Data Explorer & Download")
    st.markdown("Browse and download datasets including GHG emissions, gas species, temperature anomalies, and extreme weather events.")

    dataset_options = {
        "Total Emissions": os.path.join(data_root, selected_country_folder, "total", f"{selected_country_folder}_total_combined.parquet"),
        "Sector Emissions": os.path.join(data_root, selected_country_folder, "sectors", f"{selected_country_folder}_sectors_combined.parquet"),
        "Subsector Emissions": os.path.join(data_root, selected_country_folder, "subsectors", f"{selected_country_folder}_subsectors_combined.parquet"),
        "Sub-subsector Emissions": os.path.join(data_root, selected_country_folder, "sub_subsectors", f"{selected_country_folder}_sub_subsectors_combined.parquet"),
        "Extreme Weather": "data/EM-DATA/summary_extreme_weather_all_countries.parquet",
        "Temperature Anomalies": "data/EM-DATA/global_temp_anomalies.parquet"
    }

    
    # Add gas versions of each hierarchy level
    gas_species_folder = os.path.join(data_root, selected_country_folder)
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


# Main App Logic
def main():
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
