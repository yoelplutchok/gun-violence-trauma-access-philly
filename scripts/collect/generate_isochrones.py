#!/usr/bin/env python3
"""
Generate drive-time isochrones for trauma centers using OpenRouteService API.

Creates polygon geometries showing areas reachable within specified
time intervals from each Level I trauma center.
"""

import sys
import os
import time
from pathlib import Path

import geopandas as gpd
from shapely.geometry import shape
import requests
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_csv, load_config
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Load environment variables
load_dotenv(PATHS.root / ".env")

# OpenRouteService API configuration
ORS_API_URL = "https://api.openrouteservice.org/v2/isochrones/driving-car"

# Time intervals in seconds (5, 10, 15, 20, 30 minutes)
TIME_INTERVALS = [300, 600, 900, 1200, 1800]
TIME_LABELS = {300: 5, 600: 10, 900: 15, 1200: 20, 1800: 30}


def get_isochrones(lat: float, lng: float, api_key: str) -> dict:
    """
    Request isochrones from OpenRouteService API.
    
    Args:
        lat: Latitude of the center point
        lng: Longitude of the center point
        api_key: OpenRouteService API key
        
    Returns:
        GeoJSON response from the API
    """
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
    }
    
    body = {
        "locations": [[lng, lat]],  # ORS uses [lng, lat] order
        "range": TIME_INTERVALS,
        "range_type": "time",
        "attributes": ["total_pop"],  # Optional, can help with analysis
    }
    
    response = requests.post(ORS_API_URL, json=body, headers=headers, timeout=60)
    response.raise_for_status()
    
    return response.json()


def generate_all_isochrones() -> Path:
    """
    Generate isochrones for all Level I trauma centers.
    
    Returns:
        Path to the output GeoJSON file.
    """
    # Get API key
    api_key = os.getenv("OPENROUTESERVICE_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "OpenRouteService API key not found. "
            "Please set OPENROUTESERVICE_API_KEY in .env file."
        )
    
    # Load trauma centers
    trauma_file = PATHS.processed / "trauma_centers_geocoded.csv"
    if not trauma_file.exists():
        raise FileNotFoundError(
            f"Geocoded trauma centers not found at {trauma_file}. "
            "Run geocode_trauma_centers.py first."
        )
    
    df = load_csv(trauma_file)
    
    # Filter to Level I Adult trauma centers only (for GSW analysis)
    # Include both Adult and Pediatric Level I centers
    level_i = df[df['trauma_level'] == 'I'].copy()
    logger.info(f"Found {len(level_i)} Level I trauma centers")
    
    # For the main analysis, focus on Adult Level I centers
    # Pediatric centers handle children, not typical GSW patients
    adult_level_i = level_i[level_i['designation'] == 'Adult'].copy()
    logger.info(f"  Adult Level I centers: {len(adult_level_i)}")
    
    # Generate isochrones for each center
    all_features = []
    
    with StepLogger("Generating isochrones from OpenRouteService", logger):
        for idx, row in adult_level_i.iterrows():
            hospital_name = row['hospital_name']
            lat = row['latitude']
            lng = row['longitude']
            
            logger.info(f"  {hospital_name}...")
            
            try:
                result = get_isochrones(lat, lng, api_key)
                
                # Process each isochrone feature
                for feature in result.get('features', []):
                    # Add hospital info to properties
                    time_seconds = feature['properties']['value']
                    time_minutes = TIME_LABELS.get(time_seconds, time_seconds // 60)
                    
                    feature['properties']['hospital_name'] = hospital_name
                    feature['properties']['trauma_level'] = 'I'
                    feature['properties']['time_minutes'] = time_minutes
                    feature['properties']['hospital_lat'] = lat
                    feature['properties']['hospital_lng'] = lng
                    
                    all_features.append(feature)
                
                logger.info(f"    Generated {len(result.get('features', []))} isochrones")
                
            except requests.exceptions.HTTPError as e:
                logger.error(f"    API error for {hospital_name}: {e}")
                logger.error(f"    Response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
                continue
            
            # Rate limiting - respect API limits
            time.sleep(1.5)
    
    if not all_features:
        raise ValueError("No isochrones were generated. Check API key and rate limits.")
    
    with StepLogger("Saving isochrones to GeoJSON", logger):
        # Create GeoDataFrame
        geojson = {
            "type": "FeatureCollection",
            "features": all_features
        }
        
        # Convert to GeoDataFrame for validation
        gdf = gpd.GeoDataFrame.from_features(geojson, crs="EPSG:4326")
        
        # Remove any list-type columns (ORS returns some that GeoJSON doesn't support)
        for col in gdf.columns:
            if col != 'geometry' and gdf[col].apply(lambda x: isinstance(x, list)).any():
                logger.info(f"  Dropping list column: {col}")
                gdf = gdf.drop(columns=[col])
        
        logger.info(f"  Total isochrones: {len(gdf)}")
        logger.info(f"  Hospitals covered: {gdf['hospital_name'].nunique()}")
        logger.info(f"  Time intervals: {sorted(gdf['time_minutes'].unique())}")
        
        # Save to file
        PATHS.isochrones.mkdir(parents=True, exist_ok=True)
        output_file = PATHS.isochrones / "trauma_center_isochrones.geojson"
        gdf.to_file(output_file, driver="GeoJSON")
        logger.info(f"  Saved to: {output_file}")
    
    return output_file


if __name__ == "__main__":
    output_path = generate_all_isochrones()
    print(f"\n✅ Isochrones generated: {output_path}")

