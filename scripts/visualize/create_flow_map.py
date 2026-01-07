#!/usr/bin/env python3
"""
Flow Lines Visualization: Patient Flow from Tracts to Trauma Centers.

Creates an origin-destination flow map showing which trauma center serves
each census tract, with lines weighted by shooting volume and colored by
transport time.

This visualization intuitively shows:
- The catchment area of each trauma center
- Which hospitals bear the highest burden
- Where the longest transport corridors are
- The concentration of high-violence tracts around certain hospitals

Output:
- Static flow map (PNG/PDF)
- Interactive flow map (HTML)
"""

import sys
from pathlib import Path
from collections import defaultdict

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, Normalize
import folium
from folium import plugins

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_csv
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Color scheme for transport time
TIME_COLORS = {
    'fast': '#1a9850',    # Green - 0-10 min
    'moderate': '#fee08b', # Yellow - 10-15 min  
    'slow': '#fc8d59',     # Orange - 15-20 min
    'very_slow': '#d73027' # Red - 20+ min
}

# Hospital colors for distinguishing catchments
HOSPITAL_COLORS = {
    'Temple University Hospital': '#e41a1c',
    'Penn Presbyterian Medical Center': '#377eb8',
    'Thomas Jefferson University Hospital': '#4daf4a',
    'Jefferson Einstein Philadelphia Hospital': '#984ea3',
    'default': '#666666'
}


def get_time_color(time_minutes: float) -> str:
    """Get color based on transport time."""
    if time_minutes <= 10:
        return TIME_COLORS['fast']
    elif time_minutes <= 15:
        return TIME_COLORS['moderate']
    elif time_minutes <= 20:
        return TIME_COLORS['slow']
    else:
        return TIME_COLORS['very_slow']


def get_line_width(shootings: int, max_shootings: int) -> float:
    """Get line width based on shooting count (normalized)."""
    if max_shootings == 0:
        return 0.5
    # Scale from 0.3 to 4 based on shooting volume
    normalized = shootings / max_shootings
    return 0.3 + (normalized * 3.7)


def create_static_flow_map(
    gdf: gpd.GeoDataFrame,
    trauma_centers: pd.DataFrame,
    output_path: Path
):
    """
    Create a static flow map showing patient flows.
    """
    fig, ax = plt.subplots(1, 1, figsize=(14, 16))
    
    # Plot tract boundaries in light gray
    gdf.plot(ax=ax, facecolor='#f0f0f0', edgecolor='#cccccc', linewidth=0.3)
    
    # Prepare flow lines
    max_shootings = gdf['total_shootings'].max()
    
    # Group by nearest trauma center for statistics
    hospital_stats = defaultdict(lambda: {'tracts': 0, 'population': 0, 'shootings': 0})
    
    # Draw flow lines
    for _, row in gdf.iterrows():
        # Get tract centroid
        centroid = row.geometry.centroid
        tract_x, tract_y = centroid.x, centroid.y
        
        # Get nearest trauma center coordinates
        nearest_hospital = row.get('nearest_trauma_center', '')
        tc_match = trauma_centers[trauma_centers['hospital_name'] == nearest_hospital]
        
        if len(tc_match) == 0:
            continue
            
        hospital_x = tc_match.iloc[0]['longitude']
        hospital_y = tc_match.iloc[0]['latitude']
        
        # Get styling
        time_min = row.get('time_to_nearest', 15)
        shootings = row.get('total_shootings', 0)
        
        color = get_time_color(time_min)
        width = get_line_width(shootings, max_shootings)
        alpha = min(0.8, 0.2 + (shootings / max_shootings) * 0.6)
        
        # Draw line
        ax.plot(
            [tract_x, hospital_x], 
            [tract_y, hospital_y],
            color=color,
            linewidth=width,
            alpha=alpha,
            solid_capstyle='round',
            zorder=1
        )
        
        # Accumulate hospital stats
        hospital_stats[nearest_hospital]['tracts'] += 1
        hospital_stats[nearest_hospital]['population'] += row.get('total_population', 0)
        hospital_stats[nearest_hospital]['shootings'] += shootings
    
    # Plot trauma centers on top
    for _, tc in trauma_centers.iterrows():
        if tc['trauma_level'] == 'I' and tc['designation'] == 'Adult':
            color = HOSPITAL_COLORS.get(tc['hospital_name'], HOSPITAL_COLORS['default'])
            ax.plot(
                tc['longitude'], tc['latitude'],
                marker='o', markersize=15,
                color=color, markeredgecolor='white', markeredgewidth=2,
                zorder=10
            )
            # Add label
            ax.annotate(
                tc['hospital_name'].replace(' Hospital', '').replace(' Medical Center', ''),
                (tc['longitude'], tc['latitude']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=8, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                zorder=11
            )
    
    # Create legend
    legend_elements = [
        mpatches.Patch(facecolor=TIME_COLORS['fast'], label='0-10 min (Good)'),
        mpatches.Patch(facecolor=TIME_COLORS['moderate'], label='10-15 min'),
        mpatches.Patch(facecolor=TIME_COLORS['slow'], label='15-20 min'),
        mpatches.Patch(facecolor=TIME_COLORS['very_slow'], label='20+ min (Poor)'),
        plt.Line2D([0], [0], color='gray', linewidth=1, label='Few shootings'),
        plt.Line2D([0], [0], color='gray', linewidth=4, label='Many shootings'),
    ]
    
    ax.legend(handles=legend_elements, loc='lower right', 
             title='Transport Time / Volume', framealpha=0.9)
    
    ax.set_title(
        'Patient Flow to Level I Trauma Centers\n'
        'Line thickness = shooting volume | Color = transport time',
        fontsize=14, fontweight='bold'
    )
    ax.axis('off')
    
    # Add hospital statistics as text box
    stats_text = "Hospital Catchment Statistics:\n"
    for hospital, stats in sorted(hospital_stats.items(), 
                                  key=lambda x: x[1]['shootings'], reverse=True):
        short_name = hospital.replace(' Hospital', '').replace(' Medical Center', '')[:20]
        stats_text += f"\n{short_name}:\n"
        stats_text += f"  {stats['tracts']} tracts | {stats['population']:,} pop | {stats['shootings']:,} shootings"
    
    ax.text(0.02, 0.02, stats_text, transform=ax.transAxes,
           fontsize=8, verticalalignment='bottom',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9),
           family='monospace')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.savefig(output_path.with_suffix('.pdf'), bbox_inches='tight', facecolor='white')
    plt.close()
    
    logger.info(f"Saved static flow map: {output_path}")
    
    return hospital_stats


