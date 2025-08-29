"""
Climate Impact page for the GHG Emissions Dashboard.
Shows the connection between emissions and climate impacts.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from helper.utils import get_co2_column


def render_climate_impact_page(sidebar_data):
    """
    Renders the Climate Impact page with interactive visualisations and analysis.

    Args:
        sidebar_data (dict): Dictionary containing:
            - total_emissions_df (pd.DataFrame): Emissions data
            - year_range (tuple): Selected year range (start_year, end_year)
            - selected_country_folder (str): Currently selected country

    Returns:
        None - Renders content directly to Streamlit page
    """
    # Extract required data from sidebar
    total_emissions_df = sidebar_data['total_emissions_df']
    year_range = sidebar_data['year_range']
    selected_country_folder = sidebar_data['selected_country_folder']
    co2_column = get_co2_column(total_emissions_df)
    
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

        # Add metrics for top of page
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
        st.info(f"""
        **The Global Picture ({year_range[0]}-{year_range[1]})**

        **Temperature Rise:** Global temperatures have risen by **{temp_change:.2f}°C** during this period.

        **Local Impact in {selected_country_folder}:** **{total_events}** extreme weather events recorded, affecting **{total_affected:,}** people.

        *Every fraction of a degree matters. The data below shows how emissions, temperature, and extreme weather are interconnected.*
        """)
        
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

        # Enhanced temperature visualisation
        temp_chart_tab, temp_table_tab = st.tabs('Chart', 'Table')
        with temp_chart_tab: 
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
        
        with temp_table_tab:
            st.dataframe(filtered_temp_data)
            csv = filtered_temp_data.to_csv(index=False)
            st.download_button(
                label="Download temperature data as CSV",
                data=csv,
                file_name=f'global_temperature_data_{year_range[0]}-{year_range[1]}.csv',
                mime='text/csv',
            ) 
            
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
        tab1, tab2, tab3 = st.tabs([" Time Series", "Correlation", "Table"])

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

        with tab3:
            st.dataframe(global_combined)
            csv = global_combined.to_csv(index=False)
            st.download_button(
                label="Download emissions-temperature data as CSV",
                data=csv,
                file_name=f'emissions_temperature_data_{year_range[0]}-{year_range[1]}.csv',
                mime='text/csv',
            )

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
        
        analysis_tabs = st.tabs([" Frequency Over Time", " Event Types", " Severity Analysis", "Data Table"])
        
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
             
        with analysis_tabs[3]: 
            st.dataframe(country_weather)
    
            # Provide download options for different aggregations
            col1, col2 = st.columns(2)
            
            with col1:
                # Raw event data
                csv_raw = country_weather.to_csv(index=False)
                st.download_button(
                    label="Download raw event data",
                    data=csv_raw,
                    file_name=f'climate_events_{selected_country_folder}.csv',
                    mime='text/csv',
                )
            
            with col2:
                # Aggregated yearly summary
                yearly_summary = country_weather.groupby('Year').agg({
                    'Total Deaths': 'sum',
                    'Total Affected': 'sum',
                    'Disaster Type': 'count'
                }).reset_index()
                csv_summary = yearly_summary.to_csv(index=False)
                st.download_button(
                    label="Download yearly summary",
                    data=csv_summary,
                    file_name=f'climate_events_summary_{selected_country_folder}.csv',
                    mime='text/csv',
                )

            # Add disaster type summary
            st.subheader("Disaster Type Summary")
            disaster_summary = country_weather.groupby('Disaster Type').agg({
                'Total Deaths': 'sum',
                'Total Affected': 'sum',
                'Year': 'count'
            }).reset_index()
            st.dataframe(disaster_summary)
            
            csv_disaster = disaster_summary.to_csv(index=False)
            st.download_button(
                label="Download disaster type summary",
                data=csv_disaster,
                file_name=f'disaster_type_summary_{selected_country_folder}.csv',
                mime='text/csv',
            )
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
