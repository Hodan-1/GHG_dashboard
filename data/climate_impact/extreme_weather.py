import pandas as pd
import os

def process_extreme_weather_data(input_path, output_path=None, hazards=None):
    """
    Process EM-DAT extreme weather data

    Args:
        input_path(str): Path to the EM-DAT Excel file
        output_path(str): Path to save processed parquet file
        hazards(list): List of disaster types to include. Uses set list if None.

    Returns:
        pd.DataFrame: Processed extreme weather summary by country year and disaster type.
    """

    # Check if hazards is given if not use default list
    if hazards is None:
        # Define hazards (keeping all countries)
        # Represents climate related natural disasters
         hazards = ['Wildfire', 'Flood', 'Drought', 'Heatwave', 'Extreme temperature', 'Storm', 'Mass movement (wet)']
    
    # Read the data
    extreme_weather = pd.read_excel(input_path)

    # Filter for hazards only (no country filter)
    # Removes non-weather related disasters
    filtered_weather = extreme_weather[
        extreme_weather['Disaster Type'].isin(hazards)
    ]
    
    # Standardise 'Start Year' column to macth rest of datasets
    # Convert year to integer
    filtered_weather['Year'] = filtered_weather['Start Year'].astype(int)
    #Standardise columns to match UNFCCC Naming conventions
    filtered_weather['Country'] = filtered_weather['Country'].replace('United Kingdom of Great Britain and Northern Ireland', 'United Kingdom')
    
    # Create aggregated summary using 'Country', year and disaster type
    summary = (
        filtered_weather
        .groupby(["Country", "Year", "Disaster Type"])[
            ["Total Deaths", "Total Affected", "Total Damage ('000 US$)"]
        ]
        .sum()
        .reset_index()
    )
    
    # Save if output path provided
    if output_path:
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        
        # Save as parquet for efficency
        summary.to_parquet(output_path, index=False)

        # Create the output directory if it doesn't already exist
        # exist_ok=True prevents errors if the directory already exists
        os.makedirs(output_dir, exist_ok=True)  

        # Print confirmation messages
        print(f"Extreme weather data saved to: {output_path}")
        print(f"Countries included: {summary['Country'].nunique()}")
        print(f"Year range: {summary['Year'].min()}-{summary['Year'].max()}")
    
    return summary
