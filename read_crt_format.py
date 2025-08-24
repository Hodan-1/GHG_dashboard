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
    Cleans multi-index headers if needed.

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

            # Keep only parts that contain relevant greenhouse gas or category keywords
            keep_parts = [p for p in parts if any(unit in p for unit in 
                          ['SINK CATEGORIES', 'CO2', 'CH4', 'N2O', 'SF6', 
                           'HFC', 'PFC', '(kt)', 'NF', 'NO', 'NMVOC', 'CO', 'SO'])]
            
            # Join the kept parts with spaces and clean up
            return ' '.join(keep_parts).strip()

        # Apply the cleaning function to all columns
        df.columns = [clean_column(col) for col in df.columns]

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
 
