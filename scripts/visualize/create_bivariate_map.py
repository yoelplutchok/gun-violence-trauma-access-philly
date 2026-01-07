#!/usr/bin/env python3
"""
Create bivariate choropleth map of trauma deserts.

Generates an interactive Folium map showing the 3×3 bivariate classification
of shooting density vs. transport time to Level I trauma centers.
"""

import sys
from pathlib import Path

import folium
from folium.plugins import FloatImage
import geopandas as gpd
import pandas as pd

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.trauma_desert.paths import PATHS
from src.trauma_desert.io_utils import load_geojson, load_config
from src.trauma_desert.logging_utils import get_logger, StepLogger

# Configure logging
logger = get_logger(__name__)

# Stevens Blue-Green bivariate color scheme
BIVARIATE_COLORS = {
    1: "#e8e8e8",  # Low density, Low time (good)
    2: "#b5c0da",  # Low density, Med time
    3: "#6c83b5",  # Low density, High time
    4: "#b8d6be",  # Med density, Low time
    5: "#90b2b3",  # Med density, Med time
    6: "#567994",  # Med density, High time
    7: "#73ae80",  # High density, Low time
    8: "#5a9178",  # High density, Med time
    9: "#2a5a5b",  # High density, High time (TRAUMA DESERT)
}


def create_bivariate_legend() -> str:
    """Create HTML for bivariate legend."""
    legend_html = """
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        z-index: 1000;
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        font-family: Arial, sans-serif;
    ">
        <div style="font-weight: bold; margin-bottom: 10px; font-size: 14px;">
            Trauma Desert Classification
        </div>
        <div style="display: flex; align-items: center;">
            <div style="margin-right: 10px;">
                <div style="font-size: 11px; transform: rotate(-90deg); white-space: nowrap; margin-left: -30px;">
                    ← Low Violence | High Violence →
                </div>
            </div>
            <div>
                <table style="border-collapse: collapse;">
                    <tr>
                        <td style="width: 30px; height: 30px; background-color: #6c83b5;"></td>
                        <td style="width: 30px; height: 30px; background-color: #567994;"></td>
                        <td style="width: 30px; height: 30px; background-color: #2a5a5b; border: 3px solid #e41a1c;"></td>
                    </tr>
                    <tr>
                        <td style="width: 30px; height: 30px; background-color: #b5c0da;"></td>
                        <td style="width: 30px; height: 30px; background-color: #90b2b3;"></td>
                        <td style="width: 30px; height: 30px; background-color: #5a9178;"></td>
                    </tr>
                    <tr>
                        <td style="width: 30px; height: 30px; background-color: #e8e8e8;"></td>
                        <td style="width: 30px; height: 30px; background-color: #b8d6be;"></td>
                        <td style="width: 30px; height: 30px; background-color: #73ae80;"></td>
                    </tr>
                </table>
                <div style="font-size: 11px; margin-top: 5px; text-align: center;">
                    ← Good Access | Poor Access →
                </div>
            </div>
        </div>
        <div style="margin-top: 10px; font-size: 11px; border-top: 1px solid #ccc; padding-top: 8px;">
            <span style="display: inline-block; width: 12px; height: 12px; background-color: #2a5a5b; border: 2px solid #e41a1c; margin-right: 5px;"></span>
            Trauma Desert
        </div>
    </div>
    """
    return legend_html


def style_function(feature):
    """Style function for bivariate classification."""
    bivariate_class = feature['properties'].get('bivariate_class', 5)
    is_trauma_desert = bivariate_class == 9
    
    return {
        'fillColor': BIVARIATE_COLORS.get(bivariate_class, '#cccccc'),
        'fillOpacity': 0.7,
        'color': '#e41a1c' if is_trauma_desert else '#333333',
        'weight': 3 if is_trauma_desert else 0.5,
        'dashArray': '' if is_trauma_desert else '3'
    }


