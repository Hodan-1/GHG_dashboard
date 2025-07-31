def process_summary_sheet(sheet_name, folder_path, output_folder):
    """
    Process a specific summary sheet from all Excel files in the folder
    """
    print(f"Processing {sheet_name}...")
    
    # Get country name from the folder path
    country_name = os.path.basename(folder_path).lower()

    for filepath in glob.glob(os.path.join(folder_path, "*.xlsx")):
        try:
            # Read the specific summary sheet
            df = read_excel_with_detected_header(filepath, sheet_name, anchor='GREENHOUSE GAS SOURCE AND', flatten=True)
            
            # Standardise column names
            new_columns = []
            for col in df.columns:
                # Standardise CO2 column names
                if col == 'CO2' or col == 'CO2 (kt)' or col == 'Net CO2 (kt)':
                    new_columns.append('Net CO2 emissions/removals (kt)')
                #other gases just in case
                elif col == 'CH4' or col == 'CH4 (kt)':
                    new_columns.append('CH4 (kt)')
                elif col == 'N2O' or col == 'N2O (kt)':
                    new_columns.append('N2O (kt)')
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

            # Keep the category column
            categories = df[category_col]

            # Convert other columns to numeric, coercing errors to NaN
            numeric_df = df.drop(columns=[category_col]).apply(pd.to_numeric, errors='coerce')

            # Recombine the category column back
            df = pd.concat([categories, numeric_df], axis=1)

            # Drop rows that are completely empty but keep the category column
            df = df.dropna(axis=0, how='all', subset=numeric_df.columns)
            
            # Drop columns that are completely empty
            df = df.dropna(axis=1, how='all')

            # Define years and GHG keywords
            years_table10s6 = [str(year) for year in range(1990, 2023+1)]
            ghg_keywords = ['CO2', 'CH4', 'N2O', 'SF6', 'HFC', 'PFC',
                          'Base year (1)', 'Change from base to latest'] + years_table10s6

            # Keep category column containing any GHG keywords
            cols_to_keep = [category_col] + [col for col in df.columns 
                                           if any(k in col for k in ghg_keywords)]

            df = df[cols_to_keep]
            
            # Extract year
            country_code, year = extract_year_from_filename(os.path.basename(filepath))
            if not country_code or not year:
                print(f"Skipping {filepath}: Could not extract country code or year")
                continue
            
            # Add sheet name to DataFrame
            df['Sheet'] = sheet_name

            # Create directories using country name from folder
            country_output = os.path.join(output_folder, country_name)
            os.makedirs(os.path.join(country_output, 'total'), exist_ok=True)
            os.makedirs(os.path.join(country_output, 'sectors'), exist_ok=True)
            os.makedirs(os.path.join(country_output, 'subsectors'), exist_ok=True)
            os.makedirs(os.path.join(country_output, 'sub_subsectors'), exist_ok=True)
            os.makedirs(os.path.join(country_output, 'memo_items'), exist_ok=True)

            df['Country'] = country_name.upper()
            df['Year'] = year
            
            # Process into hierarchical structure
            total_df, sector_df, subsector_df, sub_subsector_df, memo_df = process_hierarchical_data(df)

            # Create filename with sheet name and year
            base_filename = f"{country_code.lower()}_{sheet_name}_{year}"
            
            # Save files
            if not total_df.empty:
                total_df.to_csv(
                    os.path.join(country_output, 'total', f"{base_filename}_total.csv"), 
                    index=False
                )
            
            if not sector_df.empty:
                sector_df.to_csv(
                    os.path.join(country_output, 'sectors', f"{base_filename}_sectors.csv"), 
                    index=False
                )
            
            if not subsector_df.empty:
                subsector_df.to_csv(
                    os.path.join(country_output, 'subsectors', f"{base_filename}_subsectors.csv"),
                    index=False
                )

            if not sub_subsector_df.empty:
                sub_subsector_df.to_csv(
                    os.path.join(country_output, 'sub_subsectors', f"{base_filename}_sub_subsectors.csv"),
                    index=False
                )

            if not memo_df.empty:
                memo_df.to_csv(
                    os.path.join(country_output, 'memo_items', f"{base_filename}_memo_items.csv"),
                    index=False
                )
                
            print(f"Processed {sheet_name} for year {year}")
            
        except Exception as e:
            print(f"Error processing {sheet_name} in {filepath}: {e}")