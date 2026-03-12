# Pre-Run Checklist

Before running the GDB Spatial Analysis script, verify these requirements:

## ✅ Environment Setup

- [ ] **Python 3.7+** installed
  - Check: `python --version` or `python3 --version`
  - Install from: https://www.python.org/

- [ ] **Required packages** installed
  - Install: `pip install -r requirements.txt`
  - Verify: `python -c "import geopandas; import pandas; import fiona; import shapely; import matplotlib"`

- [ ] **Working directory** is set to project folder
  - Contains: `gdb_spatial_analysis.py`, `requirements.txt`, etc.

## 📁 Data Setup

- [ ] **GDB file** exists at specified path
  - Default path: `data/mobile_data.gdb`
  - Update `GDB_PATH` in script if different location

- [ ] **Layer names** are correct
  - Run this command to verify available layers:
    ```bash
    python -c "import fiona; print(fiona.listlayers('data/mobile_data.gdb'))"
    ```
  - Should include: `mobile_data_user_a`, `mobile_data_user_b`, etc.
  - Update `LAYERS_TO_LOAD` in script if names differ

- [ ] **Output directory** will be created automatically
  - By default: `analysis_results/`
  - Can be changed via `OUTPUT_DIR` variable

## 🗂️ File Structure

Verify your project folder looks like this:
```
project_folder/
├── gdb_spatial_analysis.py       ✓
├── README.md                      ✓
├── QUICKSTART.md                  ✓
├── EXAMPLES_AND_TIPS.md           ✓
├── requirements.txt               ✓
├── config.py                      ✓
├── run_analysis.bat (Windows)     ✓
├── run_analysis.sh (Linux/Mac)    ✓
├── data/
│   └── mobile_data.gdb/           ✓ (your GDB)
└── analysis_results/              (created by script)
```

## 🔧 Configuration

- [ ] **GDB path** is correct
  - Edit line in script: `GDB_PATH = "data/mobile_data.gdb"`

- [ ] **Required layers** exist in your GDB
  - Check against `LAYERS_TO_LOAD` list
  - Edit if your layer names differ

- [ ] **Timestamp column** name is known (optional)
  - Add to `timestamp_cols` list if non-standard name
  - Script auto-detects common names

- [ ] **Night hours window** is appropriate (optional)
  - Default: 00:00-06:00 for home estimation
  - Adjust `NIGHT_START_HOUR` and `NIGHT_END_HOUR` if needed

- [ ] **Output directory** path is acceptable
  - Default: `analysis_results/`
  - Change `OUTPUT_DIR` if needed

## 🎯 Data Quality

- [ ] **Geodatabase is valid**
  - Try opening in QGIS or similar to verify
  - Check file is not corrupted

- [ ] **Layers have geometry**
  - Should be Point or Polygon geometries
  - Not text-based or attribute-only layers

- [ ] **Timestamp data exists**
  - Check layers have a timestamp/time/datetime column
  - Values should be parseable as dates

- [ ] **CRS information is present**
  - All layers should have defined CRS
  - Can verify with: `geopandas.read_file(...).crs`

## 💾 Disk Space

- [ ] **Sufficient disk space** for outputs
  - Visualizations: ~1-5 MB each
  - GeoJSON exports: variable size
  - Rule of thumb: 2-3x your GDB size

- [ ] **Write permissions** in output directory
  - Should be writable by your user account

## 🚀 Before Running

1. **Backup your data** (optional but recommended)
   ```bash
   copy data/mobile_data.gdb data/mobile_data_backup.gdb
   ```

2. **Test with dry run** (optional)
   ```python
   # Quick namespace test
   import geopandas
   import geopandas as gpd
   gdf = gpd.read_file("data/mobile_data.gdb", layer="mobile_data_user_a")
   print(f"Loaded: {len(gdf)} features")
   ```

3. **Check available memory** for large datasets
   - Close other applications if needed
   - Monitor with Task Manager or Activity Monitor

## ✨ Ready to Run!

### Windows
```bash
run_analysis.bat
```
or
```bash
python gdb_spatial_analysis.py
```

### Linux/macOS
```bash
bash run_analysis.sh
```
or
```bash
python3 gdb_spatial_analysis.py
```

## 🆘 If Something Goes Wrong

1. **Check error message** - note the exact error
2. **Verify checklist items** above
3. **Try test command**:
   ```python
   import fiona
   import geopandas as gpd
   
   # List layers
   print(fiona.listlayers("data/mobile_data.gdb"))
   
   # Try loading one layer
   gdf = gpd.read_file("data/mobile_data.gdb", layer="mobile_data_user_a")
   print(gdf.head())
   ```
4. **Check README.md** Troubleshooting section
5. **Review EXAMPLES_AND_TIPS.md** for solutions

## 📋 Post-Run Verification

After successful run:

- [ ] `analysis_results/` folder created
- [ ] PNG files generated (*.png)
- [ ] GeoJSON files generated (*.geojson)
- [ ] Output files are valid and can be opened in QGIS
- [ ] File sizes are reasonable (not 0 bytes)

## 🎉 Success!

If you see output like:
```
============================================================
Analysis Complete!
============================================================
Results exported to: analysis_results/
```

...then your analysis ran successfully! Check the `analysis_results/` folder for your outputs.

---

**Questions?** See README.md and EXAMPLES_AND_TIPS.md for detailed documentation.
