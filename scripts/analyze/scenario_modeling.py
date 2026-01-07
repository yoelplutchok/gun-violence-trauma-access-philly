#!/usr/bin/env python3
"""
Scenario Modeling: Hypothetical New Trauma Center/EMS Station Analysis.

This script models the impact of placing a new trauma facility at various
candidate locations. It answers questions like:
- "If we built a new Level I trauma center in Southwest Philadelphia, 
   how many people would gain access within 10 minutes?"
- "What's the optimal location for a mobile trauma unit?"
- "Which location would have the greatest impact on trauma desert tracts?"

Methodology:
1. Define candidate locations (user-specified or algorithmic)
2. For each location, calculate drive times to all tract centroids
3. Recalculate "nearest trauma center" with the new facility
4. Quantify impact: tracts that improve, population affected, shootings covered
5. Rank locations by impact score

IMPORTANT LIMITATIONS:
- Drive times are ESTIMATED using haversine distance * routing factor / urban speed
- This is NOT equivalent to actual routing API results (ORS/Mapbox)
- Results are ILLUSTRATIVE for comparing relative impact between locations
- For precise planning, actual routing API calls should be used
- The existing isochrone-based transport times use actual ORS routing

Output:
- Ranked list of candidate locations by impact
- Before/after comparison maps
- Impact statistics for each scenario
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Average driving speed assumptions (mph) for estimating drive times
# Based on Philadelphia urban driving conditions
URBAN_SPEED_MPH = 18  # Average urban speed including stops, traffic
HIGHWAY_SPEED_MPH = 35  # If near highways

# Bivariate color scheme
BIVARIATE_COLORS = {
    1: "#e8e8e8", 2: "#b5c0da", 3: "#6c83b5",
    4: "#b8d6be", 5: "#90b2b3", 6: "#567994",
    7: "#73ae80", 8: "#5a9178", 9: "#2a5a5b"
}


@dataclass
class CandidateLocation:
    """A candidate location for a new trauma facility."""
    name: str
    lat: float
    lng: float
    facility_type: str = "Level I Trauma Center"
    notes: str = ""


# Predefined candidate locations based on gap analysis
# These are areas identified as having poor trauma access + high burden
CANDIDATE_LOCATIONS = [
    CandidateLocation(
        name="Southwest Philadelphia (Eastwick)",
        lat=39.8986,
        lng=-75.2341,
        notes="Far Southwest - currently 20+ min from nearest Level I"
    ),
    CandidateLocation(
        name="Kingsessing/Cobbs Creek",
        lat=39.9401,
        lng=-75.2248,
        notes="West Philadelphia gap area"
    ),
    CandidateLocation(
        name="Frankford/Mayfair",
        lat=40.0248,
        lng=-75.0801,
        notes="Northeast gap - between Temple and Torresdale"
    ),
    CandidateLocation(
        name="Germantown/Mt. Airy",
        lat=40.0450,
        lng=-75.1750,
        notes="Northwest Philadelphia"
    ),
    CandidateLocation(
        name="Point Breeze/Grays Ferry",
        lat=39.9320,
        lng=-75.1850,
        notes="South-central gap area"
    ),
    CandidateLocation(
        name="Tioga/Nicetown",
        lat=40.0100,
        lng=-75.1550,
        notes="Between Temple and Einstein - high violence area"
    ),
    CandidateLocation(
        name="Hunting Park",
        lat=40.0070,
        lng=-75.1420,
        notes="Near Temple but potentially fills local gap"
    ),
    CandidateLocation(
        name="Strawberry Mansion",
        lat=39.9920,
        lng=-75.1750,
        notes="High violence area in trauma desert zone"
    ),
]


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate great-circle distance between two points in miles.
    """
    R = 3959  # Earth radius in miles
    
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    dlat = np.radians(lat2 - lat1)
    dlng = np.radians(lng2 - lng1)
    
    a = np.sin(dlat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlng/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    
    return R * c


def estimate_drive_time(distance_miles: float, speed_mph: float = URBAN_SPEED_MPH) -> float:
    """
    Estimate drive time in minutes from distance.
    Applies a routing factor (roads aren't straight lines).
    """
    # Routing factor: actual road distance is typically 1.3-1.5x straight line
    routing_factor = 1.4
    actual_distance = distance_miles * routing_factor
    return (actual_distance / speed_mph) * 60  # Convert to minutes


def calculate_new_transport_times(
    gdf: gpd.GeoDataFrame,
    new_location: CandidateLocation,
    existing_trauma_centers: pd.DataFrame
) -> gpd.GeoDataFrame:
    """
    Calculate transport times with a new facility added.
    
    Returns GeoDataFrame with new transport time column.
    """
    result = gdf.copy()
    
    # Calculate distance and time to new facility for each tract
    result['dist_to_new'] = result.apply(
        lambda row: haversine_distance(
            row.geometry.centroid.y, row.geometry.centroid.x,
            new_location.lat, new_location.lng
        ),
        axis=1
    )
    result['time_to_new'] = result['dist_to_new'].apply(estimate_drive_time)
    
    # Get current time to nearest (from existing data)
    current_time_col = 'time_to_nearest'
    
    # New time is minimum of current and time to new facility
    result['time_with_new'] = result[[current_time_col, 'time_to_new']].min(axis=1)
    
    # Identify tracts where new facility is closer
    result['new_is_closer'] = result['time_to_new'] < result[current_time_col]
    
    # Calculate time improvement
    result['time_improvement'] = result[current_time_col] - result['time_with_new']
    
    return result


def calculate_impact_metrics(
    gdf: gpd.GeoDataFrame,
    new_location: CandidateLocation
) -> Dict:
    """
    Calculate impact metrics for a candidate location.
    """
    # Tracts where new facility is closer
    improved = gdf[gdf['new_is_closer']]
    
    # Tracts that move into golden hour (<=20 min)
    was_outside = gdf['time_to_nearest'] > 20
    now_inside = gdf['time_with_new'] <= 20
    gained_golden_hour = gdf[was_outside & now_inside]
    
    # Tracts that move from >15 min to <=10 min (significant improvement)
    significant_improvement = gdf[
        (gdf['time_to_nearest'] > 15) & 
        (gdf['time_with_new'] <= 10)
    ]
    
    # Impact on trauma deserts (bivariate class 9)
    is_desert = gdf['bivariate_class'] == 9
    desert_improvement = gdf[is_desert & gdf['new_is_closer']]
    
    metrics = {
        'location_name': new_location.name,
        'lat': new_location.lat,
        'lng': new_location.lng,
        'tracts_improved': len(improved),
        'population_improved': improved['total_population'].sum(),
        'shootings_in_improved_tracts': improved['total_shootings'].sum(),
        'tracts_gained_golden_hour': len(gained_golden_hour),
        'population_gained_golden_hour': gained_golden_hour['total_population'].sum(),
        'tracts_significant_improvement': len(significant_improvement),
        'trauma_deserts_improved': len(desert_improvement),
        'avg_time_improvement_min': improved['time_improvement'].mean() if len(improved) > 0 else 0,
        'max_time_improvement_min': improved['time_improvement'].max() if len(improved) > 0 else 0,
        'notes': new_location.notes
    }
    
    # Calculate composite impact score
    # Weighted combination of factors
    metrics['impact_score'] = (
        metrics['population_improved'] * 0.3 +
        metrics['shootings_in_improved_tracts'] * 50 +  # Weight shootings heavily
        metrics['population_gained_golden_hour'] * 0.5 +
        metrics['trauma_deserts_improved'] * 5000  # Big bonus for helping deserts
    )
    
    return metrics


def create_scenario_comparison_map(
    gdf: gpd.GeoDataFrame,
    new_location: CandidateLocation,
    trauma_centers: pd.DataFrame,
    output_path: Path
):
    """
    Create before/after comparison map for a scenario.
    """
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # Left: Current state
    ax1 = axes[0]
    colors_before = gdf['bivariate_class'].map(BIVARIATE_COLORS)
    gdf.plot(ax=ax1, color=colors_before, edgecolor='#333333', linewidth=0.2)
    
    # Plot existing trauma centers
    for _, tc in trauma_centers.iterrows():
        if tc['trauma_level'] == 'I' and tc['designation'] == 'Adult':
            ax1.plot(tc['longitude'], tc['latitude'], 'r^', markersize=10, 
                    markeredgecolor='white', markeredgewidth=1)
    
    ax1.set_title('Current State\n(Existing Trauma Centers Only)', 
                 fontsize=12, fontweight='bold')
    ax1.axis('off')
    
    # Right: With new facility
    ax2 = axes[1]
    
    # Color by improvement
    def get_color(row):
        if row['new_is_closer']:
            improvement = row['time_improvement']
            if improvement >= 5:
                return '#1a9850'  # Dark green - major improvement
            elif improvement >= 2:
                return '#91cf60'  # Light green - moderate improvement
            else:
                return '#d9ef8b'  # Yellow-green - minor improvement
        else:
            return BIVARIATE_COLORS.get(int(row['bivariate_class']), '#e8e8e8')
    
    colors_after = gdf.apply(get_color, axis=1)
    gdf.plot(ax=ax2, color=colors_after, edgecolor='#333333', linewidth=0.2)
    
    # Plot existing trauma centers
    for _, tc in trauma_centers.iterrows():
        if tc['trauma_level'] == 'I' and tc['designation'] == 'Adult':
            ax2.plot(tc['longitude'], tc['latitude'], 'r^', markersize=10,
                    markeredgecolor='white', markeredgewidth=1)
    
    # Plot new facility
    ax2.plot(new_location.lng, new_location.lat, 'g*', markersize=20,
            markeredgecolor='white', markeredgewidth=2, label='New Facility')
    
    # Add circle showing approximate 10-min coverage
    circle = plt.Circle((new_location.lng, new_location.lat), 
                        0.045,  # Approximate 10-min driving radius in degrees
                        fill=False, edgecolor='green', linewidth=2, linestyle='--')
    ax2.add_patch(circle)
    
    ax2.set_title(f'With New Facility:\n{new_location.name}', 
                 fontsize=12, fontweight='bold')
    ax2.axis('off')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='#1a9850', label='Major improvement (5+ min)'),
        mpatches.Patch(facecolor='#91cf60', label='Moderate improvement (2-5 min)'),
        mpatches.Patch(facecolor='#d9ef8b', label='Minor improvement (<2 min)'),
        plt.Line2D([0], [0], marker='^', color='w', markerfacecolor='red', 
                  markersize=10, label='Existing Level I'),
        plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='green',
                  markersize=15, label='New Facility'),
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=5,
              fontsize=9, frameon=False, bbox_to_anchor=(0.5, 0.02))
    
    plt.suptitle(
        f'Scenario Analysis: Impact of New Trauma Facility\n'
        f'{new_location.name}',
        fontsize=14, fontweight='bold', y=0.98
    )
    
    plt.tight_layout(rect=[0, 0.08, 1, 0.93])
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved scenario map: {output_path}")


