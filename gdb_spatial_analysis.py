"""
Spatial Analysis of ESRI File Geodatabase (.gdb)

This script performs comprehensive spatial analysis on mobile data from a geodatabase:
- Loads and lists all layers in a File Geodatabase
- Processes mobile user trajectories and GPS data
- Estimates home locations from night-time points
- Creates visualizations and exports results as GeoJSON

Requirements:
    geopandas, pandas, fiona, shapely, matplotlib

Author: Spatial Analysis Script
Date: 2026
"""

import os
import warnings
import pandas as pd
import geopandas as gpd
import fiona
from shapely.geometry import LineString, Point
from datetime import datetime, time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

try:
    import contextily as ctx
    CONTEXTILY_AVAILABLE = True
except ImportError:
    CONTEXTILY_AVAILABLE = False
    print("⚠ contextily not available - maps will be generated without basemap")

from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import numpy as np

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

# Path to the GDB file (adjust as needed)
GDB_PATH = "cvic04.gdb"

# Layers to load from the geodatabase
LAYERS_TO_LOAD = [
    'mobile_data_user_a',
    'mobile_data_user_b',
    'gps_data',
    'bts_locations',
    'lau1_maakond',
    'lau2_omavalitsus'
]

# Night hours for home location estimation (00:00 - 06:00)
NIGHT_START_HOUR = 0
NIGHT_END_HOUR = 6

# Output directory for results
OUTPUT_DIR = "out/iter_01_basic_spatial"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_output_directory():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")


def list_gdb_layers(gdb_path):
    """
    List all feature classes (layers) in a File Geodatabase.
    
    Parameters:
        gdb_path (str): Path to the .gdb folder
        
    Returns:
        list: List of layer names in the geodatabase
    """
    try:
        layers = fiona.listlayers(gdb_path)
        print(f"\n{'='*70}")
        print(f"Layers found in geodatabase: {gdb_path}")
        print(f"{'='*70}")
        for i, layer in enumerate(layers, 1):
            print(f"  {i}. {layer}")
        print(f"Total layers: {len(layers)}\n")
        return layers
    except Exception as e:
        print(f"Error listing layers: {e}")
        return []


def load_gdb_layer(gdb_path, layer_name):
    """
    Load a single layer from the geodatabase.
    
    Parameters:
        gdb_path (str): Path to the .gdb folder
        layer_name (str): Name of the layer to load
        
    Returns:
        GeoDataFrame: Loaded layer as a GeoDataFrame, or None if failed
    """
    try:
        gdf = gpd.read_file(gdb_path, layer=layer_name)
        print(f"✓ Loaded layer '{layer_name}': {len(gdf)} features")
        return gdf
    except Exception as e:
        print(f"✗ Failed to load layer '{layer_name}': {e}")
        return None


def load_all_required_layers(gdb_path, layer_names):
    """
    Load all required layers from the geodatabase.
    
    Parameters:
        gdb_path (str): Path to the .gdb folder
        layer_names (list): List of layer names to load
        
    Returns:
        dict: Dictionary mapping layer names to GeoDataFrames
    """
    print(f"\n{'='*70}")
    print("Loading layers from geodatabase...")
    print(f"{'='*70}")
    
    layers_data = {}
    for layer_name in layer_names:
        gdf = load_gdb_layer(gdb_path, layer_name)
        if gdf is not None:
            layers_data[layer_name] = gdf
    
    print(f"\nSuccessfully loaded {len(layers_data)} out of {len(layer_names)} layers\n")
    return layers_data


def inspect_geodataframe(gdf, name):
    """
    Display inspection details for a GeoDataFrame.
    
    Parameters:
        gdf (GeoDataFrame): The GeoDataFrame to inspect
        name (str): Name/label for the GeoDataFrame
    """
    print(f"\n{'='*70}")
    print(f"Inspection: {name}")
    print(f"{'='*70}")
    print(f"Shape: {gdf.shape}")
    print(f"CRS: {gdf.crs}")
    print(f"Geometry type: {gdf.geometry.type.unique()}")
    print(f"\nColumns: {list(gdf.columns)}")
    print(f"\nFirst few rows:")
    print(gdf.head(3))
    print()


