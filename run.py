import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob

# Set page configuration
st.set_page_config(
    page_title="GHG Emissions Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        weather_data['Country'] = weather_data['Country'].str.title()
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

data_root = "data/processed_data"
country_folders = sorted([
    name for name in os.listdir(data_root)
    if os.path.isdir(os.path.join(data_root, name))
])

# Display uppercase in the sidebar
country_labels = [name.title() for name in country_folders]

# Sidebar country selector
selected_label = st.sidebar.selectbox(
    "Select Country",
    options=country_labels
)

# Map label back to folder name
selected_country_folder = selected_label.lower()

# Load data for selected country
data_dict = load_country_data(selected_country_folder)

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

    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Emissions Trends", "Sector Distribution", "Extreme Weather", "temp", "Data View"])

    with tab1:
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

    with tab2:
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

    with tab3:
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
    
    with tab4:
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
    with tab5:
        st.header("Data Explorer and Download")
        
        # Create a dictionary of available datasets
        datasets = {
            "Total Emissions": total_emissions_df if total_emissions_df is not None else None,
            "Filtered Emissions": filtered_total_df if 'filtered_total_df' in locals() else None,
            "Sector Emissions": sector_df if sector_df is not None else None,
            "Filtered Sector Emissions": filtered_sector_df if 'filtered_sector_df' in locals() else None,
            "Weather Events": country_weather if 'country_weather' in locals() else None,
            "Temperature Data": filtered_temp_data if 'filtered_temp_data' in locals() else None
        }

        # Dataset selector
        selected_dataset = st.selectbox(
            "Select Dataset to View",
            options=list(datasets.keys())
        )

        # Display selected dataset and download button
        if datasets[selected_dataset] is not None:
            # Show info about the dataset
            st.info(f"Showing {len(datasets[selected_dataset])} rows and {len(datasets[selected_dataset].columns)} columns")
            
            # Create columns for download button and additional options
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Show the first few rows by default
                st.dataframe(datasets[selected_dataset])
            
            with col2:
                # Download button
                csv = datasets[selected_dataset].to_csv(index=False)
                st.download_button(
                    label="Download Data",
                    data=csv,
                    file_name=f'{selected_label}_{selected_dataset.lower().replace(" ", "_")}.csv',
                    mime='text/csv'
                )
                
                # Show basic statistics
                st.write("Dataset Info:")
                st.write(f"Time Period: {datasets[selected_dataset]['Year'].min()} - {datasets[selected_dataset]['Year'].max()}")
        else:
            st.warning("This dataset is not available for the selected country.")

        # Add description section
        st.markdown("---")
        st.subheader("Dataset Descriptions")
        
        descriptions = {
            "Total Emissions": "Complete yearly emissions data for all greenhouse gases.",
            "Filtered Emissions": f"Emissions data filtered for years {year_range[0]} to {year_range[1]}.",
            "Sector Emissions": "Emissions data broken down by sectors and categories.",
            "Filtered Sector Emissions": f"Sector emissions data filtered for years {year_range[0]} to {year_range[1]}.",
            "Weather Events": "Historical extreme weather events and their impacts.",
            "Temperature Data": "Global temperature anomaly data."
        }

        # Create a description table
        desc_df = pd.DataFrame({
            'Dataset': descriptions.keys(),
            'Description': descriptions.values()
        })
        
        st.table(desc_df)



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
