"""
Emissions Trends page for the GHG Emissions Dashboard.
Shows detailed emissions trends analysis for individual countries.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from helper.utils import get_co2_column, get_other_gas_columns


def render_emissions_trends_page(sidebar_data):
    """Enhanced emissions trends page with visual storytelling
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
    
    # Access data
    total_emissions_df = sidebar_data['total_emissions_df']
    selected_country_folder = sidebar_data['selected_country_folder']
    year_range = sidebar_data['year_range']
    
    st.header(f"{selected_country_folder}'s Emissions Trends")
    st.write("Greenhouse gases (GHGs) differ in how they're produced and how strongly they warm the planet. "
    "In this section, you can explore how **total emissions have changed over time** for different gases, based on national inventories submitted via the **UNFCCC Common Reporting Tables (CRTs)**.")
    
    
    
    # Get gas columns
    co2_column = get_co2_column(total_emissions_df)
    other_gas_columns = get_other_gas_columns(total_emissions_df)
    
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
    
    
    # Summary metrics increase ir decrease
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
    # Create  plot with annotations
    with d1: 
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
