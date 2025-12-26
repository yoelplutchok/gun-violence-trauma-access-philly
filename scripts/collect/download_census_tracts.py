#!/usr/bin/env python3
"""
Download Philadelphia census tract boundaries from the Census Bureau.

Uses the Census TIGER/Line API to get tract boundaries for Philadelphia County.
"""

import sys
from pathlib import Path
import zipfile
import io

import geopandas as gpd
import requests

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_config
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Census TIGER/Line shapefiles URL (2023 tracts)
# Format: state FIPS code (42 = Pennsylvania)
TIGER_URL = "https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_42_tract.zip"

# Philadelphia County FIPS code
PHILADELPHIA_FIPS = "42101"


def download_census_tracts() -> Path:
    """
    Download and filter census tract boundaries for Philadelphia.
    
    Returns:
        Path to the output GeoJSON file.
    """
    PATHS.geo.mkdir(parents=True, exist_ok=True)
    
    with StepLogger("Downloading Pennsylvania census tracts from TIGER/Line", logger):
        logger.info(f"  URL: {TIGER_URL}")
        
        response = requests.get(TIGER_URL, timeout=120)
        response.raise_for_status()
        
        logger.info(f"  Downloaded {len(response.content) / 1024 / 1024:.1f} MB")
    
    with StepLogger("Extracting and filtering to Philadelphia County", logger):
        # Extract shapefile from zip
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            # Find the .shp file
            shp_files = [f for f in z.namelist() if f.endswith('.shp')]
            if not shp_files:
                raise ValueError("No shapefile found in download")
            
            # Extract all files to a temp location
            temp_dir = PATHS.geo / "temp_tiger"
            temp_dir.mkdir(exist_ok=True)
            z.extractall(temp_dir)
            
            shp_path = temp_dir / shp_files[0]
            logger.info(f"  Extracted: {shp_path.name}")
        
        # Load the shapefile
        gdf = gpd.read_file(shp_path)
        logger.info(f"  Total PA tracts: {len(gdf)}")
        
        # Filter to Philadelphia County (COUNTYFP = 101, or GEOID starts with 42101)
        phila_gdf = gdf[gdf['GEOID'].str.startswith(PHILADELPHIA_FIPS)].copy()
        logger.info(f"  Philadelphia tracts: {len(phila_gdf)}")
        
        # Clean up temp files
        for f in temp_dir.glob("*"):
            f.unlink()
        temp_dir.rmdir()
    
    with StepLogger("Saving Philadelphia tract boundaries", logger):
        # Ensure CRS is WGS84 (EPSG:4326) for web mapping
        if phila_gdf.crs != "EPSG:4326":
            phila_gdf = phila_gdf.to_crs("EPSG:4326")
            logger.info("  Reprojected to EPSG:4326 (WGS84)")
        
        # Keep essential columns
        columns_to_keep = ['GEOID', 'TRACTCE', 'NAME', 'ALAND', 'AWATER', 'geometry']
        phila_gdf = phila_gdf[columns_to_keep]
        
        # Calculate area in square miles for reference
        phila_gdf_projected = phila_gdf.to_crs("EPSG:2272")  # PA State Plane South
        phila_gdf['area_sq_mi'] = phila_gdf_projected.geometry.area / 27878400  # sq ft to sq mi
        
        # Save to GeoJSON
        output_file = PATHS.geo / "philadelphia_tracts.geojson"
        phila_gdf.to_file(output_file, driver="GeoJSON")
        logger.info(f"  Saved to: {output_file}")
        
        # Summary stats
        logger.info(f"\nSummary:")
        logger.info(f"  Total tracts: {len(phila_gdf)}")
        logger.info(f"  Total land area: {phila_gdf['ALAND'].sum() / 2.59e6:.1f} sq km")
        logger.info(f"  Average tract size: {phila_gdf['area_sq_mi'].mean():.2f} sq mi")
        logger.info(f"  Smallest tract: {phila_gdf['area_sq_mi'].min():.4f} sq mi")
        logger.info(f"  Largest tract: {phila_gdf['area_sq_mi'].max():.2f} sq mi")
    
    return output_file


if __name__ == "__main__":
    output_path = download_census_tracts()
    print(f"\n✅ Census tracts downloaded: {output_path}")