def convert_timestamp_column(gdf, column_name, datetime_format=None):
    """
    Convert a column to datetime format.
    
    Parameters:
        gdf (GeoDataFrame): The GeoDataFrame to process
        column_name (str): Name of the column to convert
        datetime_format (str): Optional datetime format string
        
    Returns:
        GeoDataFrame: GeoDataFrame with converted datetime column
    """
    if column_name not in gdf.columns:
        print(f"Warning: Column '{column_name}' not found in GeoDataFrame")
        return gdf
    
    try:
        if datetime_format:
            gdf[column_name] = pd.to_datetime(gdf[column_name], format=datetime_format)
        else:
            gdf[column_name] = pd.to_datetime(gdf[column_name])
        print(f"✓ Converted column '{column_name}' to datetime")
        return gdf
    except Exception as e:
        print(f"✗ Failed to convert column '{column_name}': {e}")
        return gdf


def filter_night_points(gdf, timestamp_column):
    """
    Filter points that occur during night hours (00:00 - 06:00).
    
    Parameters:
        gdf (GeoDataFrame): The GeoDataFrame with timestamp column
        timestamp_column (str): Name of the timestamp column
        
    Returns:
        GeoDataFrame: Filtered GeoDataFrame with night points only
    """
    night_points = gdf[
        (gdf[timestamp_column].dt.hour >= NIGHT_START_HOUR) & 
        (gdf[timestamp_column].dt.hour < NIGHT_END_HOUR)
    ].copy()
    return night_points


def compute_home_location(points_gdf, timestamp_column):
    """
    Estimate home location as centroid of night-time points.
    
    Parameters:
        points_gdf (GeoDataFrame): Points with timestamp information
        timestamp_column (str): Name of the timestamp column
        
    Returns:
        Point: Centroid point representing estimated home location
    """
    night_points = filter_night_points(points_gdf, timestamp_column)
    
    if len(night_points) == 0:
        print(f"Warning: No night points found for home location estimation")
        return None
    
    # Calculate centroid
    centroid_lon = night_points.geometry.x.mean()
    centroid_lat = night_points.geometry.y.mean()
    home_location = Point(centroid_lon, centroid_lat)
    
    print(f"✓ Computed home location from {len(night_points)} night points")
    return home_location


def create_trajectory(points_gdf, timestamp_column, sort=True):
    """
    Create a trajectory (LineString) from a sequence of points.
    
    Parameters:
        points_gdf (GeoDataFrame): Points to connect into a trajectory
        timestamp_column (str): Column name for sorting by time
        sort (bool): Whether to sort points chronologically before creating trajectory
        
    Returns:
        LineString: Trajectory connecting the points in sequence
    """
    if len(points_gdf) < 2:
        print("Warning: Need at least 2 points to create a trajectory")
        return None
    
    # Sort by timestamp if requested
    if sort and timestamp_column in points_gdf.columns:
        points_gdf = points_gdf.sort_values(timestamp_column)
    
    # Extract coordinates and create LineString
    coords = [(geom.x, geom.y) for geom in points_gdf.geometry]
    trajectory = LineString(coords)
    
    return trajectory


def compute_point_density_grid(gdf, grid_size=0.01):
    """
    Compute point density on a regular grid (simple binning).
    
    Parameters:
        gdf (GeoDataFrame): Points to compute density for
        grid_size (float): Size of grid cells
        
    Returns:
        GeoDataFrame: Grid cells with point counts
    """
    # Get bounds
    minx, miny, maxx, maxy = gdf.total_bounds
    
    # Create grid
    x_coords = np.arange(minx, maxx, grid_size)
    y_coords = np.arange(miny, maxy, grid_size)
    
    # Count points in each grid cell
    point_count = np.zeros((len(y_coords)-1, len(x_coords)-1))
    
    for i, x in enumerate(x_coords[:-1]):
        for j, y in enumerate(y_coords[:-1]):
            cell_bounds = (x, y, x + grid_size, y + grid_size)
            count = len(gdf.cx[x:x+grid_size, y:y+grid_size])
            point_count[j, i] = count
    
    return x_coords, y_coords, point_count


