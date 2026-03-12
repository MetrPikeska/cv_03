# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or with conda:
```bash
conda create -n geoanalysis -c conda-forge geopandas fiona shapely matplotlib pandas
conda activate geoanalysis
```

## 2. Prepare Your Data

Place your `.gdb` file in a `data/` folder or update the path in the script:

```python
GDB_PATH = "path/to/your/database.gdb"
```

## 3. Run the Script

```bash
python gdb_spatial_analysis.py
```

## 4. View Results

Check the `analysis_results/` folder for:
- 📊 PNG maps
- 🗺️ GeoJSON files

## Common Tasks

### Verify Layer Names
Before running, check what layers are available:

```python
import fiona
layers = fiona.listlayers("data/mobile_data.gdb")
print(layers)
```

### Adjust Analysis Window

Edit the configuration section:
```python
NIGHT_START_HOUR = 22  # 10 PM
NIGHT_END_HOUR = 8     # 8 AM
```

### Change Output Directory

```python
OUTPUT_DIR = "my_results"
```

## File Structure After Running

```
your_project/
├── gdb_spatial_analysis.py
├── README.md
├── requirements.txt
├── QUICKSTART.md (this file)
├── data/
│   └── cvic04.gdb/
└── analysis_results/
    ├── user_a_trajectory.png
    ├── user_b_trajectory.png
    ├── combined_analysis.png
    ├── bts_and_boundaries.png
    ├── user_a_trajectory.geojson
    ├── user_b_trajectory.geojson
    ├── user_a_points.geojson
    ├── user_b_points.geojson
    └── home_locations.geojson
```

## Next Steps

1. **Customize timestamps:** Modify `timestamp_cols` if your column has a different name
2. **Add filters:** Restrict analysis to specific time periods or geographic areas
3. **Extend analysis:** Add your own functions for additional spatial operations
4. **Export formats:** Modify export functions to save in different formats (Shapefile, GeoPackage, etc.)

## Help & Troubleshooting

See `README.md` for detailed troubleshooting and advanced customization options.
