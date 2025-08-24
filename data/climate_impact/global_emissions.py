import pandas as pd
import os

def process_global_emissions(input_path, output_path):
    """
    Process Our World in Data global CO2 emissions

    Args:
        input_path(str): Path to the EM-DAT Excel file
        output_path(str): Path to save processed parquet file
        

    Returns:
        pd.DataFrame: Processed global CO2 emissions summary.
    """

    # Read the data
    df = pd.read_csv(input_path)

    # Filter to only global/world level (not individual countries)
    global_df = df[df['country'] == 'World'] 

    # Selecr only relevent emission columns for analysis
    global_emissions = global_df[['year', 'co2', 'co2_including_luc', 'total_ghg']].copy()

    # Remove rows where CO2 data is missing
    global_emissions = global_emissions.dropna(subset=['co2'])

    # Changes 'year' to 'Year', 'co2' to 'Co2', etc.
    global_emissions.columns = global_emissions.columns.str.capitalize()
    cols = global_emissions.columns.str.replace('Co2', 'CO\u2082')
    global_emissions.columns = cols  
    
    # Save if output path exists
    if output_path:
        output_dir = os.path.dirname(output_path)

        # Create the output directory if it doesn't already exist
        # exist_ok=True prevents errors if the directory already exists
        os.makedirs(output_dir, exist_ok=True)

        # Print confirmation
        global_emissions.to_parquet(output_path, index=False)
        print(f"Global emissions data saved to {output_path}")

    return global_emissions