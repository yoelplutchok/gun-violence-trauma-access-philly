#!/usr/bin/env python3
"""
Neighborhood Fact Sheets: One-Pagers for Trauma Desert Tracts.

Creates professional, printable fact sheets for the top trauma desert
neighborhoods. Each fact sheet includes:
- Tract/neighborhood identification
- Key statistics (shootings, transport time, demographics)
- Mini-map showing location
- Trend analysis (improving/worsening)
- Nearest trauma center information
- Suggested interventions

These are designed for:
- Community advocacy groups
- Policy briefings
- Grant applications
- Public health presentations
"""

import sys
from pathlib import Path
from typing import Dict, List

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.gridspec as gridspec

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Color scheme
COLORS = {
    'primary': '#2a5a5b',      # Dark teal (trauma desert color)
    'secondary': '#e41a1c',    # Red (hospitals)
    'accent': '#fc8d59',       # Orange
    'background': '#f7f7f7',   # Light gray
    'text': '#333333',         # Dark gray
    'good': '#1a9850',         # Green
    'bad': '#d73027',          # Red
}


def get_tract_neighborhood_name(tract_name: str, lat: float, lng: float) -> str:
    """
    Map tract to approximate neighborhood name based on location.
    This is a simplified mapping - ideally would use actual neighborhood boundaries.
    """
    # Philadelphia neighborhood approximate coordinates
    neighborhoods = {
        'North Philadelphia': (40.00, -75.15),
        'Kensington': (39.99, -75.12),
        'West Philadelphia': (39.96, -75.22),
        'Southwest Philadelphia': (39.92, -75.23),
        'South Philadelphia': (39.93, -75.16),
        'Northeast Philadelphia': (40.05, -75.05),
        'Germantown': (40.04, -75.17),
        'Frankford': (40.02, -75.08),
        'Hunting Park': (40.01, -75.14),
        'Strawberry Mansion': (39.99, -75.18),
        'Tioga': (40.01, -75.15),
        'Nicetown': (40.01, -75.15),
        'Olney': (40.04, -75.12),
        'Cobbs Creek': (39.95, -75.24),
        'Point Breeze': (39.93, -75.18),
    }
    
    # Find closest neighborhood
    min_dist = float('inf')
    closest = 'Philadelphia'
    
    for name, (nlat, nlng) in neighborhoods.items():
        dist = ((lat - nlat)**2 + (lng - nlng)**2)**0.5
        if dist < min_dist:
            min_dist = dist
            closest = name
    
    return closest


