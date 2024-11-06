import pandas as pd
from collections import defaultdict
from typing import Dict, List, Tuple, Set
from datetime import datetime
import sys
from io import StringIO

def clean_value(value) -> str:
    """Clean and standardize string values, treating empty and None as empty string."""
    if pd.isna(value) or value is None or str(value).strip() == '':
        return ''
    return str(value).strip()

def create_composite_key(row: pd.Series, elements: List[str]) -> str:
    """Creates a composite key from specified elements."""
    values = []
    mapping = {
        'title': 'Title',
        'h1': 'metadata-h1-contents',
        'meta_description': 'Meta Description'
    }
    for element in elements:
        values.append(clean_value(row[mapping[element]]))
    return '|'.join(values)

def find_duplicates(df: pd.DataFrame, elements: List[str], require_nonempty: bool = True) -> Dict:
    """
    Finds duplicates based on specified elements.
    If require_nonempty is True, all specified elements must have non-empty values.
    """
    mapping = {
        'title': 'Title',
        'h1': 'metadata-h1-contents',
        'meta_description': 'Meta Description'
    }
    
    # Find duplicates
    duplicates = defaultdict(list)
    for idx, row in df.iterrows():
        # Skip if any required element is empty
        if require_nonempty:
            skip = False
            for element in elements:
                if clean_value(row[mapping[element]]) == '':
                    skip = True
                    break
            if skip:
                continue
            
        composite = create_composite_key(row, elements)
        duplicates[composite].append({
            'url': row['Full URL'],
            'title': clean_value(row['Title']),
            'h1': clean_value(row['metadata-h1-contents']),
            'meta_description': clean_value(row['Meta Description'])
        })
    
    # Filter out non-duplicates
    return {k: v for k, v in duplicates.items() if len(v) > 1}

def find_single_element_duplicates(df: pd.DataFrame, element: str, exclude_urls: Set[str]) -> Dict:
    """Find duplicates of a single element, excluding specified URLs."""
    mapping = {
        'title': 'Title',
        'h1': 'metadata-h1-contents',
        'meta_description': 'Meta Description'
    }
    
    column = mapping[element]
    print(f"\nAnalyzing {element} duplicates:")
    print(f"Total rows before exclusions: {len(df)}")
    
    # Create working copy of dataframe
    df_working = df[~df['Full URL'].isin(exclude_urls)].copy()
    print(f"Rows after URL exclusions: {len(df_working)}")
    
    # Remove rows where the element is empty
    df_working = df_working[df_working[column].notna()]
    df_working = df_working[df_working[column].str.strip() != '']
    print(f"Rows with non-empty {element}: {len(df_working)}")
    
    duplicates = defaultdict(list)
    for idx, row in df_working.iterrows():
        value = clean_value(row[column])
        duplicates[value].append({
            'url': row['Full URL'],
            'title': clean_value(row['Title']),
            'h1': clean_value(row['metadata-h1-contents']),
            'meta_description': clean_value(row['Meta Description'])
        })
    
    # Filter to only groups with duplicates
    duplicates = {k: v for k, v in duplicates.items() if len(v) > 1}
    print(f"Found {len(duplicates)} duplicate groups for {element}")
    
    if duplicates:
        print("Sample duplicate values:")
        for i, (value, pages) in enumerate(list(duplicates.items())[:3], 1):
            print(f"{i}. '{value}' ({len(pages)} pages)")
    
    return duplicates

def get_urls_from_duplicates(duplicates: Dict) -> Set[str]:
    """Extract all URLs from a duplicates dictionary."""
    urls = set()
    for pages in duplicates.values():
        for page in pages:
            urls.add(page['url'])
    return urls

def export_duplicate_report(duplicates: Dict, filename: str, description: str):
    """Exports duplicate findings to a CSV file with a description row."""
    if not duplicates:
        return False
        
    # Create rows for the CSV
    duplicate_rows = []
    
    # Add description as first row
    duplicate_rows.append({
        'Group ID': 'REPORT DESCRIPTION',
        'URL': description,
        'Title': '',
        'H1': '',
        'Meta Description': ''
    })
    
    # Add a blank row after description
    duplicate_rows.append({
        'Group ID': '',
        'URL': '',
        'Title': '',
        'H1': '',
        'Meta Description': ''
    })
    
    # Add duplicate groups
    for group_id, pages in enumerate(duplicates.values(), 1):
        for page in pages:
            duplicate_rows.append({
                'Group ID': group_id,
                'URL': page['url'],
                'Title': page['title'],
                'H1': page['h1'],
                'Meta Description': page['meta_description']
            })
    
    pd.DataFrame(duplicate_rows).to_csv(filename, index=False)
    return True