def create_ranking_chart(rankings_df: pd.DataFrame, output_path: Path):
    """
    Create a chart showing ranked candidate locations by impact score.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Impact score ranking
    ax1 = axes[0]
    sorted_df = rankings_df.sort_values('impact_score', ascending=True)
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(sorted_df)))
    
    bars = ax1.barh(sorted_df['location_name'], sorted_df['impact_score'], color=colors)
    ax1.set_xlabel('Impact Score', fontsize=11)
    ax1.set_title('Candidate Locations by Impact Score', fontsize=12, fontweight='bold')
    ax1.axvline(x=sorted_df['impact_score'].median(), color='gray', 
               linestyle='--', alpha=0.7, label='Median')
    
    # Right: Population improved
    ax2 = axes[1]
    sorted_df2 = rankings_df.sort_values('population_improved', ascending=True)
    bars2 = ax2.barh(sorted_df2['location_name'], sorted_df2['population_improved'], 
                    color='#2166ac')
    ax2.set_xlabel('Population with Improved Access', fontsize=11)
    ax2.set_title('Population Impact by Location', fontsize=12, fontweight='bold')
    
    # Add value labels
    for bar in bars2:
        width = bar.get_width()
        ax2.text(width + 500, bar.get_y() + bar.get_height()/2,
                f'{int(width):,}', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved ranking chart: {output_path}")


def run_scenario_analysis(
    candidate_locations: Optional[List[CandidateLocation]] = None
) -> Tuple[pd.DataFrame, gpd.GeoDataFrame]:
    """
    Run scenario analysis for all candidate locations.
    
    Args:
        candidate_locations: List of locations to test. Uses defaults if None.
        
    Returns:
        Tuple of (rankings DataFrame, best scenario GeoDataFrame)
    """
    logger.info("=" * 60)
    logger.info("SCENARIO MODELING: HYPOTHETICAL NEW FACILITIES")
    logger.info("=" * 60)
    
    if candidate_locations is None:
        candidate_locations = CANDIDATE_LOCATIONS
    
    # Load tract data
    with StepLogger("Loading tract data", logger):
        tracts_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        gdf = load_geojson(tracts_file)
        
        # Normalize column names
        if 'time_to_nearest' in gdf.columns:
            gdf['time_to_nearest'] = gdf['time_to_nearest'].astype(float)
        
        logger.info(f"  Loaded {len(gdf)} tracts")
    
    # Load trauma centers
    with StepLogger("Loading trauma centers", logger):
        tc_file = PATHS.processed / "trauma_centers_geocoded.csv"
        trauma_centers = load_csv(tc_file)
        logger.info(f"  Loaded {len(trauma_centers)} trauma centers")
    
    # Analyze each candidate location
    all_metrics = []
    best_gdf = None
    best_score = 0
    
    with StepLogger("Analyzing candidate locations", logger):
        for location in candidate_locations:
            logger.info(f"  Analyzing: {location.name}")
            
            # Calculate new transport times
            scenario_gdf = calculate_new_transport_times(gdf, location, trauma_centers)
            
            # Calculate impact metrics
            metrics = calculate_impact_metrics(scenario_gdf, location)
            all_metrics.append(metrics)
            
            logger.info(f"    → {metrics['tracts_improved']} tracts improved")
            logger.info(f"    → {metrics['population_improved']:,} population affected")
            logger.info(f"    → Impact score: {metrics['impact_score']:,.0f}")
            
            # Track best scenario
            if metrics['impact_score'] > best_score:
                best_score = metrics['impact_score']
                best_gdf = scenario_gdf.copy()
                best_location = location
    
    # Create rankings DataFrame
    rankings_df = pd.DataFrame(all_metrics)
    rankings_df = rankings_df.sort_values('impact_score', ascending=False)
    rankings_df['rank'] = range(1, len(rankings_df) + 1)
    
    # Save outputs
    with StepLogger("Saving outputs", logger):
        PATHS.tables.mkdir(parents=True, exist_ok=True)
        PATHS.figures.mkdir(parents=True, exist_ok=True)
        
        # Save rankings
        rankings_path = PATHS.tables / "scenario_impact_rankings.csv"
        rankings_df.to_csv(rankings_path, index=False)
        logger.info(f"  Saved rankings: {rankings_path}")
        
        # Save best scenario GeoJSON
        best_scenario_path = PATHS.processed / "best_scenario_analysis.geojson"
        best_gdf.to_file(best_scenario_path, driver="GeoJSON")
        logger.info(f"  Saved best scenario: {best_scenario_path}")
    
    # Create visualizations
    with StepLogger("Creating visualizations", logger):
        # Ranking chart
        ranking_chart_path = PATHS.figures / "scenario_rankings.png"
        create_ranking_chart(rankings_df, ranking_chart_path)
        
        # Before/after map for top 3 locations
        for i, (_, row) in enumerate(rankings_df.head(3).iterrows()):
            location = CandidateLocation(
                name=row['location_name'],
                lat=row['lat'],
                lng=row['lng'],
                notes=row['notes']
            )
            scenario_gdf = calculate_new_transport_times(gdf, location, trauma_centers)
            
            map_path = PATHS.figures / f"scenario_map_rank{i+1}_{location.name.replace('/', '_').replace(' ', '_')}.png"
            create_scenario_comparison_map(scenario_gdf, location, trauma_centers, map_path)
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TOP 5 CANDIDATE LOCATIONS BY IMPACT")
    logger.info("=" * 60)
    
    for _, row in rankings_df.head(5).iterrows():
        logger.info(f"\n  #{int(row['rank'])}: {row['location_name']}")
        logger.info(f"      Population improved: {row['population_improved']:,}")
        logger.info(f"      Shootings in improved tracts: {int(row['shootings_in_improved_tracts'])}")
        logger.info(f"      Trauma deserts helped: {int(row['trauma_deserts_improved'])}")
        logger.info(f"      Avg time improvement: {row['avg_time_improvement_min']:.1f} min")
        logger.info(f"      Impact score: {row['impact_score']:,.0f}")
    
    return rankings_df, best_gdf


if __name__ == "__main__":
    rankings, best_scenario = run_scenario_analysis()
    
    print("\n✅ Scenario analysis complete!")
    print(f"\nTop recommendation: {rankings.iloc[0]['location_name']}")
    print(f"  Would improve access for {rankings.iloc[0]['population_improved']:,} residents")
    print(f"  Impact score: {rankings.iloc[0]['impact_score']:,.0f}")