def extract_hour_from_timestamp(gdf, timestamp_column):
    """
    Extract hour from timestamp column.
    
    Parameters:
        gdf (GeoDataFrame): GeoDataFrame with timestamp column
        timestamp_column (str): Name of the timestamp column
        
    Returns:
        GeoDataFrame: GeoDataFrame with additional 'hour' column
    """
    gdf['hour'] = gdf[timestamp_column].dt.hour
    return gdf


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_user_trajectory(trajectory_gdf, user_name, title, output_path=None):
    """
    Create a map showing a user's trajectory with OSM basemap (if available).
    
    Parameters:
        trajectory_gdf (GeoDataFrame): GeoDataFrame with trajectory and points
        user_name (str): Name of the user for title
        title (str): Title for the plot
        output_path (str): Optional path to save the figure
    """
    fig, ax = plt.subplots(figsize=(14, 11))
    
    # Try to add basemap if available
    if CONTEXTILY_AVAILABLE:
        try:
            traj_3857 = trajectory_gdf.to_crs('EPSG:3857')
            ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=10, alpha=0.5)
        except Exception as e:
            print(f"⚠ Error adding basemap: {e}")
            traj_3857 = trajectory_gdf
    else:
        traj_3857 = trajectory_gdf
    
    # Plot trajectory line
    if 'trajectory' in traj_3857.columns:
        trajectory_lines = traj_3857[traj_3857['geometry'].geom_type == 'LineString']
        if len(trajectory_lines) > 0:
            trajectory_lines.plot(ax=ax, color='blue', linewidth=3, alpha=0.7, label='Trajectory')
    
    # Plot points with color gradient by hour
    points = traj_3857[traj_3857['geometry'].geom_type == 'Point'].copy()
    if len(points) > 0 and 'hour' in points.columns:
        scatter = ax.scatter(
            points.geometry.x, 
            points.geometry.y,
            c=points['hour'],
            cmap='viridis',
            s=80,
            alpha=0.7,
            vmin=0,
            vmax=23,
            edgecolor='black',
            linewidth=0.5,
            label='Points (colored by hour)'
        )
        cbar = plt.colorbar(scatter, ax=ax, label='Hour of Day', pad=0.02)
    elif len(points) > 0:
        points.plot(ax=ax, color='green', markersize=80, alpha=0.7, label='Points', edgecolor='black', linewidth=0.5)
    
    # Plot home location if available
    if 'home_location' in trajectory_gdf.columns:
        home = trajectory_gdf['home_location'].iloc[0]
        if home is not None and CONTEXTILY_AVAILABLE:
            home_3857 = gpd.GeoSeries([home], crs='EPSG:3301').to_crs('EPSG:3857')
            ax.plot(home_3857.geometry.x.values[0], home_3857.geometry.y.values[0], 'r*', markersize=25, label='Estimated Home', markeredgecolor='darkred', markeredgewidth=1)
        elif home is not None:
            ax.plot(home.x, home.y, 'r*', markersize=20, label='Estimated Home')
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='best', fontsize=10, framealpha=0.9)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved visualization: {output_path}")
    
    plt.close()


