"""
Sector Distribution page for the GHG Emissions Dashboard.
Shows detailed breakdown of emissions by sector over time.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from helper.utils import get_co2_column, get_other_gas_columns
from data_content.gas_information import gas_explanations
from data_content.chart_explanations import chart_explanations
from data_content.sector_goals import sector_goals
from data_content.policy_data import policy_data


def render_sector_distribution_page(sidebar_data):
    """Render the Sector Distribution page

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
    total_emissions_df = sidebar_data['total_emissions_df']
    data_dict = sidebar_data['data_dict']
    year_range = sidebar_data['year_range']
    selected_country_folder = sidebar_data['selected_country_folder']
    selected_hierarchy = sidebar_data['selected_hierarchy']
    selected_sectors = sidebar_data['selected_sectors']  

    # Display page header and description
    st.header("Sector Distribution")
    st.write("Here, you can explore a detailed breakdown of greenhouse gas emissions by sector over time. Below the charts, you'll find an overview of the specific climate policies implemented in the selected country to address these emissions.")
    
    # Check if emissions data is available
    if total_emissions_df is not None:
        # Get CO2 and other gas columns
        co2_column = get_co2_column(total_emissions_df)
        other_gas_columns = get_other_gas_columns(total_emissions_df)
        
        # Get sector data
        sector_df = data_dict.get(selected_hierarchy)
        
        #Filter based on sector and year range
        if sector_df is not None:
            # Filter sector data
            filtered_sector_df = sector_df[
                (sector_df['Year'].between(year_range[0], year_range[1])) &
                (sector_df['GREENHOUSE GAS SOURCE AND SINK CATEGORIES'].isin(selected_sectors))
            ]

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

            # Create tabs for chart and table view
            chart_tab1, table_tab1 = st.tabs(["Chart", "Table"])
            #Display bar chart
            with chart_tab1:
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
            
            #Table download view
            with table_tab1:
                st.dataframe(latest_data_melted)
                csv = latest_data_melted.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'sector_emissions_by_gas_{latest_year}.csv',
                    mime='text/csv',
                )

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
            chart_tab2, table_tab2 = st.tabs(["Chart", "Table"])

            # Option 1: Filter out negative values
            pie_data = latest_data[latest_data[selected_gas_tab2_pie] > 0]  # Only keep positive values

            # Pie chart display
            with chart_tab2:
                fig_pie = px.pie(
                    pie_data,
                    values=selected_gas_tab2_pie,
                    names='GREENHOUSE GAS SOURCE AND SINK CATEGORIES',
                    title=f'Distribution of {selected_gas_tab2_pie} by Sector ({latest_year})'
                )
                st.plotly_chart(fig_pie, use_container_width=True, key='Sector pie chart')
            
            #Table download
            with table_tab2:
                pie_data = latest_data[['GREENHOUSE GAS SOURCE AND SINK CATEGORIES', selected_gas_tab2_pie]]
                st.dataframe(pie_data)
                csv = pie_data.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'sector_distribution_{selected_gas_tab2_pie}_{latest_year}.csv',
                    mime='text/csv',
                )

            # Display the explanation for the selected gas
            if selected_gas_tab2_pie in gas_explanations:
                st.write(gas_explanations[selected_gas_tab2_pie])

            st.markdown("---")
            
            # Stacked area chart showing emissions by sector over time
            t1, t2, table_tab3 = st.tabs(['Area Chart', 'Line Chart', 'Table'])
            st.subheader("Emissions by Sector Over Time")
            #area Chart
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

            #Line chart
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

            # Download view
            with table_tab3:
                time_series_data = filtered_sector_df[['Year', 'GREENHOUSE GAS SOURCE AND SINK CATEGORIES', selected_gas_tab2_pie]]
                st.dataframe(time_series_data)
                csv = time_series_data.to_csv(index=False)
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name=f'sector_emissions_timeseries_{selected_gas_tab2_pie}.csv',
                    mime='text/csv',
                )

            #  Display policy information based on hierarchy level
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
                # Subsector display 
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

            # Create sector selector for climate commitments
            selected_sector_goal = st.selectbox(
                "Select a sector to view global climate commitments:",
                options=list(sector_goals.key())
            )

            #Display commitments
            if selected_sector_goal in sector_goals:
                st.markdown(f"### Global Climate Commitments for {selected_sector_goal}")
                st.markdown(sector_goals[selected_sector_goal])
            else:
                st.warning("No global climate commitment data found for this sector.")