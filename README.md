# ESRI File Geodatabase Spatial Analysis Script

A comprehensive Python script for spatial analysis of mobile user data and geographic information from ESRI File Geodatabase (.gdb) format.

## Features

✅ **Geodatabase Management**
- Automatically list all layers in a File Geodatabase
- Load specific feature classes (layers)
- Inspect layer properties and CRS

✅ **Data Processing**
- Convert timestamp columns to datetime format
- Sort points chronologically
- Extract hour information from timestamps
- Filter night-time points (00:00-06:00)

✅ **Spatial Analysis**
- Create trajectories (LineString) from point sequences
- Compute home location centroids from night-time points
- Optionally compute point density grids
- Analyze movement patterns over time

✅ **Visualization**
- Individual trajectory maps with hourly color coding
- Combined multi-user analysis maps
- BTS locations and administrative boundary overlays
- Legend-enhanced publication-quality maps

✅ **Data Export**
- Export trajectories as GeoJSON
- Export point data as GeoJSON
- Export estimated home locations as GeoJSON

## Requirements

### Python Packages
- `geopandas` - For geographic data manipulation
- `pandas` - For data handling and processing
- `fiona` - For file I/O with geospatial data formats
- `shapely` - For geometric operations
- `matplotlib` - For visualization

### Installation

#### Option 1: Using requirements.txt
```bash
pip install -r requirements.txt
```

#### Option 2: Manual Installation
```bash
pip install geopandas pandas fiona shapely matplotlib
```

#### Using Conda
```bash
conda create -n geoanalysis python=3.9
conda activate geoanalysis
conda install -c conda-forge geopandas fiona shapely matplotlib pandas
```

## Usage

### Setup

1. **Prepare your workspace:**
   ```
   project_folder/
   ├── gdb_spatial_analysis.py
   ├── README.md
   ├── requirements.txt
   ├── data/
   │   └── mobile_data.gdb/  (your geodatabase)
   └── analysis_results/     (created automatically)
   ```

2. **Update the geodatabase path** in the script (if different):
   ```python
   GDB_PATH = "data/mobile_data.gdb"  # Adjust as needed
   ```

3. **Customize required layers** (optional):
   ```python
   LAYERS_TO_LOAD = [
       'mobile_data_user_a',
       'mobile_data_user_b',
       'gps_data',
       'bts_locations',
       'lau1_maakond',
       'lau2_omavalitsus'
   ]
   ```

4. **Adjust home location estimation window** (optional):
   ```python
   NIGHT_START_HOUR = 0   # 00:00
   NIGHT_END_HOUR = 6     # 06:00
   ```

### Running the Script

```bash
python gdb_spatial_analysis.py
```

### Expected Output

The script will:
1. Display all layers available in the geodatabase
2. Load and inspect each required layer
3. Process user trajectories and compute statistics
4. Generate visualization maps (PNG format)
5. Export results as GeoJSON files
6. Print detailed progress messages and statistics

### Output Files

All results are saved in the `analysis_results/` directory:

```
analysis_results/
├── user_a_trajectory.png          # User A trajectory map
├── user_b_trajectory.png          # User B trajectory map
├── bts_and_boundaries.png         # Infrastructure and boundaries
├── combined_analysis.png          # Multi-user analysis
├── user_a_trajectory.geojson      # User A trajectory geometries
├── user_b_trajectory.geojson      # User B trajectory geometries
├── user_a_points.geojson          # User A movement points
├── user_b_points.geojson          # User B movement points
└── home_locations.geojson         # Estimated home locations
```

## Script Structure

### Configuration Section
```python
GDB_PATH = "data/mobile_data.gdb"
LAYERS_TO_LOAD = [...]
NIGHT_START_HOUR = 0
NIGHT_END_HOUR = 6
OUTPUT_DIR = "analysis_results"
```

### Key Functions

#### Data Loading
| Function | Purpose |
|----------|---------|
| `list_gdb_layers()` | List all layers in geodatabase |
| `load_gdb_layer()` | Load single layer |
| `load_all_required_layers()` | Load multiple specific layers |
| `inspect_geodataframe()` | Display layer properties and data |

#### Data Processing
| Function | Purpose |
|----------|---------|
| `convert_timestamp_column()` | Convert column to datetime |
| `extract_hour_from_timestamp()` | Extract hour for visualization |
| `filter_night_points()` | Filter points during night hours |
| `compute_home_location()` | Calculate home centroid |
| `create_trajectory()` | Create LineString from points |