def create_interactive_flow_map(
    gdf: gpd.GeoDataFrame,
    trauma_centers: pd.DataFrame,
    output_path: Path
):
    """
    Create an interactive flow map using Folium.
    """
    # Create base map
    center_lat = gdf.geometry.centroid.y.mean()
    center_lng = gdf.geometry.centroid.x.mean()
    
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=11,
        tiles='cartodbpositron'
    )
    
    # Add tract boundaries
    tract_style = lambda x: {
        'fillColor': '#f0f0f0',
        'color': '#cccccc',
        'weight': 0.5,
        'fillOpacity': 0.3
    }
    
    folium.GeoJson(
        gdf.__geo_interface__,
        style_function=tract_style,
        name='Census Tracts'
    ).add_to(m)
    
    # Create feature groups for each hospital
    hospital_groups = {}
    for _, tc in trauma_centers.iterrows():
        if tc['trauma_level'] == 'I' and tc['designation'] == 'Adult':
            name = tc['hospital_name']
            hospital_groups[name] = folium.FeatureGroup(name=f"Flows to {name}")
    
    # Add flow lines
    max_shootings = gdf['total_shootings'].max()
    
    for _, row in gdf.iterrows():
        centroid = row.geometry.centroid
        tract_coords = [centroid.y, centroid.x]
        
        nearest_hospital = row.get('nearest_trauma_center', '')
        tc_match = trauma_centers[trauma_centers['hospital_name'] == nearest_hospital]
        
        if len(tc_match) == 0:
            continue
            
        hospital_coords = [tc_match.iloc[0]['latitude'], tc_match.iloc[0]['longitude']]
        
        time_min = row.get('time_to_nearest', 15)
        shootings = row.get('total_shootings', 0)
        
        color = get_time_color(time_min)
        weight = max(1, min(8, 1 + (shootings / max_shootings) * 7))
        opacity = min(0.8, 0.3 + (shootings / max_shootings) * 0.5)
        
        # Create popup
        popup_html = f"""
        <b>Tract {row.get('NAME', row.get('GEOID', 'Unknown'))}</b><br>
        Shootings: {int(shootings)}<br>
        Transport time: {time_min:.1f} min<br>
        Nearest: {nearest_hospital}<br>
        Population: {int(row.get('total_population', 0)):,}
        """
        
        line = folium.PolyLine(
            locations=[tract_coords, hospital_coords],
            color=color,
            weight=weight,
            opacity=opacity,
            popup=folium.Popup(popup_html, max_width=200)
        )
        
        if nearest_hospital in hospital_groups:
            line.add_to(hospital_groups[nearest_hospital])
    
    # Add hospital groups to map
    for group in hospital_groups.values():
        group.add_to(m)
    
    # Add trauma center markers
    for _, tc in trauma_centers.iterrows():
        if tc['trauma_level'] == 'I' and tc['designation'] == 'Adult':
            color = HOSPITAL_COLORS.get(tc['hospital_name'], HOSPITAL_COLORS['default'])
            
            folium.CircleMarker(
                location=[tc['latitude'], tc['longitude']],
                radius=12,
                color='white',
                weight=3,
                fill=True,
                fillColor=color,
                fillOpacity=1,
                popup=f"<b>{tc['hospital_name']}</b><br>Level I Trauma Center"
            ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                background-color: white; padding: 10px; border-radius: 5px;
                border: 2px solid gray; font-size: 12px;">
        <b>Transport Time</b><br>
        <i style="background: #1a9850; width: 20px; height: 10px; display: inline-block;"></i> 0-10 min<br>
        <i style="background: #fee08b; width: 20px; height: 10px; display: inline-block;"></i> 10-15 min<br>
        <i style="background: #fc8d59; width: 20px; height: 10px; display: inline-block;"></i> 15-20 min<br>
        <i style="background: #d73027; width: 20px; height: 10px; display: inline-block;"></i> 20+ min<br>
        <br><b>Line Thickness</b> = Shooting Volume
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add title
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                z-index: 1000; background-color: white; padding: 10px 20px;
                border-radius: 5px; border: 2px solid gray; font-size: 16px;
                font-weight: bold;">
        Patient Flow to Level I Trauma Centers
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Save
    m.save(str(output_path))
    logger.info(f"Saved interactive flow map: {output_path}")


def run_flow_visualization():
    """
    Main function to create flow visualizations.
    """
    logger.info("=" * 60)
    logger.info("FLOW LINES VISUALIZATION")
    logger.info("=" * 60)
    
    # Load data
    with StepLogger("Loading data", logger):
        tracts_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        gdf = load_geojson(tracts_file)
        logger.info(f"  Loaded {len(gdf)} tracts")
        
        tc_file = PATHS.processed / "trauma_centers_geocoded.csv"
        trauma_centers = load_csv(tc_file)
        logger.info(f"  Loaded {len(trauma_centers)} trauma centers")
    
    # Calculate hospital statistics
    with StepLogger("Calculating hospital catchment statistics", logger):
        hospital_stats = defaultdict(lambda: {'tracts': 0, 'population': 0, 'shootings': 0})
        
        for _, row in gdf.iterrows():
            nearest = row.get('nearest_trauma_center', '')
            hospital_stats[nearest]['tracts'] += 1
            hospital_stats[nearest]['population'] += row.get('total_population', 0)
            hospital_stats[nearest]['shootings'] += row.get('total_shootings', 0)
        
        for hospital, stats in sorted(hospital_stats.items(), 
                                      key=lambda x: x[1]['shootings'], reverse=True):
            logger.info(f"  {hospital}:")
            logger.info(f"    Tracts: {stats['tracts']}")
            logger.info(f"    Population: {stats['population']:,}")
            logger.info(f"    Shootings: {stats['shootings']:,}")
    
    # Create visualizations
    with StepLogger("Creating static flow map", logger):
        static_path = PATHS.figures / "patient_flow_map.png"
        create_static_flow_map(gdf, trauma_centers, static_path)
    
    with StepLogger("Creating interactive flow map", logger):
        interactive_path = PATHS.interactive / "patient_flow_map.html"
        create_interactive_flow_map(gdf, trauma_centers, interactive_path)
    
    # Save statistics
    with StepLogger("Saving catchment statistics", logger):
        stats_rows = []
        for hospital, stats in hospital_stats.items():
            stats_rows.append({
                'hospital_name': hospital,
                'tracts_served': stats['tracts'],
                'population_served': stats['population'],
                'shootings_in_catchment': stats['shootings'],
                'pct_city_shootings': stats['shootings'] / gdf['total_shootings'].sum() * 100 if gdf['total_shootings'].sum() > 0 else 0
            })
        
        stats_df = pd.DataFrame(stats_rows)
        stats_df = stats_df.sort_values('shootings_in_catchment', ascending=False)
        
        stats_path = PATHS.tables / "hospital_catchment_statistics.csv"
        stats_df.to_csv(stats_path, index=False)
        logger.info(f"  Saved: {stats_path}")
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("HOSPITAL BURDEN SUMMARY")
    logger.info("=" * 60)
    
    total_shootings = gdf['total_shootings'].sum()
    for hospital, stats in sorted(hospital_stats.items(), 
                                  key=lambda x: x[1]['shootings'], reverse=True):
        pct = (stats['shootings'] / total_shootings * 100) if total_shootings > 0 else 0
        logger.info(f"  {hospital}: {stats['shootings']:,} shootings ({pct:.1f}% of city)")
    
    return gdf, stats_df


if __name__ == "__main__":
    gdf, stats = run_flow_visualization()
    print("\n✅ Flow visualization complete!")
    print(f"\nHospital catchment summary:\n{stats.to_string(index=False)}")

