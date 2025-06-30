import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob

# Set page configuratiin
st.set_page_config(
    page_title="GHG Emissions Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_country_data(country_code):
    """Load data for a specific country with hierarchy levels"""
    country_path = f"data/processed_data/{country_code.lower()}"
    data_dict = {
        'Total': None,
        'Sectors': None,
        'Subsectors': None
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
     
# Sidebar country selector
available_countries = ['GBR', 'AUT', 'BLR', 'CAN', 'USA', 'EST']
selected_country = st.sidebar.selectbox(
    "Select Country",
    options=available_countries
)

# Load data for selected country
data_dict = load_country_data(selected_country)

#  total emissions data (for Tab 1)
total_emissions_df = data_dict['Total']

#  level selector (for Tab 2 only)
# Removed Total since it's not needed for sector 
hierarchy_options = ['Sectors', 'Subsectors']  
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
    co2_column = [col for col in total_emissions_df.columns if 'Net CO2' in col][0]
    other_gas_columns = [col for col in total_emissions_df.columns if any(gas in col for gas in ['CH4', 'N2O', 'SF6', 'HFC', 'PFC'])]

    # Sidebar filters for sector analysis only
    st.sidebar.markdown("### Sector Analysis Filters")
    # Sector selector
    if sector_df is not None:
        available_sectors = sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].unique()
        selected_sectors = st.sidebar.multiselect(
            "Select Sectors",
            options=available_sectors,
            default=available_sectors
        )

        # Gas selector for sector analysis
        selected_gases = st.sidebar.multiselect(
            "Select Gases for Sector Analysis",
            options=[co2_column] + other_gas_columns,
            default=[co2_column]
        )

        # Filter sector data 
        filtered_sector_df = sector_df[
            (sector_df['Year'].between(year_range[0], year_range[1])) &
            (sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].isin(selected_sectors))
        ]

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Emissions Trends", "Sector Distribution", "Extreme Weather", "temp"])

    with tab1:
        # Filter total emissions data by year
        filtered_total_df = total_emissions_df[
            total_emissions_df['Year'].between(year_range[0], year_range[1])
        ]
        
        # CO2 Emissions Time Series (Total only)
        st.subheader("CO2 Emissions Over Time")
        fig_co2 = px.line(
            filtered_total_df,
            x='Year',
            y=co2_column,
            title='Net CO2 Emissions/Removals',
            labels={'value': 'Emissions (kt)'}
        )
        st.plotly_chart(fig_co2, use_container_width=True)

        # Other Gases Time Series (Total only --. showing overall emissions)
        st.subheader("Other Greenhouse Gases Over Time")
        fig_other = px.line(
            filtered_total_df,
            x='Year',
            y=other_gas_columns,
            title='Other Greenhouse Gas Emissions',
            labels={'value': 'Emissions (kt)'}
        )
        st.plotly_chart(fig_other, use_container_width=True)

        # Stacked area chart showing emissions by sector over time
        if sector_df is not None:
            st.subheader("Emissions by Sector Over Time")
            for gas in selected_gases:
                fig_area = px.area(
                    filtered_sector_df,
                    x='Year',
                    y=gas,
                    color='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
                    title=f'{gas} Emissions by Sector Over Time',
                    labels={'value': 'Emissions (kt)'}
                )
                st.plotly_chart(fig_area, use_container_width=True)

    with tab2:
        if sector_df is not None:
            col1, col2 = st.columns(2)

            with col1:
                # Pie chart of emissions distribution by sector
                latest_year = filtered_sector_df['Year'].max()
                latest_data = filtered_sector_df[filtered_sector_df['Year'] == latest_year]
                
                for gas in selected_gases:
                    fig_pie = px.pie(
                        latest_data,
                        values=gas,
                        names='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
                        title=f'Distribution of {gas} by Sector ({latest_year})'
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                # Bar chart of emissions by gas type for each sector
                latest_data_melted = latest_data.melt(
                    id_vars=['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'],
                    value_vars=selected_gases,
                    var_name='Gas',
                    value_name='Emissions_kt'
                )
                
                fig_bar = px.bar(
                    latest_data_melted,
                    x='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
                    y='Emissions_kt',
                    color='Gas',
                    title='Emissions by Sector and Gas Type',
                    labels={'Emissions_kt': 'Emissions (kt)',
                           'GREENHOUSE GAS SOURCE AND SINK CATEGORIES': 'Sector'}
                )
                fig_bar.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_bar, use_container_width=True)
    
    
    with tab3:
        st.header("Extreme Weather Events Analysis")
        
        # Load weather data
        weather_data = load_weather_data()
        
        if weather_data is not None:
            # Filter for selected country
            country_weather = weather_data[weather_data['ISO'] == selected_country]
            
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
                yearly_events = country_weather.groupby('year').size().reset_index(name='Number of Events')
                fig_temporal = px.bar(
                    yearly_events,
                    x='year',
                    y='Number of Events',
                    title=f'Annual Frequency of Extreme Weather Events in {selected_country}'
                )
            else:
                hazard_yearly = country_weather.groupby(['year', 'Disaster Type']).size().reset_index(name='count')
                fig_temporal = px.bar(
                    hazard_yearly,
                    x='year',
                    y='count',
                    color='Disaster Type',
                    title=f'Distribution of Event Types by Year in {selected_country}',
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
            
            yearly_trends = country_weather.groupby('year').agg({
                'Total Deaths': 'sum',
                'Total Affected': 'sum',
                "Total Damage ('000 US$)": 'sum'
            }).reset_index()
            
            fig_trends = px.line(
                yearly_trends,
                x='year',
                y=impact_metric,
                title=f'Yearly {impact_metric} from Extreme Weather Events'
            )
            st.plotly_chart(fig_trends, use_container_width=True)

            # 5. Multi-Country Comparison 
            st.subheader("Compare with Other Countries")
            countries_to_compare = st.multiselect(
                "Select countries to compare",
                weather_data['ISO'].unique(),
                default=[selected_country]
            )
            
            comparison_data = weather_data[weather_data['ISO'].isin(countries_to_compare)]
            
            fig_comparison = px.bar(
                comparison_data.groupby(['ISO', 'Disaster Type']).size().reset_index(name='count'),
                x='ISO',
                y='count',
                color='Disaster Type',
                title='Event Frequency by Country and Type',
                barmode='group'
            )
            st.plotly_chart(fig_comparison, use_container_width=True)

            # 6. Key Insights Box
            st.subheader("Key Insights")
            most_common_disaster = country_weather['Disaster Type'].mode().iloc[0]
            worst_year = country_weather.groupby('year')['Total Affected'].sum().idxmax()
            deadliest_event = country_weather.loc[country_weather['Total Deaths'].idxmax()]
            
            st.info(f"""
            Key Statistics for {selected_country}:
            * Most frequent disaster type: {most_common_disaster}
            * Year with highest impact: {worst_year}
            * Deadliest event: {deadliest_event['Disaster Type']} in {deadliest_event['year']}
            * Average events per year: {total_events / len(country_weather['year'].unique()):.1f}
            """)

        else:
            st.error("Weather data not available")
    
    with tab4:
        st.header("Global Temperature Analysis")
        
        # Load temperature data
        temp_data = load_temperature_data()
        
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
                filtered_total_df[['Year', co2_column]],
                on='Year',
                how='inner'
            )
            
            # Create figure with two y-axes using px
            fig_combined = px.line(
                combined_data,
                x='Year',
                y=['Temperature_Anomaly', co2_column],
                title='Temperature Anomalies vs CO2 Emissions',
                labels={
                    'Temperature_Anomaly': 'Temperature Anomaly (°C)',
                    co2_column: 'CO2 Emissions (kt)',
                    'value': 'Value',
                    'variable': 'Metric'
                }
            )
            st.plotly_chart(fig_combined, use_container_width=True)

            # 3. Scatter plot of Temperature vs CO2
            st.subheader("Temperature vs CO2 Correlation")
            fig_scatter = px.scatter(
                combined_data,
                x=co2_column,
                y='Temperature_Anomaly',
                title='Temperature Anomaly vs CO2 Emissions',
                labels={
                    co2_column: 'CO2 Emissions (kt)',
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
            correlation = combined_data['Temperature_Anomaly'].corr(combined_data[co2_column])
            
            # Key findings box
            st.info(f"""
            Key Findings:

            """)

        else:
            st.error("Temperature data not available")

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