def create_fact_sheet(
    tract_data: pd.Series,
    all_tracts: gpd.GeoDataFrame,
    trauma_centers: pd.DataFrame,
    trends_df: pd.DataFrame,
    output_path: Path
):
    """
    Create a single fact sheet for one tract.
    """
    fig = plt.figure(figsize=(8.5, 11))  # Letter size
    
    # Create grid layout
    gs = gridspec.GridSpec(5, 2, height_ratios=[1.2, 1.5, 1, 1, 0.8], 
                           hspace=0.3, wspace=0.2)
    
    # Get tract info
    geoid = str(tract_data.get('GEOID', ''))
    tract_name = tract_data.get('NAME', geoid[-6:])
    
    # Get centroid for neighborhood lookup
    if hasattr(tract_data, 'geometry'):
        centroid = tract_data.geometry.centroid
        lat, lng = centroid.y, centroid.x
    else:
        lat, lng = 40.0, -75.15  # Default
    
    neighborhood = get_tract_neighborhood_name(tract_name, lat, lng)
    
    # ============ HEADER ============
    ax_header = fig.add_subplot(gs[0, :])
    ax_header.set_xlim(0, 10)
    ax_header.set_ylim(0, 2)
    ax_header.axis('off')
    
    # Background box
    header_box = FancyBboxPatch((0, 0), 10, 2, boxstyle="round,pad=0.05",
                                 facecolor=COLORS['primary'], edgecolor='none')
    ax_header.add_patch(header_box)
    
    # Title
    ax_header.text(0.5, 1.5, '🚨 TRAUMA DESERT FACT SHEET', fontsize=16, 
                  fontweight='bold', color='white')
    ax_header.text(0.5, 0.9, f'{neighborhood}', fontsize=22, 
                  fontweight='bold', color='white')
    ax_header.text(0.5, 0.3, f'Census Tract {tract_name}', fontsize=12, 
                  color='white', alpha=0.9)
    
    # ============ MINI MAP ============
    ax_map = fig.add_subplot(gs[1, 0])
    
    # Plot all tracts in light gray
    all_tracts.plot(ax=ax_map, facecolor='#e0e0e0', edgecolor='#cccccc', linewidth=0.3)
    
    # Highlight this tract
    this_tract = all_tracts[all_tracts['GEOID'].astype(str) == str(geoid)]
    if len(this_tract) > 0:
        this_tract.plot(ax=ax_map, facecolor=COLORS['primary'], 
                       edgecolor=COLORS['secondary'], linewidth=2)
    
    # Plot trauma centers
    for _, tc in trauma_centers.iterrows():
        if tc['trauma_level'] == 'I' and tc['designation'] == 'Adult':
            ax_map.plot(tc['longitude'], tc['latitude'], 
                       'r^', markersize=8, markeredgecolor='white', markeredgewidth=1)
    
    ax_map.set_title('Location in Philadelphia', fontsize=10, fontweight='bold')
    ax_map.axis('off')
    
    # ============ KEY STATS ============
    ax_stats = fig.add_subplot(gs[1, 1])
    ax_stats.set_xlim(0, 10)
    ax_stats.set_ylim(0, 10)
    ax_stats.axis('off')
    
    # Stats box
    stats = [
        ('Total Shootings', f"{int(tract_data.get('total_shootings', 0)):,}", COLORS['bad']),
        ('Transport Time', f"{tract_data.get('time_to_nearest', 0):.0f} min", COLORS['accent']),
        ('Population', f"{int(tract_data.get('total_population', 0)):,}", COLORS['text']),
        ('% Black', f"{tract_data.get('pct_black', 0):.1f}%", COLORS['text']),
        ('% Poverty', f"{tract_data.get('pct_poverty', 0):.1f}%", COLORS['text']),
    ]
    
    ax_stats.text(5, 9.5, 'KEY STATISTICS', fontsize=12, fontweight='bold', 
                 ha='center', color=COLORS['primary'])
    
    for i, (label, value, color) in enumerate(stats):
        y_pos = 8 - i * 1.6
        ax_stats.text(1, y_pos, label + ':', fontsize=10, color=COLORS['text'])
        ax_stats.text(9, y_pos, value, fontsize=12, fontweight='bold', 
                     ha='right', color=color)
    
    # ============ TRAUMA ACCESS INFO ============
    ax_access = fig.add_subplot(gs[2, :])
    ax_access.set_xlim(0, 10)
    ax_access.set_ylim(0, 3)
    ax_access.axis('off')
    
    # Background
    access_box = FancyBboxPatch((0, 0), 10, 3, boxstyle="round,pad=0.05",
                                 facecolor=COLORS['background'], edgecolor=COLORS['primary'])
    ax_access.add_patch(access_box)
    
    nearest = tract_data.get('nearest_trauma_center', 'Unknown')
    time_min = tract_data.get('time_to_nearest', 0)
    
    ax_access.text(0.3, 2.4, '🏥 NEAREST LEVEL I TRAUMA CENTER', fontsize=11, 
                  fontweight='bold', color=COLORS['primary'])
    ax_access.text(0.5, 1.6, nearest, fontsize=12, fontweight='bold', color=COLORS['text'])
    ax_access.text(0.5, 0.8, f'Estimated drive time: {time_min:.0f} minutes', 
                  fontsize=10, color=COLORS['text'])
    
    # Access indicator
    if time_min <= 10:
        access_label = 'GOOD ACCESS'
        access_color = COLORS['good']
    elif time_min <= 15:
        access_label = 'MODERATE ACCESS'
        access_color = COLORS['accent']
    else:
        access_label = 'POOR ACCESS'
        access_color = COLORS['bad']
    
    ax_access.text(9.5, 1.5, access_label, fontsize=10, fontweight='bold',
                  ha='right', color=access_color)
    
    # ============ THE PROBLEM ============
    ax_problem = fig.add_subplot(gs[3, 0])
    ax_problem.set_xlim(0, 10)
    ax_problem.set_ylim(0, 5)
    ax_problem.axis('off')
    
    ax_problem.text(0.3, 4.5, '⚠️ THE PROBLEM', fontsize=11, fontweight='bold', 
                   color=COLORS['bad'])
    
    density = tract_data.get('annual_shootings_per_sq_mi', 0)
    city_avg_density = 20.2  # From earlier analysis
    
    problems = [
        f"• {int(tract_data.get('total_shootings', 0)):,} shootings since 2015",
        f"• {density:.1f} shootings/sq mi/year",
        f"  (City avg: {city_avg_density:.1f})",
        f"• {time_min:.0f} min to Level I trauma",
        f"• High burden + Poor access = TRAUMA DESERT",
    ]
    
    for i, text in enumerate(problems):
        ax_problem.text(0.3, 3.5 - i * 0.8, text, fontsize=9, color=COLORS['text'])
    
    # ============ RECOMMENDATIONS ============
    ax_recs = fig.add_subplot(gs[3, 1])
    ax_recs.set_xlim(0, 10)
    ax_recs.set_ylim(0, 5)
    ax_recs.axis('off')
    
    ax_recs.text(0.3, 4.5, '💡 RECOMMENDATIONS', fontsize=11, fontweight='bold', 
                color=COLORS['good'])
    
    recommendations = [
        "• Prioritize for violence intervention",
        "• Deploy 'Stop the Bleed' training",
        "• Consider mobile trauma unit",
        "• Expand community outreach",
        "• Improve EMS response protocols",
    ]
    
    for i, text in enumerate(recommendations):
        ax_recs.text(0.3, 3.5 - i * 0.8, text, fontsize=9, color=COLORS['text'])
    
    # ============ FOOTER ============
    ax_footer = fig.add_subplot(gs[4, :])
    ax_footer.set_xlim(0, 10)
    ax_footer.set_ylim(0, 2)
    ax_footer.axis('off')
    
    ax_footer.text(5, 1.2, 'Philadelphia Trauma Desert Project', fontsize=9, 
                  ha='center', style='italic', color=COLORS['text'])
    ax_footer.text(5, 0.6, 'Data: OpenDataPhilly, PA Trauma Systems Foundation, Census ACS', 
                  fontsize=7, ha='center', color='gray')
    ax_footer.text(5, 0.2, f'Generated: January 2025 | Tract GEOID: {geoid}', 
                  fontsize=7, ha='center', color='gray')
    
    # Save
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"  Created fact sheet: {output_path.name}")


