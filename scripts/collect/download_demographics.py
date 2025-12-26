#!/usr/bin/env python3
"""
Download demographic data from the Census Bureau API.

Fetches ACS 5-year estimates for Philadelphia census tracts including:
- Total population
- Race/ethnicity breakdown
- Poverty status
- Median household income
"""

import sys
from pathlib import Path

import pandas as pd
import requests

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import save_csv, load_config
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Census API configuration
# Using ACS 5-Year Estimates (2019-2023)
CENSUS_API_BASE = "https://api.census.gov/data/2022/acs/acs5"

# Philadelphia County = PA (42) + Philadelphia County (101)
STATE_FIPS = "42"
COUNTY_FIPS = "101"

# Variables to request:
# B01003_001E - Total population
# B02001_001E - Total population (race table)
# B02001_002E - White alone
# B02001_003E - Black or African American alone
# B02001_005E - Asian alone
# B03003_001E - Total Hispanic origin
# B03003_003E - Hispanic or Latino
# B19013_001E - Median household income
# B17001_001E - Poverty status - total
# B17001_002E - Poverty status - below poverty level
VARIABLES = [
    "B01003_001E",  # Total population
    "B02001_002E",  # White alone
    "B02001_003E",  # Black or African American alone
    "B02001_005E",  # Asian alone
    "B03003_003E",  # Hispanic or Latino
    "B19013_001E",  # Median household income
    "B17001_001E",  # Poverty universe total
    "B17001_002E",  # Below poverty level
]


def download_demographics() -> Path:
    """
    Download demographic data for Philadelphia census tracts.
    
    Returns:
        Path to the output CSV file.
    """
    PATHS.processed.mkdir(parents=True, exist_ok=True)
    
    with StepLogger("Fetching demographic data from Census API", logger):
        # Build API URL
        variables_str = ",".join(VARIABLES)
        url = (
            f"{CENSUS_API_BASE}"
            f"?get=NAME,{variables_str}"
            f"&for=tract:*"
            f"&in=state:{STATE_FIPS}&in=county:{COUNTY_FIPS}"
        )
        
        logger.info(f"  Requesting ACS 5-Year estimates...")
        
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"  Received data for {len(data) - 1} tracts")
    
    with StepLogger("Processing demographic data", logger):
        # First row is headers
        headers = data[0]
        rows = data[1:]
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Create GEOID from state + county + tract
        df['GEOID'] = df['state'] + df['county'] + df['tract']
        
        # Rename columns for clarity
        column_map = {
            'NAME': 'tract_name',
            'B01003_001E': 'total_population',
            'B02001_002E': 'white_alone',
            'B02001_003E': 'black_alone',
            'B02001_005E': 'asian_alone',
            'B03003_003E': 'hispanic_latino',
            'B19013_001E': 'median_household_income',
            'B17001_001E': 'poverty_universe',
            'B17001_002E': 'below_poverty',
        }
        df = df.rename(columns=column_map)
        
        # Convert to numeric (Census returns strings)
        numeric_cols = [
            'total_population', 'white_alone', 'black_alone', 'asian_alone',
            'hispanic_latino', 'median_household_income', 'poverty_universe',
            'below_poverty'
        ]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Handle Census Bureau's missing data encoding (-666666666)
        df['median_household_income'] = df['median_household_income'].replace(-666666666, pd.NA)
        
        # Calculate percentages
        df['pct_black'] = (df['black_alone'] / df['total_population'] * 100).round(1)
        df['pct_white'] = (df['white_alone'] / df['total_population'] * 100).round(1)
        df['pct_asian'] = (df['asian_alone'] / df['total_population'] * 100).round(1)
        df['pct_hispanic'] = (df['hispanic_latino'] / df['total_population'] * 100).round(1)
        df['pct_poverty'] = (df['below_poverty'] / df['poverty_universe'] * 100).round(1)
        
        # Keep relevant columns
        output_cols = [
            'GEOID', 'tract_name', 'total_population',
            'black_alone', 'pct_black',
            'white_alone', 'pct_white',
            'asian_alone', 'pct_asian',
            'hispanic_latino', 'pct_hispanic',
            'median_household_income',
            'below_poverty', 'pct_poverty'
        ]
        df = df[output_cols]
        
        # Summary statistics
        total_pop = df['total_population'].sum()
        avg_pct_black = df['pct_black'].mean()
        avg_pct_poverty = df['pct_poverty'].mean()
        
        logger.info(f"\nSummary statistics:")
        logger.info(f"  Total population: {total_pop:,}")
        logger.info(f"  Average % Black: {avg_pct_black:.1f}%")
        logger.info(f"  Average % Poverty: {avg_pct_poverty:.1f}%")
        logger.info(f"  Tracts with >50% Black: {(df['pct_black'] > 50).sum()}")
        logger.info(f"  Tracts with >30% Poverty: {(df['pct_poverty'] > 30).sum()}")
    
    with StepLogger("Saving demographic data", logger):
        output_file = PATHS.processed / "tract_demographics.csv"
        save_csv(df, output_file)
        logger.info(f"  Saved to: {output_file}")
    
    return output_file


if __name__ == "__main__":
    output_path = download_demographics()
    print(f"\n✅ Demographics downloaded: {output_path}")

