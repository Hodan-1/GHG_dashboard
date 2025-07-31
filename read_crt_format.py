import os
import glob
import pandas as pd

def detect_header_rows(filepath, sheet_name, anchor=None, keywords=None, lookahead=15):
    """
    Detects header rows in an Excel sheet using either:
    - an exact anchor string (preferred), or
    - a list of keywords (fallback).
    """
    preview = pd.read_excel(filepath, sheet_name=sheet_name, nrows=lookahead, header=None)
    target_row = None

    for i, row in preview.iterrows():
        for cell in row:
            if pd.isna(cell):
                continue
            cell_str = str(cell).lower()

            if anchor and anchor.lower() in cell_str:
                target_row = i
                break

            if keywords and any(k.lower() in cell_str for k in keywords):
                target_row = i
                break

        if target_row is not None:
            break

    if target_row is None:
        raise ValueError("No header row detected with provided anchor or keywords.")

    return list(range(target_row, target_row + 2))  # assume 2-row header


def read_excel_with_detected_header(filepath, sheet_name, anchor=None, keywords=None, flatten=True):
    """
    Reads Excel with auto-detected header rows using an anchor or keywords.
    Cleans multi-index headers if needed.
    """
    header_rows = detect_header_rows(filepath, sheet_name, anchor=anchor, keywords=keywords)
    df = pd.read_excel(filepath, sheet_name=sheet_name, header=header_rows)

    if flatten and isinstance(df.columns, pd.MultiIndex):
        def clean_column(col):
            parts = [str(part).strip() for part in col if pd.notna(part)]
            keep_parts = [p for p in parts if any(unit in p for unit in 
                          ['SINK CATEGORIES', 'CO2', 'CH4', 'N2O', 'SF6', 
                           'HFC', 'PFC', '(kt)', 'NF', 'NO', 'NMVOC', 'CO', 'SO'])]
            return ' '.join(keep_parts).strip()

        df.columns = [clean_column(col) for col in df.columns]

    return df

def extract_year_from_filename(filename):
    """
    Extracts year from filename following pattern like 'GBR-CRT-2025-V0.6-1990-20250415-091720.xlsx'
    Returns: (country_code, year)
    """
    parts = filename.split('-')
    try:
        if len(parts) >= 5:
            country_code = parts[0]
            year = int(parts[4])  # This is the "1990" year
            return country_code, year
        else:
            raise ValueError("Filename format is incorrect")
    except (IndexError, ValueError) as e:
        print(f"Filename parsing error: {filename} -> {e}")
        return None, None
 