#### Visualization
| Function | Purpose |
|----------|---------|
| `plot_user_trajectory()` | Map individual user trajectory |
| `plot_bts_and_boundaries()` | Map infrastructure and boundaries |
| `plot_combined_trajectories()` | Multi-user analysis map |

#### Export
| Function | Purpose |
|----------|---------|
| `export_to_geojson()` | Save GeoDataFrame as GeoJSON |

## Data Requirements

### Expected Layer Structure

**mobile_data_user_a / mobile_data_user_b**
- Point geometries
- Timestamp column (any of: `timestamp`, `time`, `datetime`, `date_time`, `created_at`)
- Optional: user ID, device info, signal strength, etc.

**gps_data**
- Point geometries
- Similar timestamp structure

**bts_locations**
- Point geometries (cell towers)
- Optional: tower ID, coverage info

**lau1_maakond** / **lau2_omavalitsus**
- Polygon geometries (administrative boundaries)

## Code Examples

### Example 1: Load and Inspect a Single Layer
```python
gdb_path = "data/mobile_data.gdb"
user_a = gpd.read_file(gdb_path, layer='mobile_data_user_a')
print(f"CRS: {user_a.crs}")
print(f"Shape: {user_a.shape}")
print(user_a.head())
```

### Example 2: Convert Timestamps and Sort
```python
user_a['timestamp'] = pd.to_datetime(user_a['timestamp'])
user_a = user_a.sort_values('timestamp')
```

### Example 3: Filter Night Points
```python
night_points = user_a[
    (user_a['timestamp'].dt.hour >= 0) & 
    (user_a['timestamp'].dt.hour < 6)
]
```

### Example 4: Create Trajectory
```python
coords = [(geom.x, geom.y) for geom in user_a.geometry]
trajectory = LineString(coords)
```

### Example 5: Compute Home Location
```python
home_lon = night_points.geometry.x.mean()
home_lat = night_points.geometry.y.mean()
home = Point(home_lon, home_lat)
```

## Troubleshooting

### Issue: "Layer not found" error
**Solution:** Check layer names using `fiona.listlayers(gdb_path)`

### Issue: Timestamp column not recognized
**Solution:** Update the `timestamp_cols` list in the script with your column name:
```python
timestamp_cols = ['your_column_name', 'timestamp', 'time', ...]
```

### Issue: Geometries not displaying on maps
**Solution:** Verify CRS matches across all layers:
```python
print(user_a.crs)
print(boundaries.crs)
```

### Issue: Memory error with large datasets
**Solution:** Process layers separately or filter before loading:
```python
# Load with spatial filter
gdf = gpd.read_file(gdb_path, layer='layer_name', 
                    bbox=(minx, miny, maxx, maxy))
```

## Advanced Customization

### Modify Home Location Definition
Change `NIGHT_START_HOUR` and `NIGHT_END_HOUR` in the configuration section.

### Add Custom Timestamp Format
Update the datetime conversion:
```python
user_gdf = convert_timestamp_column(user_gdf, timestamp_col, 
                                   datetime_format='%Y-%m-%d %H:%M:%S')
```

### Adjust Visualization Styling
Modify the plotting functions to customize colors, sizes, and styles:
```python
# In plot_user_trajectory():
points.plot(ax=ax, color='red', markersize=100, alpha=0.8)
```

### Export Additional Formats
Add export functions for additional formats (Shapefile, GeoPackage, etc.):
```python
gdf.to_file('output.shp', driver='ESRI Shapefile')
gdf.to_file('output.gpkg', layer='data', driver='GPKG')
```

## Performance Tips

- **Large datasets:** Filter by spatial extent or time range before loading
- **Fast processing:** Use `simplify()` on geometries before creating trajectories
- **Memory optimization:** Process users separately and concatenate results
- **Visualization:** Reduce marker size or use sampling for dense point clouds

## References

- [GeoPandas Documentation](https://geopandas.org/)
- [Fiona Documentation](https://fiona.readthedocs.io/)
- [Shapely Documentation](https://shapely.readthedocs.io/)
- [Matplotlib Basemap](https://matplotlib.org/)

## License

This script is provided as-is for educational and research purposes.

## Author Notes

The script is designed for flexibility and extensibility. Modify functions as needed for your specific use case. Common customizations include:
- Additional timestamp column formats
- Custom density calculations
- Modified visualization styles
- Additional geographic analysis methods

---

**Last Updated:** March 2026