def plot_bts_and_boundaries(bts_gdf, boundaries_gdf, output_path=None):
    """
    Create a map showing BTS locations and administrative boundaries with OSM basemap.
    
    Parameters:
        bts_gdf (GeoDataFrame): BTS locations
        boundaries_gdf (GeoDataFrame): Administrative boundaries
        output_path (str): Optional path to save the figure
    """
    fig, ax = plt.subplots(figsize=(14, 11))
    
    # Prepare data
    if CONTEXTILY_AVAILABLE:
        try:
            bounds_3857 = boundaries_gdf.to_crs('EPSG:3857')
            bts_3857 = bts_gdf.to_crs('EPSG:3857') if bts_gdf is not None else None
            ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=10, alpha=0.5)
        except Exception as e:
            print(f"✅ Error adding basemap: {e}")
            bounds_3857 = boundaries_gdf
            bts_3857 = bts_gdf
    else:
        bounds_3857 = boundaries_gdf
        bts_3857 = bts_gdf
    
    # Plot boundaries
    bounds_3857.plot(ax=ax, color='none', edgecolor='black', linewidth=2, alpha=0.8, label='Administrative Boundaries')
    
    # Plot BTS locations
    if bts_3857 is not None and len(bts_3857) > 0:
        bts_3857.plot(ax=ax, color='red', marker='s', markersize=120, alpha=0.8, label='BTS Locations', edgecolor='darkred', linewidth=0.5)
    
    ax.set_title('BTS Locations and Administrative Boundaries', fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='best', fontsize=10, framealpha=0.9)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved visualization: {output_path}")
    
    plt.close()


