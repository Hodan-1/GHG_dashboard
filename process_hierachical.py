def get_category(category_str):
    category_str = str(category_str).strip()

    # Special case for total and memo items header
    if category_str.startswith('Total'):
        return {
            'sector': None,
            'subsector': None,
            'sub_subsector': None,
            'sub_sub_subsector': None,
            'label': category_str,
            'is_memo': False
        }
    
    # Check if this is a memo item
    is_memo = (category_str.startswith('Memo items:') or 
               category_str.startswith('1.D.') or 
               category_str.startswith('5.F.') or 
               category_str.startswith('Indirect N2O') or 
               category_str.startswith('Indirect CO2'))

    try:
        # Try to split on space, if that fails, use the whole string
        split_parts = category_str.split(" ", 1)
        if len(split_parts) == 2:
            level, label = split_parts
        else:
            # If no space found, try to find where numbers/dots end
            for i, character in enumerate(category_str):
                if not (character.isdigit() or character == '.' or character == 'A'):
                    level = category_str[:i].strip()
                    label = category_str[i:].strip()
                    break
            else:
                level = category_str
                label = category_str
    
        parts = level.strip('.').split(".")
        sector = parts[0] if len(parts) > 0 else None
        subsector = parts[1] if len(parts) > 1 else None
        sub_subsector = parts[2] if len(parts) > 2 else None
        sub_sub_subsector = parts[3] if len(parts) > 3 else None

        return {
            'sector': sector,
            'subsector': subsector,
            'sub_subsector': sub_subsector,
            'sub_sub_subsector': sub_sub_subsector,
            'label': label.strip(),
            'is_memo': is_memo
        }
    except Exception as e:
        # If anything goes wrong, return a default structure
        return {
            'sector': None,
            'subsector': None,
            'sub_subsector': None,
            'sub_sub_subsector': None,
            'label': category_str,
            'is_memo': is_memo
        }


def process_hierarchical_data(df):
    category_col = None
    for col in df.columns:
        if 'GREENHOUSE GAS SOURCE AND SINK CATEGORIES' in col:
            category_col = col
            break
    if not category_col:
        raise ValueError("Category column not found")

    sectors, subsectors, sub_subsectors, labels, levels, is_memo = [], [], [], [],[],[]
    
    memo_start_idx = None
    for idx, value in enumerate(df[category_col]):
        if 'Memo items:' in str(value):
            memo_start_idx = idx
            break
    
    for cat_str in df[category_col].astype(str):
        categories = get_category(cat_str)

        sectors.append(categories['sector'])
        subsectors.append(categories['subsector'])
        sub_subsectors.append(categories['sub_subsector'])
        labels.append(categories['label'])
        is_memo.append(categories['is_memo'])

        if categories['label'].startswith('Total'):
            levels.append('Total')
        elif categories['sector'] and not categories['subsector']:
            levels.append('Sector')
        elif categories['subsector'] and not categories['sub_subsector']:
            levels.append('Subsector')
        elif categories['sub_subsector']:
            levels.append('Sub-subsector')
        else:
            levels.append('Unknown')

    df = df.copy()
    df['Sector'] = sectors
    df['Subsector'] = subsectors
    df['Sub_subsector'] = sub_subsectors
    df['Label'] = labels
    df['Level'] = levels
    df['Is_Memo'] = is_memo

    main_df = df[~df['Is_Memo']]
    memo_df = df[df['Is_Memo']]
                    
    total_df = main_df[main_df['Level'] == 'Total']
    sector_df = main_df[main_df['Level'] == 'Sector']
    subsector_df = main_df[main_df['Level'] == 'Subsector']
    sub_subsector_df = main_df[main_df['Level'] == 'Sub-subsector']

    # Processing Summary
    print(f"\nProcessing Summary:")
    print(f"Found {0 if total_df.empty else len(total_df)} total rows")
    print(f"Found {0 if sector_df.empty else len(sector_df)} sector rows")
    print(f"Found {0 if subsector_df.empty else len(subsector_df)} subsector rows")
    print(f"Found {0 if sub_subsector_df.empty else len(sub_subsector_df)} sub-subsector rows")
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

    if not memo_df.empty:
        print("\nMemo Items:")
        print(memo_df[category_col].tolist())

    return total_df, sector_df, subsector_df, sub_subsector_df, memo_df

