import pandas as pd
import os
import glob

def get_category(category_str):
    """
    Parse a category string into hierarchical levels.

    Args:
        category_str (str): The category string to parse, which includes sector subsector etc
    
    Returns:
        dict: A dictionary containing:
            - 'levels': Different hierarchical sectors.
            - 'label': Original label of category
            - 'is_memo': Boolean indicating if category is a memo item
            - 'is_numbered': Boolean indicating if the UNFCCC labelling in place.

    """

    # Ensure the input is a string and remove leading/trailing whitespace
    category_str = str(category_str).strip()

    # Special case for total and memo items header
    if category_str.startswith('Total'):
        return {
            'levels':[],
            'label': category_str,
            'is_memo': False,
            'is_numbered': False
        }
    
    # Check if this is a memo item
    is_memo = (category_str.startswith('Memo items:') or 
               category_str.startswith('1.D.') or 
               category_str.startswith('5.F.') or 
               category_str.startswith('Indirect N2O') or 
               category_str.startswith('Indirect CO2'))

    # Check if category is numbered (starts with digit followed by period)
    if category_str and category_str[0].isdigit() and '.' in category_str:
        
        # Try to split on space, if that fails, use the whole string
        split_parts = category_str.split(" ", 1)
        if len(split_parts) == 2:
            #if split is successful assign level and label
            level, label = split_parts
        else:
            # If no split treat whole string as a level
            level = category_str
            label = category_str
    
        # Split the level by dots to get hierarchical components
        parts = level.strip('.').split(".")
        return {
            # e.g ['1','A','1','a','i']
            'levels': parts,
            'label': label.strip(),
            'is_memo': is_memo,
            'is_numbered': True
        }
    else:
        # This is a non-numbered item (contextual relationship)
        return {
            # Fill based on context
            'levels': [],
            'label': category_str,
            'is_memo': is_memo,
            'is_numbered': False
            
        }


