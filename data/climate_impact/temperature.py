import pandas as pd
import os

def process_temperature_anomalies(input_path, output_path= None, year_range):
    """
    Process NASA GISS temperature anomoloy data.

    Args: 
       input_path (str): Path to NASA GISS CSV file
       output_path (str): Path to save processed parquet file
       year_range (tuple): (start_year, end_year) to filter data
    
    Returns:
        pd.DataFrame: Procesed temoearture data with columns: Year, Temperature_Anomaly

    """
    # Load CSV, skip first row
    df = pd.read_csv(input_path, skiprows=1) 

    # Extract 'Year' and 'J-D' columns
        # 'J-D' represents the January-December annual mean
    df_filtered = df[['Year', 'J-D']].copy()

    # Filter for years 1990-2024 to match emissions data
    start_year, end_year = year_range
    df_filtered = df_filtered[df_filtered['Year'].between(start_year, end_year)]

    # Renamed J-D column for user clarity
    df_filtered = df_filtered.rename(columns={'J-D': 'Temperature_Anomaly'})

    if output_path:
        # Save if output path input
        output_dir = os.path.dirname(output_path)

        # Create directory if it doesn't exist
         # exist_ok=True prevents errors if the directory already exists
        os.makedirs(output_dir, exist_ok=True)

        # Save the processed data as a parquet file (efficient format)
        # index=False prevents saving the DataFrame index as a separate column  
        df_filtered.to_parquet(output_path, index=False)
        print(f"Temperature anomaly data saved to: {output_path}")
        
    return df_filtered