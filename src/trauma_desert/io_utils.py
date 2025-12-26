"""
I/O utilities for the Trauma Desert project.

Provides standardized functions for loading and saving data files,
configuration, and maintaining the data manifest.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd
import geopandas as gpd
import yaml

from .paths import PATHS


def load_config(config_path: Optional[Path] = None) -> dict:
    """
    Load the project configuration from YAML file.
    
    Args:
        config_path: Optional path to config file. Defaults to params.yml.
        
    Returns:
        Dictionary containing configuration parameters.
    """
    if config_path is None:
        config_path = PATHS.params_file
    
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_csv(
    filepath: Union[str, Path],
    parse_dates: Optional[list] = None,
    **kwargs,
) -> pd.DataFrame:
    """
    Load a CSV file with standardized settings.
    
    Args:
        filepath: Path to the CSV file.
        parse_dates: List of columns to parse as dates.
        **kwargs: Additional arguments passed to pd.read_csv.
        
    Returns:
        pandas DataFrame.
    """
    return pd.read_csv(filepath, parse_dates=parse_dates, **kwargs)


def save_csv(
    df: pd.DataFrame,
    filepath: Union[str, Path],
    index: bool = False,
    **kwargs,
) -> None:
    """
    Save a DataFrame to CSV with standardized settings.
    
    Args:
        df: DataFrame to save.
        filepath: Output path.
        index: Whether to include the index. Default False.
        **kwargs: Additional arguments passed to df.to_csv.
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=index, **kwargs)


def load_geojson(filepath: Union[str, Path]) -> gpd.GeoDataFrame:
    """
    Load a GeoJSON file.
    
    Args:
        filepath: Path to the GeoJSON file.
        
    Returns:
        GeoDataFrame.
    """
    return gpd.read_file(filepath)


def save_geojson(
    gdf: gpd.GeoDataFrame,
    filepath: Union[str, Path],
    **kwargs,
) -> None:
    """
    Save a GeoDataFrame to GeoJSON.
    
    Args:
        gdf: GeoDataFrame to save.
        filepath: Output path.
        **kwargs: Additional arguments passed to gdf.to_file.
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(filepath, driver="GeoJSON", **kwargs)


def calculate_file_hash(filepath: Union[str, Path]) -> str:
    """
    Calculate MD5 hash of a file for verification.
    
    Args:
        filepath: Path to the file.
        
    Returns:
        MD5 hash string.
    """
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def update_manifest(
    filename: str,
    source_url: str,
    row_count: Optional[int] = None,
    date_range: Optional[str] = None,
    notes: Optional[str] = None,
    manifest_path: Optional[Path] = None,
) -> None:
    """
    Update the data manifest with information about a downloaded file.
    
    The manifest tracks all raw data downloads for reproducibility.
    
    Args:
        filename: Name of the downloaded file.
        source_url: URL where the data was obtained.
        row_count: Number of rows in the dataset (if applicable).
        date_range: Date range covered by the data (if applicable).
        notes: Any additional notes about the download.
        manifest_path: Path to manifest file. Defaults to data/raw/manifest.json.
    """
    if manifest_path is None:
        manifest_path = PATHS.manifest_file
    
    # Load existing manifest or create new
    if manifest_path.exists():
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
    else:
        manifest = {"downloads": []}
    
    # Calculate file hash
    filepath = PATHS.raw / filename
    file_hash = calculate_file_hash(filepath) if filepath.exists() else None
    
    # Create entry
    entry = {
        "filename": filename,
        "source_url": source_url,
        "download_timestamp": datetime.now().isoformat(),
        "file_hash_md5": file_hash,
    }
    
    if row_count is not None:
        entry["row_count"] = row_count
    if date_range is not None:
        entry["date_range"] = date_range
    if notes is not None:
        entry["notes"] = notes
    
    # Add or update entry
    existing_idx = next(
        (i for i, e in enumerate(manifest["downloads"]) if e["filename"] == filename),
        None,
    )
    if existing_idx is not None:
        manifest["downloads"][existing_idx] = entry
    else:
        manifest["downloads"].append(entry)
    
    # Save manifest
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


def normalize_geoid(series: pd.Series) -> pd.Series:
    """
    Convert GEOID to consistent 11-character string format.
    
    Handles various input formats:
    - Float (42101000100.0) -> "42101000100"
    - Int (42101000100) -> "42101000100"
    - String with decimal ("42101000100.0") -> "42101000100"
    - String ("42101000100") -> "42101000100"
    
    Args:
        series: pandas Series containing GEOIDs in any format.
        
    Returns:
        Series with consistent 11-character string GEOIDs.
    """
    return (
        series
        .fillna('')
        .astype(str)
        .str.split('.')
        .str[0]
        .str.zfill(11)
    )


def get_latest_file(
    directory: Union[str, Path],
    pattern: str = "*",
) -> Optional[Path]:
    """
    Get the most recently modified file matching a pattern in a directory.
    
    Useful for finding the latest version of date-stamped files.
    
    Args:
        directory: Directory to search.
        pattern: Glob pattern to match. Default "*" matches all files.
        
    Returns:
        Path to the most recent file, or None if no matches.
    """
    directory = Path(directory)
    files = list(directory.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)

