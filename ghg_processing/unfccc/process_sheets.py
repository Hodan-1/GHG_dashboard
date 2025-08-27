import os
import glob
import pandas as pd
from .header_detector import read_excel_with_detected_header, extract_year_from_filename
from .process_hierarchy import process_hierarchical_data
from .save_gases import save_gas_level_parquet

def process_summary_sheet(sheet_name, folder_path, output_folder, save_csv=False):
    """
    Process a specific summary sheet from all Excel files in the folder

    Args:
        sheet_name(str): Name of Excel sheet to process.
        folder_path(str): Path to folder contaning files for a specific county
        output_folder(str): Path where processed parquet files will be saved
        save_csv (Boolean): Option on wheather csv version is saved alongside output. Default is 
        false

    Returns:
        None: Saves processed data to parquet files and prints progress messages
    """
    
    # Get country name from the folder path
    country_name = os.path.basename(folder_path)

    print(f"Processing {sheet_name} for {country_name}...")
    
    # Define gas types with Unicode subscripts for better display
    GAS_STANDARD_NAMES = {
        'CO2 (1) CO2 equivalents (kt ) (2)': 'CO\u2082 (kt)',
        'CO2': 'CO\u2082 (kt)',
        'CH4': 'CH\u2084 (kt)',
        'N2O': 'N\u2082O (kt)',
        'HFCs': 'HFCs (kt)',
        'PFCs': 'PFCs (kt)',
        'Unspecified mix of HFCs and PFCs': 'HFC+PFC Mix (kt)',
        'SF6': 'SF\u2086 (kt)',
        'NF3': 'NF\u2083 (kt)',
    }

    # Define hierarchical levels for organising emissions data
    levels = ['total', 'sectors', 'subsectors', 'sub_subsectors', 'sub_sub_subsectors', 'level_5', 'level_6', 'level_7', 'level_8', 'memo_items']
    
    # Create main country directories (no gas-specific subdirectories)
    country_output = os.path.join(output_folder, country_name)
    for level in levels:
        os.makedirs(os.path.join(country_output, level), exist_ok=True)
    

    if save_csv:
        # Create CSV output directory ( outside processed_data)
        csv_output_folder = os.path.join(os.path.dirname(output_folder), 'csv_view')
        csv_country_output = os.path.join(csv_output_folder, country_name)
        for level in levels:
            os.makedirs(os.path.join(csv_country_output, level), exist_ok=True)

    # Process each file in the country's folder
    for filepath in glob.glob(os.path.join(folder_path, "*.xlsx")):
        try:
            # Read summary sheet
            # Anchor locates data table within sheet (Change depending on sheet)
            df = read_excel_with_detected_header(filepath, sheet_name, anchor='GREENHOUSE GAS SOURCE', flatten=True)
            
            # Standardise column names
            # Apply Unicode subscript column names
            new_columns = []
            for col in df.columns:
                # Remove whitespace
                col_clean = col.strip()
                if col_clean in GAS_STANDARD_NAMES:
                    new_columns.append(GAS_STANDARD_NAMES[col_clean])
                else:
                    new_columns.append(col)
            df.columns = new_columns

            # Find the category column
            category_col = None
            for col in df.columns:
                if 'GREENHOUSE GAS SOURCE AND SINK CATEGORIES' in col:
                    category_col = col
                    break
            
            if not category_col:
                raise ValueError("Category column not found")

            # Keep the category column and seperate from numeric data
            categories = df[category_col]

            # Convert other columns to numeric, coercing errors to NaN
            numeric_df = df.drop(columns=[category_col]).apply(pd.to_numeric, errors='coerce')

            # Recombine the category column back
            df = pd.concat([categories, numeric_df], axis=1)

            # Drop rows that are completely empty but keep the category column
            df = df.dropna(axis=0, how='all', subset=numeric_df.columns)
            
            # Drop columns that are completely empty
            df = df.dropna(axis=1, how='all')

            # Define years and GHG keywords (with subscript)
            years_table10s6 = [str(year) for year in range(1990, 2023+1)]
            # Use new column names
            ghg_keywords = ['CO\u2082', 'CH\u2084', 'N\u2082O', 'SF\u2086', 'HFC', 'PFC', 'NF\u2083',
                          'Base year (1)', 'Change from base to latest'] + years_table10s6

            # Keep category column containing any GHG keywords
            cols_to_keep = [category_col] + [col for col in df.columns 
                                           if any(k in col for k in ghg_keywords)]

            df = df[cols_to_keep]
            
            # Extract year, country code from filename
            country_code, year = extract_year_from_filename(os.path.basename(filepath))
            if not country_code or not year:
                print(f"Skipping {filepath}: Could not extract country code or year")
                continue
            
            # Add sheet name to DataFrame
            df['Sheet'] = sheet_name
            df['Country'] = country_name.upper()
            df['Year'] = year

            
            #  Process the flat data into hierarchical structure based on UNFCCC categories
            # This separates totals, sectors, subsectors, etc. into different DataFrames
            total_df, sector_df, subsector_df, sub_subsector_df, sub_sub_subsector_df, level_5_df, level_6_df, level_7_df, level_8_df, memo_df = process_hierarchical_data(df)

            # Get additional levels by re-processing the data
            # Extract the deeper levels that aren't returned by the main function
            category_col_internal = None
            for col in df.columns:
                if 'GREENHOUSE GAS SOURCE AND SINK CATEGORIES' in col:
                    category_col_internal = col
                    break

            
            # Create filename using country name with sheet name and year
            base_filename = f"{country_code.lower()}_{sheet_name}_{year}"
            
            # Option 1: Save combined files as Parquet
            # groups all gas types together within each organisation
            level_dfs = {
                'total': total_df,
                'sectors': sector_df,
                'subsectors': subsector_df,
                'sub_subsectors': sub_subsector_df,
                'sub_sub_subsectors': sub_sub_subsector_df,
                'level_5': level_5_df,
                'level_6': level_6_df,
                'level_7': level_7_df,
                'level_8': level_8_df,
                'memo_items': memo_df
            }

            # Save each hierarchical level as a separate parquet file
            for level, df_to_save in level_dfs.items():
                if not df_to_save.empty:
                    output_path = os.path.join(
                        country_output,
                        level,
                        f"{base_filename}_{level}.parquet"
                    )
                    df_to_save.to_parquet(output_path, index=False)

                    # If save_csv is True
                    if save_csv:
                        # Save CSV too - good for users to view output
                        csv_output_path = os.path.join(
                            csv_country_output,
                            level,
                            f"{base_filename}_{level}.csv"
                        )
                        df_to_save.to_csv(csv_output_path, index=False)


            # Option 2: Save species-specific files as Parquet
            for original_name, standardised_gas in GAS_STANDARD_NAMES.items():
                gas_type = standardised_gas.split()[0].lower()
                
                # Define paths for each level
                level_paths = {
                    'total': os.path.join(output_folder, country_name, gas_type, 'total', f"{base_filename}_total.parquet"),
                    'sectors': os.path.join(output_folder, country_name, gas_type, 'sectors', f"{base_filename}_sectors.parquet"),
                    'subsectors': os.path.join(output_folder, country_name, gas_type, 'subsectors', f"{base_filename}_subsectors.parquet"),
                    'sub_subsectors': os.path.join(output_folder, country_name, gas_type, 'sub_subsectors', f"{base_filename}_sub_subsectors.parquet"),
                    'sub_sub_subsectors': os.path.join(output_folder, country_name, gas_type, 'sub_sub_subsectors', f"{base_filename}_sub_sub_subsectors.parquet"),
                    'level_5': os.path.join(output_folder, country_name, gas_type, 'level_5', f"{base_filename}_level_5.parquet"),
                    'level_6': os.path.join(output_folder, country_name, gas_type, 'level_6', f"{base_filename}_level_6.parquet"),
                    'level_7': os.path.join(output_folder, country_name, gas_type, 'level_7', f"{base_filename}_level_7.parquet"),
                    'level_8': os.path.join(output_folder, country_name, gas_type, 'level_8', f"{base_filename}_level_8.parquet"),
                    'memo_items': os.path.join(output_folder, country_name, gas_type, 'memo_items', f"{base_filename}_memo_items.parquet")
                }

                # Save each level for this gas type
                save_gas_level_parquet(total_df, standardised_gas, level_paths['total'], save_csv=save_csv)
                save_gas_level_parquet(sector_df, standardised_gas, level_paths['sectors'], save_csv=save_csv)
                save_gas_level_parquet(subsector_df, standardised_gas, level_paths['subsectors'], save_csv=save_csv)
                save_gas_level_parquet(sub_subsector_df, standardised_gas, level_paths['sub_subsectors'], save_csv=save_csv)
                save_gas_level_parquet(sub_sub_subsector_df, standardised_gas, level_paths['sub_sub_subsectors'], save_csv=save_csv)
                save_gas_level_parquet(level_5_df, standardised_gas, level_paths['level_5'], save_csv=save_csv)
                save_gas_level_parquet(level_6_df, standardised_gas, level_paths['level_6'], save_csv=save_csv)
                save_gas_level_parquet(level_7_df, standardised_gas, level_paths['level_7'], save_csv=save_csv)
                save_gas_level_parquet(level_8_df, standardised_gas, level_paths['level_8'], save_csv=save_csv)
                save_gas_level_parquet(memo_df, standardised_gas, level_paths['memo_items'], save_csv=save_csv)

            print(f"Processed {sheet_name} for year {year}")
            
        except Exception as e:
            print(f"Error processing {sheet_name} in {filepath}: {e}")

    # After processing all files, combine years for both approaches
    
    # APPROACH 1: Combine files for the hierarchical level approach
    # This creates time series datasets for each organisational level
    for level in levels:
        level_path = os.path.join(country_output, level)
        parquet_files = glob.glob(os.path.join(level_path, "*.parquet"))
        if parquet_files:
            combined_df = pd.concat([pd.read_parquet(f) for f in parquet_files])
            combined_path = os.path.join(level_path, f"{country_name}_{level}_combined.parquet")
            combined_df.to_parquet(combined_path, index=False)
            
            # Save combined CSV too
            if save_csv:
                csv_level_path = os.path.join(csv_country_output, level)
                csv_combined_path = os.path.join(csv_level_path, f"{country_name}_{level}_combined.csv")
                combined_df.to_csv(csv_combined_path, index=False)

            #  Remove individual year files 
            # (optional - if user wants to keep remove these two lines below)
            for f in parquet_files:
                os.remove(f)

    # APPROACH 2: Combine files for the gas-specific approach
    # This creates time series datasets for each gas type at each level
    for gas in GAS_STANDARD_NAMES.values():
        gas_type = gas.split()[0].lower()
        for level in levels:
            level_path = os.path.join(output_folder, country_name, gas_type, level)
            parquet_files = glob.glob(os.path.join(level_path, f"*_{gas_type}.parquet"))
            
            if parquet_files:
                combined_df = pd.concat([pd.read_parquet(f) for f in parquet_files])
                combined_path = os.path.join(level_path, f"{country_name}_{level}_{gas_type}_combined.parquet")
                combined_df.to_parquet(combined_path, index=False)
                
                # Save combined CSV too. If true
                if save_csv:
                    csv_level_path = os.path.join(csv_output_folder, country_name, gas_type, level)
                    os.makedirs(csv_level_path, exist_ok=True)
                    csv_combined_path = os.path.join(csv_level_path, f"{country_name}_{level}_{gas_type}_combined.csv")
                    combined_df.to_csv(csv_combined_path, index=False)
            
                # Optionally remove individual year files
                for f in parquet_files:
                    os.remove(f)

    print(f"Completed processing {sheet_name} for {country_name}")