def run_fact_sheet_generation(top_n: int = 5):
    """
    Generate fact sheets for the top N trauma desert tracts.
    """
    logger.info("=" * 60)
    logger.info("NEIGHBORHOOD FACT SHEET GENERATION")
    logger.info("=" * 60)
    
    # Load data
    with StepLogger("Loading data", logger):
        tracts_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        all_tracts = load_geojson(tracts_file)
        logger.info(f"  Loaded {len(all_tracts)} tracts")
        
        tc_file = PATHS.processed / "trauma_centers_geocoded.csv"
        trauma_centers = load_csv(tc_file)
        
        # Load trend data if available
        trends_file = PATHS.tables / "tract_shooting_trends.csv"
        if trends_file.exists():
            trends_df = pd.read_csv(trends_file)
        else:
            trends_df = pd.DataFrame()
    
    # Identify trauma desert tracts (bivariate class 9)
    with StepLogger("Identifying top trauma desert tracts", logger):
        trauma_deserts = all_tracts[all_tracts['bivariate_class'] == 9].copy()
        logger.info(f"  Found {len(trauma_deserts)} trauma desert tracts")
        
        # Rank by shooting count
        trauma_deserts = trauma_deserts.sort_values('total_shootings', ascending=False)
        top_tracts = trauma_deserts.head(top_n)
        
        for i, (_, row) in enumerate(top_tracts.iterrows()):
            logger.info(f"  #{i+1}: Tract {row['NAME']} - {int(row['total_shootings'])} shootings")
    
    # Create output directory
    fact_sheets_dir = PATHS.root / "outputs" / "fact_sheets"
    fact_sheets_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate fact sheets
    with StepLogger(f"Creating {top_n} fact sheets", logger):
        for i, (_, tract_data) in enumerate(top_tracts.iterrows()):
            tract_name = str(tract_data.get('NAME', tract_data.get('GEOID', f'tract_{i}')))
            tract_name_safe = tract_name.replace('.', '_').replace(' ', '_')
            
            output_path = fact_sheets_dir / f"fact_sheet_tract_{tract_name_safe}.png"
            create_fact_sheet(tract_data, all_tracts, trauma_centers, trends_df, output_path)
    
    # Create summary
    logger.info("\n" + "=" * 60)
    logger.info(f"CREATED {top_n} FACT SHEETS")
    logger.info("=" * 60)
    logger.info(f"  Output directory: {fact_sheets_dir}")
    logger.info(f"  Formats: PNG (web) + PDF (print)")
    
    return top_tracts


if __name__ == "__main__":
    top_tracts = run_fact_sheet_generation(top_n=5)
    print(f"\n✅ Generated fact sheets for {len(top_tracts)} trauma desert tracts!")
    print(f"   Find them in: outputs/fact_sheets/")