def plot_combined_trajectories(user_a_gdf, user_b_gdf, bts_gdf, boundaries_gdf, output_path=None):
    """
    Create a combined map showing both user trajectories, BTS locations, and boundaries with OSM basemap.
    
    Parameters:
        user_a_gdf (GeoDataFrame): User A trajectory GeoDataFrame
        user_b_gdf (GeoDataFrame): User B trajectory GeoDataFrame
        bts_gdf (GeoDataFrame): BTS locations
        boundaries_gdf (GeoDataFrame): Administrative boundaries
        output_path (str): Optional path to save the figure
    """
    fig, ax = plt.subplots(figsize=(16, 13))
    
    # Prepare data
    if CONTEXTILY_AVAILABLE:
        try:
            user_a_3857 = user_a_gdf.to_crs('EPSG:3857')
            user_b_3857 = user_b_gdf.to_crs('EPSG:3857')
            bts_3857 = bts_gdf.to_crs('EPSG:3857') if bts_gdf is not None else None
            bounds_3857 = boundaries_gdf.to_crs('EPSG:3857') if boundaries_gdf is not None else None
            ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=9, alpha=0.4)
        except Exception as e:
            print(f"✅ Error with basemap: {e}")
            user_a_3857 = user_a_gdf
            user_b_3857 = user_b_gdf
            bts_3857 = bts_gdf
            bounds_3857 = boundaries_gdf
    else:
        user_a_3857 = user_a_gdf
        user_b_3857 = user_b_gdf
        bts_3857 = bts_gdf
        bounds_3857 = boundaries_gdf
    
    # Plot boundaries
    if bounds_3857 is not None and len(bounds_3857) > 0:
        bounds_3857.plot(ax=ax, color='none', edgecolor='gray', linewidth=1.5, alpha=0.6)
    
    # Plot User A trajectory
    user_a_lines = user_a_3857[user_a_3857['geometry'].geom_type == 'LineString']
    if len(user_a_lines) > 0:
        user_a_lines.plot(ax=ax, color='blue', linewidth=2.5, alpha=0.7, label='User A Trajectory')
    
    user_a_points = user_a_3857[user_a_3857['geometry'].geom_type == 'Point']
    if len(user_a_points) > 0:
        ax.scatter(user_a_points.geometry.x, user_a_points.geometry.y, 
                  color='blue', s=30, alpha=0.4, edgecolor='darkblue', linewidth=0.3)
    
    # Plot User B trajectory
    user_b_lines = user_b_3857[user_b_3857['geometry'].geom_type == 'LineString']
    if len(user_b_lines) > 0:
        user_b_lines.plot(ax=ax, color='green', linewidth=2.5, alpha=0.7, label='User B Trajectory')
    
    user_b_points = user_b_3857[user_b_3857['geometry'].geom_type == 'Point']
    if len(user_b_points) > 0:
        ax.scatter(user_b_points.geometry.x, user_b_points.geometry.y, 
                  color='green', s=30, alpha=0.4, edgecolor='darkgreen', linewidth=0.3)
    
    # Plot BTS locations
    if bts_3857 is not None and len(bts_3857) > 0:
        bts_3857.plot(ax=ax, color='red', marker='s', markersize=100, alpha=0.8, label='BTS Locations', edgecolor='darkred', linewidth=0.5)
    
    ax.set_title('Mobile User Trajectories, BTS Locations, and Administrative Boundaries', 
                fontsize=15, fontweight='bold', pad=15)
    ax.legend(loc='best', fontsize=11, framealpha=0.95)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved visualization: {output_path}")
    
    plt.close()


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_to_geojson(gdf, output_path):
    """
    Export GeoDataFrame to GeoJSON format.
    
    Parameters:
        gdf (GeoDataFrame): GeoDataFrame to export
        output_path (str): Path to save the GeoJSON file
    """
    try:
        # Remove non-serializable columns for GeoJSON export
        export_gdf = gdf.copy()
        for col in export_gdf.columns:
            if col != 'geometry':
                try:
                    # Try to convert to string if not serializable
                    export_gdf[col] = export_gdf[col].astype(str)
                except:
                    pass
        
        export_gdf.to_file(output_path, driver='GeoJSON')
        print(f"✓ Exported to GeoJSON: {output_path}")
    except Exception as e:
        print(f"✗ Failed to export GeoJSON: {e}")


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def main():
    """
    Main function to execute the spatial analysis workflow.
    """
    print("\n" + "="*70)
    print("ESRI File Geodatabase Spatial Analysis")
    print("="*70 + "\n")
    
    # Step 1: Create output directory
    create_output_directory()
    
    # Step 2: List all layers in the GDB
    all_layers = list_gdb_layers(GDB_PATH)
    
    # Step 3: Load required layers
    layers_data = load_all_required_layers(GDB_PATH, LAYERS_TO_LOAD)
    
    if len(layers_data) == 0:
        print("Error: No layers loaded. Exiting.")
        return
    
    # Step 4: Inspect loaded layers
    for layer_name, gdf in layers_data.items():
        inspect_geodataframe(gdf, layer_name)
    
    # Step 5: Process mobile data users
    print(f"\n{'='*70}")
    print("Processing Mobile User Data")
    print(f"{'='*70}\n")
    
    # Determine timestamp column (common names)
    timestamp_cols = ['timestamp', 'time', 'datetime', 'date_time', 'date', 'created_at']
    
    processed_data = {}
    
    for user_key in ['mobile_data_user_a', 'mobile_data_user_b']:
        if user_key not in layers_data:
            print(f"Skipping {user_key}: not loaded")
            continue
        
        user_gdf = layers_data[user_key].copy()
        user_label = "User A" if user_key.endswith("_a") else "User B"
        
        print(f"\n--- Processing {user_label} ---")
        
        # Find timestamp column
        timestamp_col = None
        for col in timestamp_cols:
            if col in user_gdf.columns:
                timestamp_col = col
                break
        
        if timestamp_col is None:
            # Try to find any datetime-like column
            for col in user_gdf.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    timestamp_col = col
                    break
        
        # Convert timestamp column
        if timestamp_col:
            user_gdf = convert_timestamp_column(user_gdf, timestamp_col)
            
            # Sort by timestamp
            user_gdf = user_gdf.sort_values(timestamp_col)
            print(f"✓ Sorted {len(user_gdf)} points by timestamp")
            
            # Extract hour information
            user_gdf = extract_hour_from_timestamp(user_gdf, timestamp_col)
            
            # Compute home location
            home_location = compute_home_location(user_gdf, timestamp_col)
            
            # Create trajectory
            trajectory = create_trajectory(user_gdf, timestamp_col)
            
            # Create result GeoDataFrame with both points and trajectory
            result_gdf = user_gdf.copy()
            
            if trajectory:
                trajectory_row = gpd.GeoDataFrame(
                    {'geometry': [trajectory], 'type': ['trajectory']},
                    crs=user_gdf.crs
                )
                result_gdf = pd.concat([result_gdf, trajectory_row], ignore_index=True)
            
            result_gdf['home_location'] = home_location
            result_gdf['user'] = user_label
            
            processed_data[user_key] = {
                'gdf': result_gdf,
                'home_location': home_location,
                'trajectory': trajectory,
                'timestamp_col': timestamp_col
            }
            
            print(f"✓ Processed {user_label}: {len(user_gdf)} points")
        else:
            print(f"Warning: Could not find timestamp column for {user_label}")
    
    # Step 6: Create visualizations
    print(f"\n{'='*70}")
    print("Creating Visualizations")
    print(f"{'='*70}\n")
    
    # User A trajectory map
    if 'mobile_data_user_a' in processed_data:
        plot_user_trajectory(
            processed_data['mobile_data_user_a']['gdf'],
            'User A',
            'User A - Trajectory and Movement Pattern',
            os.path.join(OUTPUT_DIR, 'user_a_trajectory.png')
        )
    
    # User B trajectory map
    if 'mobile_data_user_b' in processed_data:
        plot_user_trajectory(
            processed_data['mobile_data_user_b']['gdf'],
            'User B',
            'User B - Trajectory and Movement Pattern',
            os.path.join(OUTPUT_DIR, 'user_b_trajectory.png')
        )
    
    # BTS and boundaries map
    bts_gdf = layers_data.get('bts_locations')
    boundaries_gdf = layers_data.get('lau2_omavalitsus')
    if boundaries_gdf is not None:
        plot_bts_and_boundaries(
            bts_gdf,
            boundaries_gdf,
            os.path.join(OUTPUT_DIR, 'bts_and_boundaries.png')
        )
    
    # Combined trajectories map
    if 'mobile_data_user_a' in processed_data and 'mobile_data_user_b' in processed_data:
        combined_gdf = pd.concat([
            processed_data['mobile_data_user_a']['gdf'],
            processed_data['mobile_data_user_b']['gdf']
        ], ignore_index=True)
        
        plot_combined_trajectories(
            processed_data['mobile_data_user_a']['gdf'],
            processed_data['mobile_data_user_b']['gdf'],
            bts_gdf,
            boundaries_gdf,
            os.path.join(OUTPUT_DIR, 'combined_analysis.png')
        )
    
    # Step 7: Export results
    print(f"\n{'='*70}")
    print("Exporting Results")
    print(f"{'='*70}\n")
    
    # Export trajectories
    for user_key, data in processed_data.items():
        user_label = "user_a" if user_key.endswith("_a") else "user_b"
        trajectory_gdf = data['gdf'][data['gdf']['geometry'].geom_type == 'LineString']
        
        if len(trajectory_gdf) > 0:
            export_to_geojson(
                trajectory_gdf,
                os.path.join(OUTPUT_DIR, f'{user_label}_trajectory.geojson')
            )
    
    # Export home locations
    home_locations = []
    for user_key, data in processed_data.items():
        home = data['home_location']
        user_label = "User A" if user_key.endswith("_a") else "User B"
        if home is not None:
            home_locations.append({
                'geometry': home,
                'user': user_label,
                'type': 'Estimated Home Location'
            })
    
    if home_locations:
        home_gdf = gpd.GeoDataFrame(home_locations, crs='EPSG:4326')
        export_to_geojson(
            home_gdf,
            os.path.join(OUTPUT_DIR, 'home_locations.geojson')
        )
    
    # Export processed user data (points only)
    for user_key, data in processed_data.items():
        user_label = "user_a" if user_key.endswith("_a") else "user_b"
        points_gdf = data['gdf'][data['gdf']['geometry'].geom_type == 'Point']
        
        if len(points_gdf) > 0:
            export_to_geojson(
                points_gdf,
                os.path.join(OUTPUT_DIR, f'{user_label}_points.geojson')
            )
    
    print(f"\n{'='*70}")
    print("Analysis Complete!")
    print(f"{'='*70}")
    print(f"Results exported to: {OUTPUT_DIR}/")
    print(f"\nGenerated files:")
    print("  - Visualizations: *.png")
    print("  - Trajectories: *_trajectory.geojson")
    print("  - Points: *_points.geojson")
    print("  - Home Locations: home_locations.geojson")
    print()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
