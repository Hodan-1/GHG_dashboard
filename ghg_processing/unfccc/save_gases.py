import os
import glob
import pandas as pd

def save_gas_level_parquet(df, gas_col, output_path, index_col='Year', column_col='Label', value_col=None):
    """
    Converts the dataframe into year x sector format and saves to Parquet for specific gas types.
    This function takes emissions data in long format and converts it to wide format where:
        - Rows represent years (or other index values)
        - Columns represent emission source categories (sectors, subsectors, etc.)
        - Values represent emission quantities for the specified gas type

    Args:
        df (pd.DataFrame): Input DataFrame containing emissions data
        gas_col (str): Name of the column containing the gas data to extract 
        output_path (str):  Path where the parquet file should be saved
        index_col (str): Column to use as index in table. Defaults to 'Year'
        column_col (str): Column to use as columns in table. Defaults to 'Label'
        value_col (str): Column to use as values in  table. Defaults to gas_col if None
    
    Returns:
        None: Function saves data to file and prints confimation message.    
    """

    # Use the gas column if no value is provided
    if value_col is None:
        value_col = gas_col

    # Check if the specified gas column exist in DataFrame
    if gas_col not in df.columns:
        print(f"Skipping {gas_col} — column not found.")
        return

    # Handle Unicode subscripts properly
    gas_name = gas_col.split()[0].lower()
    
    # Convert Unicode subscripts back to regular characters for file naming
    gas_type_mapping = {
        'CO\u2082': 'co2', 
        'CH\u2084': 'ch4',
        'N\u2082O': 'n2o',
        'SF\u2086': 'sf6'
    }
    
    # Use mapping or original if not found
    gas_type = gas_type_mapping.get(gas_name, gas_name)  

    # Modify the output path to include the gas type in the filename
    output_dir = os.path.dirname(output_path)
    filename = os.path.basename(output_path)
    filename_without_ext = os.path.splitext(filename)[0]
    new_filename = f"{filename_without_ext}_{gas_type}.parquet"
    new_output_path = os.path.join(output_dir, new_filename)

    # Ensure directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create pivot table to transform data from long to wide format
    pivot_df = df[[index_col, column_col, gas_col]].pivot_table(
        index=index_col, columns=column_col, values=value_col, aggfunc='first'
    ).sort_index()

    # Save to parquet format
    pivot_df.to_parquet(new_output_path)
    print(f"Saved {gas_type} data to {new_output_path}")
