import os
import glob
import pandas as pd

def detect_header_rows(filepath, sheet_name, anchor=None, keywords=None, lookahead=15):
    """
    Detects header rows in an Excel sheet using anchor text or keywords:
    
    Args:
        filepath (str): Path to the Excel file to analyse
        sheet_name (str): Name of Excel sheet to examine
        anchor (str): Exact text string to search for in cells.
        keywords (list): List of keywords to search as a fallback
        lookahead (int): Number of rows to scan from the top
    Returns:
        list: List of row indices for the header (assumes 2-row header structure)
    """

    # Read data
    preview = pd.read_excel(filepath, sheet_name=sheet_name, nrows=lookahead, header=None)
    target_row = None

    # Iterate through each row in the preview
    for i, row in preview.iterrows():
        # Check each cell in the current row
        for cell in row:
            # Skip empty/NaN cells
            if pd.isna(cell):
                continue

            # Convert cell content to lowercase string for case sensitivity
            cell_str = str(cell).lower()

            # Checl for any anchor matches
            if anchor and anchor.lower() in cell_str:
                target_row = i
                break

            # Check for any keyword matches
            if keywords and any(k.lower() in cell_str for k in keywords):
                target_row = i
                break
        # Stop searching after match is found
        if target_row is not None:
            break
    # Raise error if none is found
    if target_row is None:
        raise ValueError("No header row detected with provided anchor or keywords.")

    # Return a 2-row header range starting from detected row
    return list(range(target_row, target_row + 2))  


def read_excel_with_detected_header(filepath, sheet_name, anchor=None, keywords=None, flatten=True):
    """
    Reads Excel with auto-detected header rows using an anchor or keywords.
    Cleans multi-index headers if needed and handles units in first dat row.

    Args:
        filepath (str): Path to the Excel file to read
        sheet_name (str): Nme of the Excel sheet to read
        anchor (str): Exact text string to search for in cells.
        keywords (list): List of keywords to search as a fallback
        flatten (bool): Whether multi-index column will be flattened

    Returns:
        pd.DataFrame: DataFrame with detected headers and flattens them
    """

    # Detects where header rows are located
    header_rows = detect_header_rows(filepath, sheet_name, anchor=anchor, keywords=keywords)
    
    # Read Excel file using detected header row positions
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=header_rows)

    # If flatten is True and there is multi-level column header
    if flatten and isinstance(df.columns, pd.MultiIndex):
        def clean_column(col):
            """
            Clean and flatten multi-index column names by keeping only relevant parts.
                Args:
                    col (tuple): Multi-index column tuple (e.g., ('Level1', 'Level2', 'Level3'))
                    
                Returns:
                    str: Cleaned, flattened column name
            """
            # Convert all parts of the column to strings and remove whitespace
            parts = [str(part).strip() for part in col if pd.notna(part)]

            # Common UNFCCC keywords
            relevant_keywords = [
                # Categories
                'SINK CATEGORIES', 'SOURCE', 'EMISSION', 'ACTIVITY', 'FACTOR',
                
                # Greenhouse Gases
                'CO2', 'CH4', 'N2O', 'SF6', 'HFC', 'PFC', 'NF3', 'NF', 
                'NO', 'NMVOC', 'CO', 'SO',
                
                # Energy Content
                'GCV', 'NCV', 'NCV/GCV', 'NCV/GCV (5)'
                
                # Mass Units
                '(kt)', 'Mt', 't', 'kg',
                
                # Energy Units  
                'PJ', '(TJ)',
                
                # Emission Factors
                '(t/TJ)', '(kg/TJ)', 'kg/t', '(t/TJ)', '(kg/TJ)', '(kg/t)',
                '(kt)', '(Mt)', '(t)', '(kg)', '(PJ)', '(TJ)',
                
                # CO2 Equivalents
                'CO₂ equivalents', 'CO₂-eq', 'CO2-eq', 'CO2 eq', 
                't CO₂ eq', 'kt CO₂ eq', 'Mt CO₂ eq',
                
                # Other UNFCCC Terms
                'captured', 'transported', 'injected', 'stored',
                'Reference year', 'Base year', '1990', 'Change from',
                'NaN'
            ]

            # Keep only parts that contain relevant greenhouse gas or category keywords
            keep_parts = [p for p in parts if any(unit in p for unit in relevant_keywords)]
            
            if not keep_parts:
                keep_parts = parts

            # Join the kept parts with spaces and clean up
            return ' '.join(keep_parts).strip()

        # Apply the cleaning function to all columns
        df.columns = [clean_column(col) for col in df.columns]
    
    # Handle units in first data row
    if len(df) > 0:
        first_row = df.iloc[0]
        new_columns = []
        
        # Unit patterns for first row detection
        unit_patterns = [
            '(TJ)', '(kt)', '(Mt)', '(t)', '(kg)', '(PJ)',
            '(t/TJ)', '(kg/TJ)', '(kg/t)', 
            'NCV/GCV', 'GCV', 'NCV',
            'CO₂-eq', 'CO2-eq', 'CO2 eq',
            't CO₂ eq', 'kt CO₂ eq', 'Mt CO₂ eq', 'NCV/GCV (5)'
        ]
        
        for i, col_name in enumerate(df.columns):
            if i < len(first_row):
                first_val = str(first_row.iloc[i]).strip()
                
                # Check if first row value is a unit
                is_unit = (first_val in unit_patterns or 
                          any(pattern in first_val for pattern in unit_patterns) or
                          ('(' in first_val and ')' in first_val and len(first_val) < 20))
                
                if is_unit and first_val not in ['NaN', '', 'nan']:
                    new_col_name = f"{col_name} {first_val}".strip()
                    new_columns.append(new_col_name)
                else:
                    new_columns.append(col_name)
            else:
                new_columns.append(col_name)
        
        # Update column names
        df.columns = new_columns
        
        # Check if first row is all units (should be in header)
        first_row_is_units = all(
            str(val).strip() in unit_patterns + ['NaN', '', 'nan'] or
            any(pattern in str(val) for pattern in unit_patterns) or
            ('(' in str(val) and ')' in str(val) and len(str(val)) < 20)
            for val in first_row if pd.notna(val)
        )
        
        if first_row_is_units:
            df = df.drop(df.index[0]).reset_index(drop=True)

    return df


def extract_year_from_filename(filename):
    """
    Extracts year from filename following pattern like 'GBR-CRT-2025-V0.6-1990-20250415-091720.xlsx'
    Args:
        filename (str): The filename to parse (with or without extension)
    
    Returns:
        tuple:
            - country_code (str): 3-letter ISO country code (e.g., 'GBR')
            - year (int): The reporting year (e.g., 1990)
            Returns (None, None) if parsing fails
    """
    # Remove the file extension and split by '-'
    basename = os.path.splitext(filename)[0]  
    parts = basename.split('-')
    try:
        # Check if we have enough parts for the expected format
        if len(parts) >= 5:
            # 3 letter country code
            country_code = parts[0]
            # This is the reporting year
            year = int(parts[4])  
            return country_code, year
        else:
             # Not enough parts in filename - doesn't match expected format
            raise ValueError("Filename format is incorrect")
    except (IndexError, ValueError) as e:
        print(f"Filename parsing error: {filename} -> {e}")
        return None, None
 
