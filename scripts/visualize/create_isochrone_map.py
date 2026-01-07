#!/usr/bin/env python3
"""
Create interactive map with trauma center isochrones.

Shows drive-time polygons from each Level I trauma center
overlaid on shooting incident locations.
"""

import sys
from pathlib import Path

import folium
from folium.plugins import MarkerCluster, HeatMap
import geopandas as gpd
import pandas as pd

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_csv, load_config
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Isochrone colors (green to red gradient)
ISOCHRONE_COLORS = {
    5: "#1a9850",   # Dark green - excellent access
    10: "#91cf60",  # Light green
    15: "#fee08b",  # Yellow
    20: "#fc8d59",  # Orange
    30: "#d73027",  # Red - poor access
}


def create_isochrone_map() -> Path:
    """
    Create interactive map with isochrones and shooting locations.
    
    Returns:
        Path to the output HTML file.
    """
    with StepLogger("Loading data", logger):
        # Load isochrones
        isochrones = load_geojson(PATHS.isochrones / "trauma_center_isochrones.geojson")
        logger.info(f"  Loaded {len(isochrones)} isochrones")
        
        # Load trauma centers
        trauma_centers = load_csv(PATHS.processed / "trauma_centers_geocoded.csv")
        logger.info(f"  Loaded {len(trauma_centers)} trauma centers")
        
        # Load shooting data
        shootings = load_csv(PATHS.processed / "shootings_clean.csv", parse_dates=['date'])
        # Sample for performance (full dataset is too large)
        shootings_sample = shootings.sample(n=min(5000, len(shootings)), random_state=42)
        logger.info(f"  Loaded {len(shootings)} shootings (showing {len(shootings_sample)} sample)")
    
    with StepLogger("Creating base map", logger):
        center_lat = 39.9526
        center_lng = -75.1652
        
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=11,
            tiles='cartodbdarkmatter',
            control_scale=True
        )
        
        logger.info("  Base map created (dark theme)")
    
    with StepLogger("Adding isochrone layers", logger):
        # Group isochrones by hospital
        hospitals = isochrones['hospital_name'].unique()
        
        for hospital in hospitals:
            hospital_isos = isochrones[isochrones['hospital_name'] == hospital]
            
            # Create feature group for this hospital
            hospital_group = folium.FeatureGroup(name=f'{hospital} Isochrones', show=True)
            
            # Sort by time descending so larger isochrones are drawn first
            for _, iso in hospital_isos.sort_values('time_minutes', ascending=False).iterrows():
                time_min = int(iso['time_minutes'])
                color = ISOCHRONE_COLORS.get(time_min, '#999999')
                
                folium.GeoJson(
                    iso.geometry.__geo_interface__,
                    style_function=lambda x, color=color, time=time_min: {
                        'fillColor': color,
                        'fillOpacity': 0.15,
                        'color': color,
                        'weight': 2,
                        'dashArray': '5, 5' if time > 15 else ''
                    },
                    tooltip=f"{hospital}: {time_min} min drive"
                ).add_to(hospital_group)
            
            hospital_group.add_to(m)
        
        logger.info(f"  Added isochrones for {len(hospitals)} hospitals")
    
    with StepLogger("Adding shooting heatmap", logger):
        # Create heatmap layer
        heat_data = [[row['lat'], row['lng']] for _, row in shootings_sample.iterrows() 
                     if pd.notna(row['lat']) and pd.notna(row['lng'])]
        
        heatmap = HeatMap(
            heat_data,
            name='Shooting Density Heatmap',
            min_opacity=0.3,
            max_zoom=13,
            radius=15,
            blur=20,
            gradient={0.2: 'blue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}
        )
        heatmap.add_to(m)
        
        logger.info(f"  Added heatmap with {len(heat_data)} points")
    
    with StepLogger("Adding trauma center markers", logger):
        tc_group = folium.FeatureGroup(name='Trauma Centers', show=True)
        
        for _, tc in trauma_centers.iterrows():
            if pd.isna(tc['latitude']) or pd.isna(tc['longitude']):
                continue
                
            # Different marker styles by level
            if tc['trauma_level'] == 'I':
                color = '#e41a1c'
                radius = 15
                icon = '🏥'
            elif tc['trauma_level'] == 'II':
                color = '#ff7f00'
                radius = 12
                icon = '🏨'
            else:
                color = '#999999'
                radius = 10
                icon = '+'
            
            # Add circle marker
            folium.CircleMarker(
                location=[tc['latitude'], tc['longitude']],
                radius=radius,
                color='white',
                weight=3,
                fill=True,
                fillColor=color,
                fillOpacity=0.9,
                popup=folium.Popup(
                    f"""
                    <div style="font-family: Arial; min-width: 150px;">
                        <h4 style="margin: 0 0 5px 0;">{tc['hospital_name']}</h4>
                        <p style="margin: 0;">{tc['trauma_level']}</p>
                        <p style="margin: 5px 0 0 0; font-size: 11px; color: #666;">
                            {tc['address']}
                        </p>
                    </div>
                    """,
                    max_width=250
                ),
                tooltip=f"{tc['hospital_name']} ({tc['trauma_level']})"
            ).add_to(tc_group)
        
        tc_group.add_to(m)
        logger.info("  Trauma center markers added")
    
    with StepLogger("Adding legend and controls", logger):
        # Isochrone legend
        legend_html = """
        <div style="
            position: fixed;
            bottom: 50px;
            right: 50px;
            z-index: 1000;
            background-color: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 8px;
            font-family: Arial, sans-serif;
            color: white;
        ">
            <div style="font-weight: bold; margin-bottom: 10px; font-size: 14px;">
                Drive Time to Level I Trauma
            </div>
            <div style="font-size: 12px;">
                <div style="margin: 5px 0;">
                    <span style="display: inline-block; width: 20px; height: 12px; background-color: #1a9850; margin-right: 8px;"></span>
                    0-5 minutes
                </div>
                <div style="margin: 5px 0;">
                    <span style="display: inline-block; width: 20px; height: 12px; background-color: #91cf60; margin-right: 8px;"></span>
                    5-10 minutes
                </div>
                <div style="margin: 5px 0;">
                    <span style="display: inline-block; width: 20px; height: 12px; background-color: #fee08b; margin-right: 8px;"></span>
                    10-15 minutes
                </div>
                <div style="margin: 5px 0;">
                    <span style="display: inline-block; width: 20px; height: 12px; background-color: #fc8d59; margin-right: 8px;"></span>
                    15-20 minutes
                </div>
                <div style="margin: 5px 0;">
                    <span style="display: inline-block; width: 20px; height: 12px; background-color: #d73027; margin-right: 8px;"></span>
                    20-30 minutes
                </div>
            </div>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #444; font-size: 11px;">
                <div>🏥 Level I Adult Trauma</div>
                <div>🏨 Level II Trauma</div>
            </div>
        </div>
        """
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Title
        title_html = """
        <div style="
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            background-color: rgba(0,0,0,0.8);
            padding: 10px 20px;
            border-radius: 8px;
            font-family: Arial, sans-serif;
            color: white;
        ">
            <h2 style="margin: 0; font-size: 18px;">
                Trauma Center Coverage
            </h2>
            <p style="margin: 5px 0 0 0; font-size: 12px; color: #aaa;">
                Drive-time isochrones from Level I trauma centers
            </p>
        </div>
        """
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Layer control
        folium.LayerControl(collapsed=False).add_to(m)
        
        logger.info("  Legend and controls added")
    
    with StepLogger("Saving map", logger):
        PATHS.interactive.mkdir(parents=True, exist_ok=True)
        output_file = PATHS.interactive / "isochrone_coverage.html"
        m.save(str(output_file))
        logger.info(f"  Saved to: {output_file}")
    
    return output_file


if __name__ == "__main__":
    output_path = create_isochrone_map()
    print(f"\n✅ Isochrone map created: {output_path}")

