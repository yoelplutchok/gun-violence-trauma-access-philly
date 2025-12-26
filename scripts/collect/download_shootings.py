#!/usr/bin/env python3
"""
Download Philadelphia shooting victims data from OpenDataPhilly.

Source: https://www.opendataphilly.org/datasets/shooting-victims/
API: CARTO SQL API
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import update_manifest
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# OpenDataPhilly CARTO API endpoint for shooting victims
# This query includes lat/lng extracted from the geometry
SHOOTINGS_API_URL = (
    "https://phl.carto.com/api/v2/sql?"
    "q=SELECT+*,+ST_Y(the_geom)+AS+lat,+ST_X(the_geom)+AS+lng+FROM+shootings"
    "&filename=shootings&format=csv&skipfields=cartodb_id"
)

SOURCE_URL = "https://www.opendataphilly.org/datasets/shooting-victims/"


def download_shootings() -> Path:
    """
    Download shooting victims data from OpenDataPhilly.
    
    Returns:
        Path to the downloaded CSV file.
    """
    # Ensure data directory exists
    PATHS.raw.mkdir(parents=True, exist_ok=True)
    
    # Create filename with date stamp
    today = datetime.now().strftime("%Y-%m-%d")
    output_file = PATHS.raw / f"shootings_{today}.csv"
    
    with StepLogger("Downloading shooting data from OpenDataPhilly", logger):
        logger.info(f"  API URL: {SHOOTINGS_API_URL[:80]}...")
        
        # Download the data
        response = requests.get(SHOOTINGS_API_URL, timeout=120)
        response.raise_for_status()
        
        # Save raw response
        with open(output_file, "wb") as f:
            f.write(response.content)
        
        logger.info(f"  Saved to: {output_file}")
    
    # Load and validate
    with StepLogger("Validating downloaded data", logger):
        df = pd.read_csv(output_file)
        
        # Basic stats
        row_count = len(df)
        logger.info(f"  Total records: {row_count:,}")
        
        # Check date range
        if "date_" in df.columns:
            df["date_"] = pd.to_datetime(df["date_"], errors="coerce")
            min_date = df["date_"].min()
            max_date = df["date_"].max()
            date_range = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
            logger.info(f"  Date range: {date_range}")
        else:
            date_range = "Unknown"
            logger.warning("  Could not determine date range (no 'date_' column)")
        
        # Check for coordinates
        has_coords = df["lat"].notna().sum()
        missing_coords = df["lat"].isna().sum()
        logger.info(f"  Records with coordinates: {has_coords:,}")
        if missing_coords > 0:
            logger.warning(f"  Records missing coordinates: {missing_coords:,}")
        
        # Check fatal vs non-fatal
        if "fatal" in df.columns:
            fatal_count = df["fatal"].sum()
            fatal_pct = (fatal_count / row_count) * 100
            logger.info(f"  Fatal shootings: {fatal_count:,} ({fatal_pct:.1f}%)")
        
        # Log column names for reference
        logger.info(f"  Columns: {', '.join(df.columns.tolist())}")
    
    # Update manifest
    with StepLogger("Updating data manifest", logger):
        update_manifest(
            filename=output_file.name,
            source_url=SOURCE_URL,
            row_count=row_count,
            date_range=date_range,
            notes="Philadelphia shooting victims from OpenDataPhilly CARTO API",
        )
        logger.info(f"  Manifest updated: {PATHS.manifest_file}")
    
    return output_file


if __name__ == "__main__":
    output_path = download_shootings()
    print(f"\n✅ Download complete: {output_path}")