def create_popup(feature):
    """Create popup content for tract."""
    props = feature['properties']
    
    # Determine category label
    bivariate_class = props.get('bivariate_class', 5)
    label = props.get('bivariate_label', 'Unknown')
    
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; min-width: 200px;">
        <h4 style="margin: 0 0 10px 0; color: {'#e41a1c' if bivariate_class == 9 else '#333'};">
            {'🚨 TRAUMA DESERT' if bivariate_class == 9 else f'Tract {props.get("NAME", "N/A")}'}
        </h4>
        <table style="width: 100%; font-size: 12px;">
            <tr>
                <td style="padding: 3px 0;"><b>Classification:</b></td>
                <td>{label}</td>
            </tr>
            <tr>
                <td style="padding: 3px 0;"><b>Shootings (Total):</b></td>
                <td>{props.get('total_shootings', 'N/A'):,.0f}</td>
            </tr>
            <tr>
                <td style="padding: 3px 0;"><b>Density:</b></td>
                <td>{props.get('annual_shootings_per_sq_mi', 0):.1f} per sq mi/yr</td>
            </tr>
            <tr>
                <td style="padding: 3px 0;"><b>Time to Level I:</b></td>
                <td>{props.get('time_to_nearest', 'N/A')} min</td>
            </tr>
            <tr>
                <td style="padding: 3px 0;"><b>Nearest Hospital:</b></td>
                <td>{props.get('nearest_trauma_center', 'N/A')}</td>
            </tr>
            <tr style="border-top: 1px solid #ccc;">
                <td style="padding: 5px 0 3px 0;"><b>Population:</b></td>
                <td>{props.get('total_population', 'N/A'):,.0f}</td>
            </tr>
            <tr>
                <td style="padding: 3px 0;"><b>% Black:</b></td>
                <td>{props.get('pct_black', 'N/A'):.1f}%</td>
            </tr>
            <tr>
                <td style="padding: 3px 0;"><b>% Poverty:</b></td>
                <td>{props.get('pct_poverty', 'N/A'):.1f}%</td>
            </tr>
        </table>
    </div>
    """
    return folium.Popup(popup_html, max_width=300)


def create_bivariate_map() -> Path:
    """
    Create bivariate choropleth map.
    
    Returns:
        Path to the output HTML file.
    """
    with StepLogger("Loading classified tract data", logger):
        classified_file = PATHS.processed / "tracts_bivariate_classified.geojson"
        gdf = load_geojson(classified_file)
        logger.info(f"  Loaded {len(gdf)} classified tracts")
    
    with StepLogger("Loading trauma center locations", logger):
        tc_file = PATHS.processed / "trauma_centers_geocoded.csv"
        trauma_centers = pd.read_csv(tc_file)
        logger.info(f"  Loaded {len(trauma_centers)} trauma centers")
    
    with StepLogger("Creating base map", logger):
        # Philadelphia center
        center_lat = 39.9526
        center_lng = -75.1652
        
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=11,
            tiles='cartodbpositron',
            control_scale=True
        )
        
        logger.info("  Base map created")
    
    with StepLogger("Adding bivariate choropleth layer", logger):
        # Convert to GeoJSON format
        gdf_json = gdf.to_json()
        
        folium.GeoJson(
            gdf_json,
            name='Bivariate Classification',
            style_function=style_function,
            popup=folium.GeoJsonPopup(
                fields=['NAME', 'bivariate_label', 'total_shootings', 'time_to_nearest'],
                aliases=['Tract', 'Classification', 'Shootings', 'Time to Trauma (min)'],
                localize=True
            ),
            tooltip=folium.GeoJsonTooltip(
                fields=['NAME', 'bivariate_label'],
                aliases=['Tract', 'Classification'],
                style='font-size: 12px;'
            )
        ).add_to(m)
        
        logger.info("  Bivariate layer added")
    
    with StepLogger("Adding trauma center markers", logger):
        # Create feature group for trauma centers
        tc_group = folium.FeatureGroup(name='Level I Trauma Centers')
        
        for _, tc in trauma_centers.iterrows():
            if tc['trauma_level'] == 'I' and tc.get('designation', '') == 'Adult':
                folium.CircleMarker(
                    location=[tc['latitude'], tc['longitude']],
                    radius=12,
                    color='#e41a1c',
                    fill=True,
                    fillColor='#e41a1c',
                    fillOpacity=0.9,
                    popup=f"<b>{tc['hospital_name']}</b><br>{tc['trauma_level']}",
                    tooltip=tc['hospital_name']
                ).add_to(tc_group)
                
                # Add hospital icon/label
                folium.Marker(
                    location=[tc['latitude'], tc['longitude']],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size: 10px; font-weight: bold; color: white; text-shadow: 1px 1px 2px black;">🏥</div>'
                    )
                ).add_to(tc_group)
        
        tc_group.add_to(m)
        logger.info("  Trauma center markers added")
    
    with StepLogger("Adding legend and controls", logger):
        # Add legend
        legend_html = create_bivariate_legend()
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add title
        title_html = """
        <div style="
            position: fixed;
            top: 10px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            background-color: white;
            padding: 10px 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            font-family: Arial, sans-serif;
        ">
            <h2 style="margin: 0; font-size: 18px; color: #333;">
                Philadelphia Trauma Deserts
            </h2>
            <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;">
                Gun Violence Burden vs. Level I Trauma Access
            </p>
        </div>
        """
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        logger.info("  Legend and controls added")
    
    with StepLogger("Saving map", logger):
        PATHS.interactive.mkdir(parents=True, exist_ok=True)
        output_file = PATHS.interactive / "bivariate_choropleth.html"
        m.save(str(output_file))
        logger.info(f"  Saved to: {output_file}")
    
    return output_file


if __name__ == "__main__":
    output_path = create_bivariate_map()
    print(f"\n✅ Bivariate map created: {output_path}")

