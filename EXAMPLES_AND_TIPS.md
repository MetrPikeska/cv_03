# Usage Examples and Tips

This document provides practical examples and tips for using the GDB Spatial Analysis script.

## Table of Contents
1. [Basic Usage](#basic-usage)
2. [Data Inspection](#data-inspection)
3. [Custom Modifications](#custom-modifications)
4. [Advanced Examples](#advanced-examples)
5. [Performance Optimization](#performance-optimization)

---

## Basic Usage

### Run with Default Settings
```bash
python gdb_spatial_analysis.py
```

### Check Quick Progress
The script prints detailed progress:
```
============================================================
Layers found in geodatabase: data/mobile_data.gdb
============================================================
  1. mobile_data_user_a
  2. mobile_data_user_b
  ...
```

---

## Data Inspection

### Example 1: Explore Layer Structure
```python
import geopandas as gpd
import fiona

# List all layers
gdb_path = "data/mobile_data.gdb"
layers = fiona.listlayers(gdb_path)
print(f"Available layers: {layers}")

# Load and inspect a layer
user_a = gpd.read_file(gdb_path, layer='mobile_data_user_a')
print(f"Layer shape: {user_a.shape}")
print(f"CRS: {user_a.crs}")
print(f"Columns: {user_a.columns.tolist()}")
print(f"Geometry types: {user_a.geometry.type.unique()}")
```

### Example 2: Check Timestamp Columns
```python
import geopandas as gpd

user_a = gpd.read_file("data/mobile_data.gdb", layer='mobile_data_user_a')

# Find columns that might contain timestamps
timestamp_candidates = [col for col in user_a.columns 
                       if 'date' in col.lower() or 'time' in col.lower()]
print(f"Possible timestamp columns: {timestamp_candidates}")

# Check first few values
for col in timestamp_candidates:
    print(f"\n{col}:")
    print(user_a[col].head())
```

### Example 3: Verify Coordinate System
```python
import geopandas as gpd

gdb_path = "data/mobile_data.gdb"

# Check CRS for all layers
for layer in ['mobile_data_user_a', 'bts_locations', 'lau2_omavalitsus']:
    gdf = gpd.read_file(gdb_path, layer=layer)
    print(f"{layer}: {gdf.crs}")
    # Get bounds
    bounds = gdf.total_bounds
    print(f"  Bounds: ({bounds[0]:.4f}, {bounds[1]:.4f}, {bounds[2]:.4f}, {bounds[3]:.4f})")
```

---

## Custom Modifications

### Modification 1: Change Home Location Window

**Default (night-time only):**
```python
NIGHT_START_HOUR = 0   # 00:00
NIGHT_END_HOUR = 6     # 06:00
```

**Alternative (evening to morning):**
```python
NIGHT_START_HOUR = 20  # 20:00 (8 PM)
NIGHT_END_HOUR = 8     # 08:00 (8 AM)
```

**Alternative (weekends only):**
```python
# Add to script to filter weekend points
def is_weekend(timestamp):
    return timestamp.weekday() >= 4  # Friday=4, Saturday=5

night_points = user_gdf[is_weekend(user_gdf['timestamp'])]
```

### Modification 2: Add Filtering by Spatial Region

```python
# Add this function to the script
def filter_by_region(gdf, minx, miny, maxx, maxy):
    """Filter points within a bounding box"""
    filtered = gdf.cx[minx:maxx, miny:maxy]
    print(f"Filtered to {len(filtered)} points within region")
    return filtered

# Use in main workflow
bbox = (24.0, 58.0, 28.0, 60.0)  # Estonia approximate bounds
user_a = filter_by_region(user_a, *bbox)
```

### Modification 3: Add Custom Time-Based Analysis

```python
import pandas as pd

# Add to compute statistics by hour
def hourly_statistics(gdf, timestamp_col):
    """Compute statistics grouped by hour of day"""
    gdf['hour'] = gdf[timestamp_col].dt.hour
    
    hourly_stats = gdf.groupby('hour').agg({
        'hour': 'count'  # Count points per hour
    }).rename(columns={'hour': 'count'})
    
    print("\nPoints per hour of day:")
    print(hourly_stats)
    
    return hourly_stats

# Call in main workflow
hourly_stats = hourly_statistics(user_a, 'timestamp')
```

### Modification 4: Export Additional Formats

```python
# Add to export_to_geojson() or create new functions

def export_to_shapefile(gdf, output_path):
    """Export to Shapefile format"""
    gdf.to_file(output_path, driver='ESRI Shapefile')
    print(f"Exported to Shapefile: {output_path}")

def export_to_geopackage(gdf, output_path, layer):
    """Export to GeoPackage format"""
    gdf.to_file(output_path, layer=layer, driver='GPKG')
    print(f"Exported to GeoPackage: {output_path}")

def export_to_csv(gdf, output_path):
    """Export to CSV (drops geometry)"""
    gdf.drop(columns='geometry').to_csv(output_path, index=False)
    print(f"Exported to CSV: {output_path}")

# Use in export section
export_to_shapefile(trajectory_gdf, 'output.shp')
export_to_geopackage(trajectory_gdf, 'output.gpkg', 'trajectory')
```

---

## Advanced Examples

### Example 1: Compute Distance Traveled

```python
from shapely.geometry import LineString

def compute_distance_traveled(points_gdf, timestamp_col):
    """Calculate total distance traveled between points"""
    
    # Sort by timestamp
    points = points_gdf.sort_values(timestamp_col)
    
    # Create trajectory
    coords = [(geom.x, geom.y) for geom in points.geometry]
    line = LineString(coords)
    
    # Project to metric CRS for accurate distance
    if points_gdf.crs.to_string().startswith('EPSG:'):
        # Use Estonia national grid for accuracy
        points_metric = points.to_crs('EPSG:3301')
        coords_metric = [(geom.x, geom.y) for geom in points_metric.geometry]
        line_metric = LineString(coords_metric)
        distance = line_metric.length
    else:
        distance = line.length
    
    print(f"Total distance traveled: {distance:.2f} meters")
    return distance
```

### Example 2: Cluster Points Using Time-Space

```python
from sklearn.cluster import DBSCAN
import numpy as np

def cluster_stops(gdf, timestamp_col, eps_meters=100, eps_time_minutes=30):
    """Identify places where user stayed (temporal-spatial clustering)"""
    
    # Extract coordinates and time
    coords = np.array([[geom.x, geom.y] for geom in gdf.geometry])
    
    # Spatial clustering (DBSCAN)
    clustering = DBSCAN(eps=eps_meters/111000, min_samples=2).fit(coords)  # meters to degrees
    
    gdf['cluster'] = clustering.labels_
    
    # Analyze clusters
    clusters = gdf[gdf['cluster'] != -1].groupby('cluster').agg({
        'cluster': 'count',  # Number of points
        'geometry': 'first',  # Example location
        timestamp_col: ['min', 'max']  # Time range
    })
    
    return gdf, clusters
```

### Example 3: Create Interactive Map with Folium

```python
import folium
from folium import plugins

def create_interactive_map(user_gdf, trajectory, output_html='interactive_map.html'):
    """Create interactive map using Folium"""
    
    # Get center of map
    bounds = user_gdf.total_bounds
    center = [(bounds[1] + bounds[3])/2, (bounds[0] + bounds[2])/2]
    
    # Create map
    m = folium.Map(location=center, zoom_start=12)
    
    # Add points with popups
    for idx, row in user_gdf.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=3,
            popup=f"Time: {row['timestamp']}" if 'timestamp' in row else None,
            color='blue',
            fill=True
        ).add_to(m)
    
    # Add trajectory line
    if trajectory:
        coords = [(y, x) for x, y in trajectory.coords]
        folium.PolyLine(
            coords,
            color='blue',
            weight=2,
            opacity=0.6
        ).add_to(m)
    
    m.save(output_html)
    print(f"Interactive map saved: {output_html}")
    return m
```

### Example 4: Heatmap of Activity

```python
import numpy as np
from scipy.stats import gaussian_kde

def create_activity_heatmap(gdf, title='Activity Heatmap'):
    """Create heatmap showing intensity of user activity"""
    
    # Extract coordinates
    x = gdf.geometry.x.values
    y = gdf.geometry.y.values
    
    # Create 2D density estimation
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)
    
    # Plot
    fig, ax = plt.subplots(figsize=(12, 10))
    scatter = ax.scatter(x, y, c=z, s=50, cmap='hot', alpha=0.6)
    plt.colorbar(scatter, ax=ax, label='Activity Intensity')
    ax.set_title(title)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    plt.tight_layout()
    plt.savefig('activity_heatmap.png', dpi=300)
    plt.close()
    
    print("Activity heatmap saved: activity_heatmap.png")
```

---

## Performance Optimization

### Tip 1: Filter Before Loading Large Layers

```python
# Load only a subset of data
import geopandas as gpd

# By bounding box
bounds = (24.0, 58.0, 28.0, 60.0)
user_a = gpd.read_file("data/mobile_data.gdb", 
                       layer='mobile_data_user_a',
                       bbox=bounds)

print(f"Loaded {len(user_a)} features")
```

### Tip 2: Use CRS Appropriate for Your Region

```python
# For Estonia, use national grid for accurate distance calculations
gdf = gdf.to_crs('EPSG:3301')  # Estonia national grid
```

### Tip 3: Simplify Geometries for Large Datasets

```python
from shapely.geometry import LineString

# Simplify trajectory for visualization/export
trajectory_simplified = trajectory.simplify(tolerance=0.0001)
print(f"Original coordinates: {len(trajectory.coords)}")
print(f"Simplified coordinates: {len(trajectory_simplified.coords)}")
```

### Tip 4: Process Data in Chunks

```python
def process_by_month(gdf, timestamp_col):
    """Process data monthly to manage memory"""
    gdf['year_month'] = gdf[timestamp_col].dt.to_period('M')
    
    for period, group in gdf.groupby('year_month'):
        print(f"Processing {period}: {len(group)} records")
        # Process group...
```

---

## Common Adjustments

### Change Visualization Style

```python
# In plot_user_trajectory() function, modify:

# Point colors by day of week
scatter = ax.scatter(
    points.geometry.x, 
    points.geometry.y,
    c=points[timestamp_col].dt.dayofweek,
    cmap='tab10',
    s=50,
    alpha=0.6,
    label='Points (colored by day)'
)

# Or by speed (requires distance calculation)
```

### Add Statistics to Output

```python
def generate_summary_statistics(user_gdf, timestamp_col):
    """Generate summary statistics for the analysis"""
    
    stats = {
        'total_points': len(user_gdf),
        'time_span': user_gdf[timestamp_col].max() - user_gdf[timestamp_col].min(),
        'points_per_day': len(user_gdf) / ((user_gdf[timestamp_col].max() - user_gdf[timestamp_col].min()).days + 1),
        'spatial_extent': user_gdf.total_bounds,
    }
    
    return stats

# Use in workflow
stats = generate_summary_statistics(user_a, 'timestamp')
for key, value in stats.items():
    print(f"{key}: {value}")
```

---

## Resources

- **GeoPandas:** https://geopandas.org/docs/reference/index.html
- **Shapely:** https://shapely.readthedocs.io/
- **Matplotlib:** https://matplotlib.org/stable/gallery/index.html
- **Fiona:** https://fiona.readthedocs.io/
- **Folium (Interactive Maps):** https://python-visualization.github.io/folium/

---

For more help, refer to the main README.md or modify and test code snippets directly in Python.
