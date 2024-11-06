# SEO Duplicate Content Analyzer

A Python tool for analyzing and identifying duplicate content across web pages, focusing on SEO elements such as titles, H1 headings, and meta descriptions.

## Features

- Identifies full duplicates (matching title, H1, and meta description)
- Finds partial duplicates (title + H1, title + meta description)
- Detects single-element duplicates
- Generates detailed CSV reports for each duplicate type
- Creates a comprehensive analysis summary
- Excludes previously reported duplicates from subsequent analyses

## Prerequisites

- Python 3.6+
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd seo-duplicate-analyzer
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your input CSV file named `kay-h1.csv` in the project directory. The file should contain the following columns:
   - Full URL
   - Title
   - metadata-h1-contents
   - Meta Description

2. Run the script:
```bash
python seo_duplicate_analyzer.py
```

## Output

The script generates several output files:

1. `duplicate_full_matches.csv` - Pages with identical title, H1, and meta description
2. `duplicate_title_h1_matches.csv` - Pages with matching titles and H1s
3. `duplicate_title_meta_matches.csv` - Pages with matching titles and meta descriptions
4. `duplicate_title_only_matches.csv` - Pages with duplicate titles only
5. `duplicate_h1_only_matches.csv` - Pages with duplicate H1s only
6. `duplicate_meta_description_only_matches.csv` - Pages with duplicate meta descriptions only
7. `duplicate_analysis_YYYYMMDD.txt` - Detailed analysis report

## Functions

- `clean_value()` - Standardizes string values and handles empty/None values
- `create_composite_key()` - Creates unique keys for comparing multiple elements
- `find_duplicates()` - Identifies duplicates based on specified elements
- `find_single_element_duplicates()` - Finds duplicates of individual elements
- `analyze_duplicates()` - Main analysis function that coordinates the entire process

## License

[Add your chosen license here]

## Contributing

[Add contribution guidelines here]