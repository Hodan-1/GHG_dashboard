import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
import folium
from streamlit_folium import st_folium
import json

# Set page configuration
st.set_page_config(
    page_title="GHG Emissions Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
            files = glob.glob(os.path.join(level_path, "*.csv"))
            if files:
                data_dict[level] = pd.concat([pd.read_csv(f) for f in files])
    
    return data_dict

@st.cache_data
def load_weather_data():
    """Load extreme weather events data"""
    try:
        weather_data = pd.read_csv('data/EM-DATA/summary_extreme_weather_all_countries.csv')
        return weather_data
    except:
        return None

@st.cache_data
def load_temperature_data():
    """Load global temperature anomaly data"""
    try:
        temp_data = pd.read_csv('data/EM-DATA/global_temp_anomalies.csv')
        return temp_data
    except:
        return None   

def load_global_emission():
    """
    Load global emissions data
    """
    try:
        global_emissions = pd.read_csv("data/EM-DATA/global_emissions.csv")
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
    
data_root = "data/processed_data"
country_folders = sorted([
    name for name in os.listdir(data_root)
    if os.path.isdir(os.path.join(data_root, name))
])

# Display uppercase in the sidebar
country_labels = [name for name in country_folders]

# Sidebar country selector
selected_label = st.sidebar.selectbox(
    "Select Country",
    options=country_labels
)

# Map label back to folder name
selected_country_folder = selected_label

# Load data for selected country
data_dict = load_country_data(selected_country_folder)

#  total emissions data (for Tab 1)
total_emissions_df = data_dict['Total']

#  level selector (for Tab 2 only)
# Removed Total since it's not needed for sector 
hierarchy_options = ['Sectors', 'Subsectors', 'Sub-subsectors']  
selected_hierarchy = st.sidebar.radio(
    "Select Detail Level for Sector Analysis",
    options=hierarchy_options
)

# Get the correct dataset for sector analysis
sector_df = data_dict.get(selected_hierarchy)

if total_emissions_df is not None:
    # Year range selector
    years = sorted(total_emissions_df['Year'].unique())
    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min(years),
        max_value=max(years),
        value=(min(years), max(years))
    )

    # Get chosen gases
    co2_column = [col for col in total_emissions_df.columns if 'CO2' in col][0]
    other_gas_columns = [col for col in total_emissions_df.columns if any(gas in col for gas in ['CH4', 'N2O', 'SF6', 'HFC', 'PFC'])]

    def get_ghg_data(country_code, sector=None, subsector=None):
        """Get the GHG data for a specific country and sector/subsector"""
        data = total_emissions_df[total_emissions_df['Country'] == country_code]
        if sector:
            data = data[data['Sector'] == sector]
        if subsector:
            data = data[data['Subsector'] == subsector]
        
        # Calculate the total emissions for the filtered data
        total_emissions = data[co2_column].sum()
        
        return total_emissions

    import math

    def get_color(emissions):
        """Get the color for a country based on its emission value"""
        if emissions == 0:
            return '#ffffff'  # White for no emissions
        else:
            # Calculate a color intensity based on the log of the emissions value
            intensity = math.log(emissions) / math.log(max(1, total_emissions_df[co2_column].max()))
            
            # Use a colormap to get the color based on the intensity
            colormap = ['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026']
            color_index = int(intensity * (len(colormap) - 1))
            return colormap[color_index]
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["GHG Map", "Emissions Trends", "Sector Distribution", "Extreme Weather", "Temperature change", "Data View"])
    with tab1:
        st.header("Global GHG Emissions Map")
        
        # Load GeoJSON data
        geojson = load_geojson()
        
        if geojson is not None and total_emissions_df is not None:
            # 1. Prepare emissions data for ALL countries (not just selected)
            # Get list of all available country folders
            all_country_folders = [name for name in os.listdir("data/processed_data") 
                                if os.path.isdir(os.path.join("data/processed_data", name))]
            
            # 2. Create a dictionary to store all gases for each country
            country_emissions = {}
            gas_columns = [co2_column] + other_gas_columns  # All gas columns
            
            for country_folder in all_country_folders:
                # Load each country's total emissions data
                country_path = f"data/processed_data/{country_folder}/total"
                if os.path.exists(country_path):
                    files = glob.glob(os.path.join(country_path, "*.csv"))
                    if files:
                        df = pd.concat([pd.read_csv(f) for f in files])
                        country_name = country_folder
                        # Sum emissions across all years for each gas
                        emissions = {gas: df[gas].sum() for gas in gas_columns if gas in df.columns}
                        country_emissions[country_name] = emissions
            
            # 3. Convert to DataFrame for Plotly
            emissions_df = pd.DataFrame.from_dict(country_emissions, orient='index').reset_index()
            emissions_df = emissions_df.rename(columns={'index': 'Country'})
            
            # 4. Create the choropleth map with custom hover data
            fig = px.choropleth(
                emissions_df,
                geojson=geojson,
                locations='Country',
                featureidkey="properties.name",
                color=co2_column,  # Default to CO2 for coloring
                color_continuous_scale="YlOrRd",
                range_color=(0, emissions_df[co2_column].max()),
                labels={co2_column: 'CO2 Emissions (kt)'},
                hover_data={gas: ':.2f' for gas in gas_columns},  # Show all gases in tooltip
                hover_name='Country',
                title="Global GHG Emissions by Country (All Gases)"
            )
            
            # 5. Customize map appearance
            fig.update_geos(
                showcountries=True,
                countrycolor="Black",
                showocean=True,
                oceancolor="LightBlue",
                projection_type="natural earth"
            )
            
            fig.update_layout(
                margin={"r":0,"t":40,"l":0,"b":0},
                coloraxis_colorbar=dict(
                    title="CO2 Emissions (kt)",
                    thickness=15,
                    len=0.5
                )
            )
            
            # 6. Add dropdown to change which gas determines the color
            fig.update_layout(
                updatemenus=[{
                    "buttons": [
                        {
                            "args": [{"color": [emissions_df[gas]]}],
                            "label": gas,
                            "method": "restyle"
                        } for gas in gas_columns
                    ],
                    "direction": "down",
                    "showactive": True,
                    "x": 0.1,
                    "xanchor": "left",
                    "y": 1.1,
                    "yanchor": "top"
                }]
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Introduction for GHG emissions
            st.markdown("""
            ### Introduction to Greenhouse Gas (GHG) Emissions

            Greenhouse gases (GHGs) are gases in Earth's atmosphere that trap heat, contributing to global warming and climate change. 
            The most commonly reported GHGs include:

            - **Carbon dioxide (CO₂)**
            - **Methane (CH₄)**
            - **Nitrous oxide (N₂O)**
            - **Sulfur hexafluoride (SF₆)**
            - **Hydrofluorocarbons (HFCs)**
            - **Perfluorocarbons (PFCs)**

            These gases are reported in national inventories under the **Common Reporting Format (CRF) tables**, a structured reporting framework developed by the UNFCCC.

            ### History

            Since the adoption of the **UNFCCC (United Nations Framework Convention on Climate Change)** in 1992 and the **Kyoto Protocol (1997)** and **Paris Agreement (2015)**,  **Annex I Parties** (developed nations) are required to submit 
            annual greenhouse gas inventories. These inventories follow strict guidelines and provide detailed emissions by sector and gas type.

            This tab visualises total reported emissions for these gases across countries, using **Annex I inventory data**, where available.
            You can explore emissions for each gas using the dropdown menu below.
            """)


        else:
            st.error("Required data not available")

    with tab2:
        st.header("Emissions Trends")

        # Filter total emissions data by year
        filtered_total_df = total_emissions_df[
            total_emissions_df['Year'].between(year_range[0], year_range[1])
        ]

        # Gas selection for Tab 1
        selected_gases_tab1 = st.multiselect(
            "Select Gases for Emissions Trends",
            options=[co2_column] + other_gas_columns,
            default=[co2_column]
        )

        # CO2 Emissions Time Series (Total only)
        st.subheader("CO2 Emissions Over Time")
        fig_co2 = px.line(
            filtered_total_df,
            x='Year',
            y=co2_column,
            title='Net CO2 Emissions/Removals',
            labels={'value': 'Emissions (kt)'}
        )
        st.plotly_chart(fig_co2, use_container_width=True, key= 'CO2 emission graph')

        # Other Gases Time Series (Total only --. showing overall emissions)
        st.subheader("Other Greenhouse Gases Over Time")
        fig_other = px.line(
            filtered_total_df,
            x='Year',
            y=selected_gases_tab1,  # Use selected gases for the plot
            title='Other Greenhouse Gas Emissions',
            labels={'value': 'Emissions (kt)'}
        )
        st.plotly_chart(fig_other, use_container_width=True, key='Other gases graph')

    with tab3:
        st.header("Sector Distribution")

        if sector_df is not None:
            # Sector selector for Tab 2
            available_sectors = sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].unique()
            selected_sectors = st.multiselect(
                "Select Sectors for Sector Analysis",
                options=available_sectors,
                default=available_sectors
            )

            # Gas selector for Bar Chart (Checkboxes)
            available_gases_tab2_bar = [co2_column] + other_gas_columns
            selected_gases_tab2_bar = st.multiselect(
                "Select Gases for Bar Chart",
                options=available_gases_tab2_bar,
                default=[co2_column]  # Default to CO2
            )

            # Gas selector for Pie Chart (Dropdown)
            available_gases_tab2_pie = [co2_column] + other_gas_columns
            selected_gas_tab2_pie = st.selectbox(
                "Select Gas for Pie Chart",
                options=available_gases_tab2_pie,
                index=0  # Default to the first gas (CO2)
            )

            # Filter sector data
            filtered_sector_df = sector_df[
                (sector_df['Year'].between(year_range[0], year_range[1])) &
                (sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].isin(selected_sectors))
            ]

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

            # Pie chart of emissions distribution by sector
            st.subheader("Distribution of Emissions by Sector")
            fig_pie = px.pie(
                latest_data,
                values=selected_gas_tab2_pie,
                names='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
                title=f'Distribution of {selected_gas_tab2_pie} by Sector ({latest_year})'
            )
            st.plotly_chart(fig_pie, use_container_width=True, key='Sector pie chart')

            # Stacked area chart showing emissions by sector over time
            st.subheader("Emissions by Sector Over Time")
            fig_area = px.area(
                filtered_sector_df,
                x='Year',
                y=selected_gas_tab2_pie,
                color='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
                title=f'{selected_gas_tab2_pie} Emissions by Sector Over Time',
                labels={'value': 'Emissions (kt)'}
            )
            st.plotly_chart(fig_area, use_container_width=True)

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

    with tab4:
        st.header("Extreme Weather Events Analysis")
        
        # Load weather data
        weather_data = load_weather_data()
        
        if weather_data is not None:
            # Filter for selected country
            country_weather = weather_data[weather_data['Country'] == selected_label]
            
            # 1. Overview Metrics 
            st.subheader("Overview Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_events = len(country_weather)
                st.metric("Total Events", total_events)
                
            with col2:
                total_deaths = country_weather['Total Deaths'].sum()
                st.metric("Total Deaths", f"{total_deaths:,}")
                
            with col3:
                total_affected = country_weather['Total Affected'].sum()
                st.metric("Total People Affected", f"{total_affected:,}")

            # 2. Toggle Bar Charts
            st.subheader("Analysis of Extreme Weather Events")
            chart_type = st.radio(
                "Select Analysis View",
                ["Annual Frequency", "Distribution by Event Type"]
            )
            
            if chart_type == "Annual Frequency":
                yearly_events = country_weather.groupby('Year').size().reset_index(name='Number of Events')
                fig_temporal = px.bar(
                    yearly_events,
                    x='Year',
                    y='Number of Events',
                    title=f'Annual Frequency of Extreme Weather Events in {selected_label}'
                )
            else:
                hazard_yearly = country_weather.groupby(['Year', 'Disaster Type']).size().reset_index(name='count')
                fig_temporal = px.bar(
                    hazard_yearly,
                    x='Year',
                    y='count',
                    color='Disaster Type',
                    title=f'Distribution of Event Types by Year in {selected_label}',
                    barmode='stack'
                )
            st.plotly_chart(fig_temporal, use_container_width=True)

            # 3. Pie Chart + Impact Table 
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Distribution of Event Types")
                fig_pie = px.pie(
                    country_weather,
                    names='Disaster Type',
                    values='Total Affected',
                    title='Impact by Disaster Type'
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                st.subheader("Impact Metrics by Event Type")
                impact_summary = country_weather.groupby('Disaster Type').agg({
                    'Total Deaths': 'sum',
                    'Total Affected': 'sum',
                    "Total Damage ('000 US$)": 'sum'
                }).reset_index()
                st.dataframe(impact_summary)

            # 4. Line Chart for Yearly Trend 
            st.subheader("Yearly Impact Analysis")
            impact_metric = st.selectbox(
                "Select Impact Metric",
                ['Total Deaths', 'Total Affected', "Total Damage ('000 US$)"]
            )
            
            yearly_trends = country_weather.groupby('Year').agg({
                'Total Deaths': 'sum',
                'Total Affected': 'sum',
                "Total Damage ('000 US$)": 'sum'
            }).reset_index()
            
            fig_trends = px.line(
                yearly_trends,
                x='Year',
                y=impact_metric,
                title=f'Yearly {impact_metric} from Extreme Weather Events'
            )
            st.plotly_chart(fig_trends, use_container_width=True)

            # 5. Multi-Country Comparison 
            countries_to_compare = st.multiselect(
            "Select countries to compare",
            options=weather_data['Country'].unique(),  
            default=[selected_label]
        )
            
            comparison_data = weather_data[weather_data['Country'].isin(countries_to_compare)]
            
            fig_comparison = px.bar(
                comparison_data.groupby(['Country', 'Disaster Type']).size().reset_index(name='count'),
                x='Country',
                y='count',
                color='Disaster Type',
                title='Event Frequency by Country and Type',
                barmode='group'
            )
            st.plotly_chart(fig_comparison, use_container_width=True)

            # 6. Key Insights Box
            st.subheader("Key Insights")
            most_common_disaster = country_weather['Disaster Type'].mode().iloc[0]
            worst_year = country_weather.groupby('Year')['Total Affected'].sum().idxmax()
            deadliest_event = country_weather.loc[country_weather['Total Deaths'].idxmax()]
            
            st.info(f"""
            Key Statistics for {selected_label}:
            * Most frequent disaster type: {most_common_disaster}
            * Year with highest impact: {worst_year}
            * Deadliest event: {deadliest_event['Disaster Type']} in {deadliest_event['Year']}
            * Average events per year: {total_events / len(country_weather['Year'].unique()):.1f}
            """)

        else:
            st.error("Weather data not available")
    
    with tab5:
        st.header("Global Temperature Analysis")
        
        # Load temperature data
        temp_data = load_temperature_data()
        
        emissions_data = load_global_emission()
        if temp_data is not None:
            # Filter temperature data for selected year range
            filtered_temp_data = temp_data[temp_data['Year'].between(year_range[0], year_range[1])]
            
            # 1. Temperature Trend
            st.subheader("Global Temperature Anomalies Over Time")
            fig_temp = px.line(
                filtered_temp_data,
                x='Year',
                y='Temperature_Anomaly',
                title='Global Temperature Anomalies (°C)',
                labels={'Temperature_Anomaly': 'Temperature Anomaly (°C)'}
            )
            fig_temp.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Baseline")
            st.plotly_chart(fig_temp, use_container_width=True)

            # 2. Combined Temperature and CO2 Emissions Analysis
            st.subheader("Temperature vs CO2 Emissions Analysis")
            
            # Create combined dataset
            combined_data = pd.merge(
                filtered_temp_data,
                emissions_data[['Year', 'CO2']],
                on='Year',
                how='inner'
            )
            
            # Create figure with two y-axes using px
            fig_combined = px.line(
                combined_data,
                x='Year',
                y=['Temperature_Anomaly', 'CO2'],
                title='Temperature Anomalies vs CO2 Emissions',
                labels={
                    'Temperature_Anomaly': 'Temperature Anomaly (°C)',
                    'CO2': 'CO2 Emissions (kt)',
                    'value': 'Value',
                    'variable': 'Metric'
                }
            )
            st.plotly_chart(fig_combined, use_container_width=True)

            # 3. Scatter plot of Temperature vs CO2
            st.subheader("Temperature vs CO2 Correlation")
            fig_scatter = px.scatter(
                combined_data,
                x='CO2',
                y='Temperature_Anomaly',
                title='Temperature Anomaly vs CO2 Emissions',
                labels={
                    'CO2': 'CO2 Emissions (kt)',
                    'Temperature_Anomaly': 'Temperature Anomaly (°C)'
                }
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

            # 4. Key Statistics
            st.subheader("Temperature Change Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                temp_change = filtered_temp_data['Temperature_Anomaly'].iloc[-1] - filtered_temp_data['Temperature_Anomaly'].iloc[0]
                st.metric(
                    "Total Temperature Change",
                    f"{temp_change:.2f}°C",
                    delta=f"{temp_change:.2f}°C"
                )
            
            with col2:
                avg_temp = filtered_temp_data['Temperature_Anomaly'].mean()
                st.metric(
                    "Average Temperature Anomaly",
                    f"{avg_temp:.2f}°C"
                )
            
            with col3:
                latest_temp = filtered_temp_data['Temperature_Anomaly'].iloc[-1]
                st.metric(
                    "Latest Temperature Anomaly",
                    f"{latest_temp:.2f}°C"
                )

            # 5. Correlation Analysis
            correlation = combined_data['Temperature_Anomaly'].corr(combined_data['CO2'])
            
            # Key findings box
            st.info(f"""
            Key Findings:

            """)

        else:
            st.error("Temperature data not available")
    with tab6:
        st.header(" Data Explorer & Download")

        st.markdown("Browse and download datasets including GHG emissions, gas species, temperature anomalies, and extreme weather events.")

        dataset_options = {
            "Total Emissions": os.path.join(data_root, selected_country_folder, "total", f"{selected_country_folder}_total_combined.csv"),
            "Sector Emissions": os.path.join(data_root, selected_country_folder, "sectors", f"{selected_country_folder}_sectors_combined.csv"),
            "Subsector Emissions": os.path.join(data_root, selected_country_folder, "subsectors", f"{selected_country_folder}_subsectors_combined.csv"),
            "Sub-subsector Emissions": os.path.join(data_root, selected_country_folder, "sub_subsectors", f"{selected_country_folder}_sub_subsectors_combined.csv"),
            "Extreme Weather": "data/EM-DATA/summary_extreme_weather_all_countries.csv",
            "Temperature Anomalies": "data/EM-DATA/global_temp_anomalies.csv"
        }

        # Add gas versions of each hierarchy level
        gas_species_folder = os.path.join(data_root, selected_country_folder)
        for gas_folder in os.listdir(gas_species_folder):
            gas_path = os.path.join(gas_species_folder, gas_folder)
            if not os.path.isdir(gas_path):
                continue

            gas = gas_folder.upper()
            for level in ["total", "sectors", "subsectors", "sub_subsectors"]:
                combined_file = os.path.join(gas_path, level, f"{selected_country_folder}_{level}_{gas.lower()}_combined.csv")
                if os.path.exists(combined_file):
                    key = f"{gas} - {level.capitalize()} Emissions"
                    dataset_options[key] = combined_file

        selected_dataset_name = st.selectbox("Select a dataset to explore", list(dataset_options.keys()))
        dataset_path = dataset_options[selected_dataset_name]

        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path)

            if 'Year' in df.columns:
                years = sorted(df['Year'].dropna().unique())
                year_filter = st.slider("Filter by Year", min_value=int(min(years)), max_value=int(max(years)),
                                        value=(int(min(years)), int(max(years))))
                df = df[df['Year'].between(year_filter[0], year_filter[1])]

            st.write(f"Preview of **{selected_dataset_name}**")
            st.dataframe(df.head(100))

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f" Download {selected_dataset_name} as CSV",
                data=csv,
                file_name=f"{selected_dataset_name.replace(' ', '_').lower()}.csv",
                mime='text/csv'
            )
        else:
            st.warning("Dataset not found.")

        st.markdown("---")
        st.subheader(" Dataset Descriptions")


    # Metrics summary (move to top later)
    st.subheader("Summary Metrics")
    col1, col2, col3 = st.columns(3)
    
    latest_year = filtered_total_df['Year'].max()
    total_co2 = filtered_total_df[co2_column].sum()
    avg_annual_co2 = filtered_total_df.groupby('Year')[co2_column].sum().mean()
    latest_co2 = filtered_total_df[filtered_total_df['Year'] == latest_year][co2_column].sum()
    
    col1.metric("Total CO2 Emissions", f"{total_co2:,.0f} kt")
    col2.metric("Average Annual CO2", f"{avg_annual_co2:,.0f} kt")
    col3.metric("Latest Year CO2", f"{latest_co2:,.0f} kt")

    
# Footer
st.markdown("---")
st.markdown("Data source: National Greenhouse Gas Inventory Submissions")
