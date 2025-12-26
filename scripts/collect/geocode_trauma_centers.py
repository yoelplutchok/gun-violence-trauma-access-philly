#!/usr/bin/env python3
"""
Geocode trauma center addresses using the Census Geocoding API.

This script takes the manually compiled trauma center list and adds
latitude/longitude coordinates using the free Census Bureau geocoder.
"""

import sys
import time
from pathlib import Path

import pandas as pd
import requests

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import get_latest_file, save_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Census Geocoder API endpoint
GEOCODER_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"


def geocode_address(address: str, city: str, state: str, zip_code: str) -> tuple:
    """
    Geocode a single address using the Census Geocoder API.
    
    Args:
        address: Street address
        city: City name
        state: State abbreviation
        zip_code: ZIP code
        
    Returns:
        Tuple of (latitude, longitude) or (None, None) if geocoding fails.
    """
    full_address = f"{address}, {city}, {state} {zip_code}"
    
    params = {
        "address": full_address,
        "benchmark": "Public_AR_Current",
        "format": "json",
    }
    
    try:
        response = requests.get(GEOCODER_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Check if we got a match
        matches = data.get("result", {}).get("addressMatches", [])
        if matches:
            coords = matches[0].get("coordinates", {})
            lat = coords.get("y")
            lng = coords.get("x")
            return (lat, lng)
        else:
            logger.warning(f"  No match found for: {full_address}")
            return (None, None)
            
    except Exception as e:
        logger.error(f"  Geocoding error for {full_address}: {e}")
        return (None, None)


def geocode_trauma_centers() -> Path:
    """
    Geocode all trauma centers in the manual list.
    
    Returns:
        Path to the geocoded output file.
    """
    # Find the latest trauma centers file
    input_file = get_latest_file(PATHS.manual, "trauma_centers_*.csv")
    if not input_file:
        raise FileNotFoundError("No trauma centers file found in data/manual/")
    
    logger.info(f"Loading trauma centers from: {input_file}")
    df = pd.read_csv(input_file)
    logger.info(f"  Found {len(df)} trauma centers")
    
    # Geocode each address
    latitudes = []
    longitudes = []
    
    with StepLogger("Geocoding trauma center addresses", logger):
        for idx, row in df.iterrows():
            logger.info(f"  Geocoding: {row['hospital_name']}")
            lat, lng = geocode_address(
                row["address"],
                row["city"],
                row["state"],
                str(row["zip"]),
            )
            latitudes.append(lat)
            longitudes.append(lng)
            
            # Rate limiting - be nice to the Census API
            time.sleep(0.5)
    
    # Add coordinates to dataframe
    df["latitude"] = latitudes
    df["longitude"] = longitudes
    
    # Check for failures
    missing = df["latitude"].isna().sum()
    if missing > 0:
        logger.warning(f"  {missing} addresses failed to geocode")
    else:
        logger.info("  All addresses geocoded successfully!")
    
    # Save geocoded file
    output_file = PATHS.processed / "trauma_centers_geocoded.csv"
    save_csv(df, output_file)
    logger.info(f"  Saved to: {output_file}")
    
    # Display results
    logger.info("\nGeocoded trauma centers:")
    for _, row in df.iterrows():
        logger.info(f"  {row['hospital_name']}: ({row['latitude']:.4f}, {row['longitude']:.4f})")
    
    return output_file


if __name__ == "__main__":
    output_path = geocode_trauma_centers()
    print(f"\n✅ Geocoding complete: {output_path}")