def process_hierarchical_data(df):
    """
    Process a DataFrame to extract hierarchical data from GHG categories

    Args:
        df (pd.DataFrame): DataFrame containing GHG data with a category column.

    Returns:
        tuple: Five DataFrames containing:
        - total_df: DataFrame for total catgories
        - sector_df: DataFrame for sector catgories
        - subsector_df: DataFrame for subsector catgories
        - sub_subsector_df: DataFrame for sub-subsector catgories
        - memo_df: DataFrame for memo items
    """

    # Identify the category column in the DataFrame
    category_col = None
    for col in df.columns:
        if 'GREENHOUSE GAS SOURCE AND SINK CATEGORIES' in col:
            category_col = col
            break
    if not category_col:
        raise ValueError("Category column not found")

    # Process each category string in the DataFrame
    parsed = [get_category(cat_str) for cat_str in df[category_col].astype(str)]

    current_context = []

    # Process each parsed item and assign context to non-numbered items
    for i, p in enumerate(parsed):
        if p['is_numbered'] and p['levels']:
            # Update context with this numbered item
            current_context = p['levels'].copy()
        elif not p['is_numbered'] and not p['label'].startswith('Total') and not p['is_memo']:
            # This is a non-numbered item, assign to current level
            if current_context:
                # Make it one level deeper than current 
                p['levels'] = current_context + ['child']
            else:
                # No context available, treat as top level
                p['levels'] = ['1']

    
    # Determine max categories
    max_len = max(len(p['levels']) for p in parsed if p['levels'])

    # Extend level names to handle deeper hierarchies
    level_names = ['Sector', 'Subsector', 'Sub_subsector', 'Sub_sub_subsector', 'Level_5', 'Level_6', 'Level_7', 'Level_8']
    if max_len > len(level_names):
        for i in range(len(level_names)+1, max_len+1):
            # stop naming at 8
            level_names.append(f'Level_{i}')  

    # Build  DataFrame
    df = df.copy()
    for i, name in enumerate(level_names):
        df[name] = [p['levels'][i] if i < len(p['levels']) else None for p in parsed]

    df['Label'] = [p['label'] for p in parsed]
    df['Is_Memo'] = [p['is_memo'] for p in parsed]

    # Add more classification into categories
    levels = []
    for i, row in df.iterrows():
        # Determine the levl of category
        if row['Label'].startswith('Total'):
            levels.append('Total')
        elif row['Sector'] and not row['Subsector']:
            levels.append('Sector')
        elif row['Subsector'] and not row['Sub_subsector']:
            levels.append('Subsector')
        elif row['Sub_subsector'] and not row['Sub_sub_subsector']:
            levels.append('Sub-subsector')
        elif row['Sub_sub_subsector'] and not row.get('Level_5'):
            levels.append('Sub-sub-subsector')
        elif row.get('Level_5') and not row.get('Level_6'):
            levels.append('Level-5')
        elif row.get('Level_6') and not row.get('Level_7'):
            levels.append('Level-6')
        elif row.get('Level_7') and not row.get('Level_8'):
            levels.append('Level-7')
        elif row.get('Level_8'):
            levels.append('Level-8')
        else:
            levels.append('Unknown')

    df['Level'] = levels

    # Seperate main data from memo items
    main_df = df[~df['Is_Memo']]
    memo_df = df[df['Is_Memo']]

    # Create seperate DataFrames for each level                
    total_df = main_df[main_df['Level'] == 'Total']
    sector_df = main_df[main_df['Level'] == 'Sector']
    subsector_df = main_df[main_df['Level'] == 'Subsector']
    sub_subsector_df = main_df[main_df['Level'] == 'Sub-subsector']
    sub_sub_subsector_df = main_df[main_df['Level'] == 'Sub-sub-subsector']
    level_5_df = main_df[main_df['Level'] == 'Level-5']
    level_6_df = main_df[main_df['Level'] == 'Level-6']
    level_7_df = main_df[main_df['Level'] == 'Level-7']
    level_8_df = main_df[main_df['Level'] == 'Level-8']

    # Processing Summary
    print(f"\nProcessing Summary:")
    print(f"Found {0 if total_df.empty else len(total_df)} total rows")
    print(f"Found {0 if sector_df.empty else len(sector_df)} sector rows")
    print(f"Found {0 if subsector_df.empty else len(subsector_df)} subsector rows")
    print(f"Found {0 if sub_subsector_df.empty else len(sub_subsector_df)} sub-subsector rows")
    print(f"Found {0 if sub_sub_subsector_df.empty else len(sub_sub_subsector_df)} sun-sub-subsector rows")
    print(f"Found {0 if level_5_df.empty else len(level_5_df)} level 5 rows")
    print(f"Found {0 if level_6_df.empty else len(level_6_df)} level 6 rows")
    print(f"Found {0 if level_7_df.empty else len(level_7_df)} level 7 rows")
    print(f"Found {0 if level_8_df.empty else len(level_8_df)} level 8 rows")
    print(f"Found {0 if memo_df.empty else len(memo_df)} memo items")

    # Detailed breakdown
    print("\nDetailed breakdown:")
    
    if not total_df.empty:
        print("\nTotal categories:")
        print(total_df[category_col].tolist())
    
    if not sector_df.empty:
        print("\nSectors:")
        print(sector_df[category_col].tolist())
    
    if not subsector_df.empty:
        # Group subsectors by their parent sector
        for sector_num in subsector_df['Sector'].unique():
            sector_subsectors = subsector_df[subsector_df['Sector'] == sector_num]
            if not sector_subsectors.empty:
                print(f"\nSubsectors for Sector {sector_num}:")
                print(sector_subsectors[category_col].tolist())
    
    if not sub_subsector_df.empty:
        # Group sub-subsectors by their parent sector and subsector
        for sector_num in sub_subsector_df['Sector'].unique():
            for subsector_code in sub_subsector_df[sub_subsector_df['Sector'] == sector_num]['Subsector'].unique():
                detailed = sub_subsector_df[
                    (sub_subsector_df['Sector'] == sector_num) & 
                    (sub_subsector_df['Subsector'] == subsector_code)
                ]
                if not detailed.empty:
                    print(f"\nDetailed breakdowns for {sector_num}.{subsector_code}:")
                    print(detailed[category_col].tolist())
    
    if not sub_sub_subsector_df.empty:
        print(f"\nSub-sub-subsectors:")
        print(sub_sub_subsector_df[category_col].tolist())

    if not level_5_df.empty:
        print(f"\nLevel-5 items:")
        print(level_5_df[category_col].tolist())

    if not level_6_df.empty:
        print(f"\nLevel-6 items:")
        print(level_6_df[category_col].tolist())

    if not memo_df.empty:
        print("\nMemo Items:")
        print(memo_df[category_col].tolist())

    return total_df, sector_df, subsector_df, sub_subsector_df, sub_sub_subsector_df, level_5_df, level_6_df, level_7_df, level_8_df, memo_df

