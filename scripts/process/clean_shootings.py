#!/usr/bin/env python3
"""
Clean and validate Philadelphia shooting data.

Standardizes fields, validates coordinates, and prepares data for analysis.
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import get_latest_file, save_csv, load_config
from src.trauma_desert.logging_utils import get_logger, StepLogger, log_dataframe_info

# Configure logging
logger = get_logger(__name__)

# Philadelphia bounding box for coordinate validation
PHILA_BBOX = {
    "min_lat": 39.86,
    "max_lat": 40.14,
    "min_lng": -75.28,
    "max_lng": -74.95,
}


def clean_shootings() -> Path:
    """
    Clean and validate shooting data.
    
    Returns:
        Path to the cleaned output file.
    """
    # Find the latest raw shooting file
    input_file = get_latest_file(PATHS.raw, "shootings_*.csv")
    if not input_file:
        raise FileNotFoundError("No shooting data file found in data/raw/")
    
    logger.info(f"Loading raw data from: {input_file}")
    df = pd.read_csv(input_file)
    initial_count = len(df)
    logger.info(f"  Initial records: {initial_count:,}")
    
    with StepLogger("Parsing and standardizing date/time fields", logger):
        # Parse date field
        df['date_'] = pd.to_datetime(df['date_'], errors='coerce')
        
        # Extract temporal components
        df['year'] = df['date_'].dt.year
        df['month'] = df['date_'].dt.month
        df['day_of_week'] = df['date_'].dt.dayofweek  # 0=Monday, 6=Sunday
        df['day_name'] = df['date_'].dt.day_name()
        
        # Parse time if available
        if 'time' in df.columns:
            df['hour'] = pd.to_datetime(df['time'], format='%H:%M:%S', errors='coerce').dt.hour
        
        # Date range
        min_date = df['date_'].min()
        max_date = df['date_'].max()
        logger.info(f"  Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}")
        
        # Check for null dates
        null_dates = df['date_'].isna().sum()
        if null_dates > 0:
            logger.warning(f"  Records with null dates: {null_dates}")
    
    with StepLogger("Validating coordinates", logger):
        # Check for null coordinates
        null_coords = df['lat'].isna() | df['lng'].isna()
        logger.info(f"  Records with null coordinates: {null_coords.sum()}")
        
        # Check for coordinates outside Philadelphia
        outside_bbox = (
            (df['lat'] < PHILA_BBOX['min_lat']) |
            (df['lat'] > PHILA_BBOX['max_lat']) |
            (df['lng'] < PHILA_BBOX['min_lng']) |
            (df['lng'] > PHILA_BBOX['max_lng'])
        )
        outside_count = (outside_bbox & ~null_coords).sum()
        logger.info(f"  Records outside Philadelphia bbox: {outside_count}")
        
        # Flag invalid coordinates
        df['valid_coords'] = ~null_coords & ~outside_bbox
        valid_count = df['valid_coords'].sum()
        logger.info(f"  Records with valid coordinates: {valid_count:,} ({valid_count/len(df)*100:.1f}%)")
    
    with StepLogger("Standardizing categorical fields", logger):
        # Standardize race field
        race_map = {
            'B': 'Black',
            'W': 'White', 
            'H': 'Hispanic',
            'A': 'Asian',
            'I': 'Other',
            'U': 'Unknown',
            '': 'Unknown',
        }
        df['race_clean'] = df['race'].fillna('U').map(lambda x: race_map.get(str(x).upper().strip(), 'Other'))
        
        logger.info("  Race distribution:")
        for race, count in df['race_clean'].value_counts().items():
            logger.info(f"    {race}: {count:,} ({count/len(df)*100:.1f}%)")
        
        # Standardize sex field
        df['is_male'] = df['sex'].fillna('U').str.upper().str.strip() == 'M'
        
        # Standardize fatal field
        df['is_fatal'] = df['fatal'].fillna(0).astype(int) == 1
        fatal_count = df['is_fatal'].sum()
        logger.info(f"  Fatal shootings: {fatal_count:,} ({fatal_count/len(df)*100:.1f}%)")
        
        # Create age groups
        df['age'] = pd.to_numeric(df['age'], errors='coerce')
        df['age_group'] = pd.cut(
            df['age'],
            bins=[0, 17, 24, 34, 44, 100],
            labels=['0-17', '18-24', '25-34', '35-44', '45+'],
            right=True
        )
        
        logger.info("  Age group distribution:")
        for age, count in df['age_group'].value_counts().sort_index().items():
            logger.info(f"    {age}: {count:,}")
    
    with StepLogger("Creating analysis flags", logger):
        # Location flags (inside/outside) - handle both Y/N and 0/1 formats
        def to_bool(series):
            """Convert Y/N or 0/1 to boolean."""
            return series.fillna('').astype(str).str.upper().str.strip().isin(['Y', 'YES', '1', 'TRUE'])
        
        df['is_outside'] = to_bool(df['outside'])
        df['is_inside'] = to_bool(df['inside'])
        
        # Officer involved
        df['is_officer_involved'] = to_bool(df['officer_involved'])
        officer_count = df['is_officer_involved'].sum()
        logger.info(f"  Officer-involved shootings: {officer_count:,}")
    
    with StepLogger("Removing invalid records", logger):
        # Keep only records with valid coordinates for spatial analysis
        df_clean = df[df['valid_coords']].copy()
        removed = initial_count - len(df_clean)
        logger.info(f"  Removed {removed} records with invalid coordinates")
        logger.info(f"  Final record count: {len(df_clean):,}")
    
    with StepLogger("Checking for duplicates", logger):
        # Check for potential duplicates (same date, location, and demographics)
        dup_cols = ['date_', 'lat', 'lng', 'race', 'sex', 'age']
        potential_dups = df_clean.duplicated(subset=dup_cols, keep=False).sum()
        if potential_dups > 0:
            logger.warning(f"  Potential duplicate records: {potential_dups}")
        else:
            logger.info("  No duplicate records found")
    
    with StepLogger("Saving cleaned data", logger):
        # Select and order columns for output
        output_cols = [
            # Identifiers
            'objectid', 'dc_key',
            # Location
            'lat', 'lng', 'location', 'dist',
            # Time
            'date_', 'year', 'month', 'day_of_week', 'day_name', 'hour',
            # Demographics
            'race_clean', 'is_male', 'age', 'age_group',
            # Incident details
            'wound', 'is_fatal', 'is_outside', 'is_inside', 'is_officer_involved',
            # Latino flag
            'latino',
        ]
        
        # Keep only columns that exist
        output_cols = [c for c in output_cols if c in df_clean.columns]
        df_clean = df_clean[output_cols]
        
        # Rename for clarity
        df_clean = df_clean.rename(columns={'race_clean': 'race', 'date_': 'date'})
        
        output_file = PATHS.processed / "shootings_clean.csv"
        save_csv(df_clean, output_file)
        logger.info(f"  Saved to: {output_file}")
        
        log_dataframe_info(df_clean, "Final dataset", logger)
    
    return output_file


if __name__ == "__main__":
    output_path = clean_shootings()
    print(f"\n✅ Shooting data cleaned: {output_path}")