def analyze_duplicates(data: pd.DataFrame):
    """Analyzes and reports on duplicate content in the specified order."""
    # Capture output for the analysis report
    old_stdout = sys.stdout
    analysis_output = StringIO()
    sys.stdout = analysis_output
    
    print("\n=== SEO Duplicate Content Analysis Report ===")
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Track URLs to exclude from subsequent reports
    excluded_urls = set()
    
    # 1. Find and report full duplicates (all 3 elements match)
    full_elements = ['title', 'h1', 'meta_description']
    full_duplicates = find_duplicates(data, full_elements, require_nonempty=True)
    
    if export_duplicate_report(full_duplicates, 'duplicate_full_matches.csv',
                             "FULL DUPLICATES REPORT: Pages where Title, Meta Description, AND H1 are identical"):
        print(f"Found {len(full_duplicates)} groups of full duplicates")
        print("Exported to 'duplicate_full_matches.csv'\n")
        excluded_urls.update(get_urls_from_duplicates(full_duplicates))
    
    # 2. Find title + h1 duplicates (excluding previous URLs)
    title_h1_elements = ['title', 'h1']
    title_h1_duplicates = find_duplicates(data[~data['Full URL'].isin(excluded_urls)], 
                                        title_h1_elements, require_nonempty=True)
    
    if export_duplicate_report(title_h1_duplicates, 'duplicate_title_h1_matches.csv',
                             "TITLE + H1 DUPLICATES REPORT: Pages where Title and H1 match (excluding previous reports)"):
        print(f"Found {len(title_h1_duplicates)} groups of Title + H1 duplicates")
        print("Exported to 'duplicate_title_h1_matches.csv'\n")
        excluded_urls.update(get_urls_from_duplicates(title_h1_duplicates))
    
    # 3. Find title + meta description duplicates (excluding previous URLs)
    title_meta_elements = ['title', 'meta_description']
    title_meta_duplicates = find_duplicates(data[~data['Full URL'].isin(excluded_urls)], 
                                          title_meta_elements, require_nonempty=True)
    
    if export_duplicate_report(title_meta_duplicates, 'duplicate_title_meta_matches.csv',
                             "TITLE + META DUPLICATES REPORT: Pages where Title and Meta Description match (excluding previous reports)"):
        print(f"Found {len(title_meta_duplicates)} groups of Title + Meta duplicates")
        print("Exported to 'duplicate_title_meta_matches.csv'\n")
        excluded_urls.update(get_urls_from_duplicates(title_meta_duplicates))
    
    # 4. Find individual element duplicates (excluding all previous URLs)
    for element in ['title', 'h1', 'meta_description']:
        element_duplicates = find_single_element_duplicates(data, element, excluded_urls)
        
        if element_duplicates:
            element_name = element.replace('_', ' ').title()
            filename = f'duplicate_{element}_only_matches.csv'
            description = f"DUPLICATE {element_name}S REPORT: Pages where only the {element_name} matches (excluding all previous reports)"
            
            if export_duplicate_report(element_duplicates, filename, description):
                print(f"Found {len(element_duplicates)} groups of {element_name}-only duplicates")
                print(f"Exported to '{filename}'")
    
    # Restore stdout and save analysis report
    sys.stdout = old_stdout
    
    # Save the analysis report to a dated file
    date_str = datetime.now().strftime('%Y%m%d')
    analysis_filename = f'duplicate_analysis_{date_str}.txt'
    with open(analysis_filename, 'w') as f:
        f.write(analysis_output.getvalue())
    
    # Print the analysis to console as well
    print(analysis_output.getvalue())
    print(f"\nAnalysis report saved to {analysis_filename}")

def main():
    # Read the data
    try:
        data = pd.read_csv('kay-h1.csv')
        analyze_duplicates(data)
    except FileNotFoundError:
        print("Error: Could not find 'kay-h1.csv'. Please make sure the file exists in the current directory.")
    except Exception as e:
        print(f"Error: An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()