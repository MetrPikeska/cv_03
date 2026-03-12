"""
Configuration file for GDB Spatial Analysis

Modify this file to customize the analysis without editing the main script.
"""

# ============================================================================
# DATA PATHS
# ============================================================================

# Path to the ESRI File Geodatabase
GDB_PATH = "data/mobile_data.gdb"

# Output directory for results
OUTPUT_DIR = "analysis_results"

# ============================================================================
# LAYERS TO LOAD
# ============================================================================

LAYERS_TO_LOAD = [
    'mobile_data_user_a',
    'mobile_data_user_b',
    'gps_data',
    'bts_locations',
    'lau1_maakond',
    'lau2_omavalitsus'
]

# ============================================================================
# TEMPORAL ANALYSIS
# ============================================================================

# Night hours for home location estimation (24-hour format)
NIGHT_START_HOUR = 0   # 00:00 (midnight)
NIGHT_END_HOUR = 6     # 06:00 (6 AM)

# Possible timestamp column names (script will search in this order)
TIMESTAMP_COLUMN_NAMES = [
    'timestamp',
    'time',
    'datetime',
    'date_time',
    'created_at',
    'date_recorded',
    'record_time'
]

# Datetime format (if known, leave as None for auto-detection)
DATETIME_FORMAT = None
# Examples: '%Y-%m-%d %H:%M:%S' or '%d/%m/%Y %H:%M:%S'

# ============================================================================
# SPATIAL ANALYSIS PARAMETERS
# ============================================================================

# Grid size for point density calculation (in degrees for lat/lon data)
POINT_DENSITY_GRID_SIZE = 0.01

# Minimum number of points required to create a trajectory
MIN_TRAJECTORY_POINTS = 2

# ============================================================================
# VISUALIZATION SETTINGS
# ============================================================================

# Figure size for maps (width, height in inches)
MAP_FIGURE_SIZE = (12, 10)
COMBINED_MAP_FIGURE_SIZE = (14, 11)

# DPI for saved images (higher = better quality, larger file size)
MAP_DPI = 300

# Color scheme for trajectories
USER_A_COLOR = 'blue'
USER_B_COLOR = 'green'
BTS_COLOR = 'red'
BOUNDARY_COLOR = 'lightgray'

# Transparency settings (0-1, where 1 is opaque)
TRAJECTORY_ALPHA = 0.6
POINT_ALPHA = 0.4
BOUNDARY_ALPHA = 0.3

# Marker sizes
POINT_MARKER_SIZE = 50
COMBINED_POINT_SIZE = 20
BTS_MARKER_SIZE = 100
HOME_MARKER_SIZE = 20

# ============================================================================
# EXPORT SETTINGS
# ============================================================================

# Whether to remove non-serializable columns before GeoJSON export
CLEAN_FOR_EXPORT = True

# Coordinate reference system for exported files
# Use 'EPSG:4326' for WGS84 (lat/lon) or keep as-is to use source CRS
EXPORT_CRS = 'EPSG:4326'

# ============================================================================
# OUTPUT FILE NAMING
# ============================================================================

# Customize output file names
OUTPUT_FILES = {
    'user_a_trajectory': 'user_a_trajectory.png',
    'user_b_trajectory': 'user_b_trajectory.png',
    'bts_boundaries': 'bts_and_boundaries.png',
    'combined': 'combined_analysis.png',
    'user_a_traj_geojson': 'user_a_trajectory.geojson',
    'user_b_traj_geojson': 'user_b_trajectory.geojson',
    'user_a_points_geojson': 'user_a_points.geojson',
    'user_b_points_geojson': 'user_b_points.geojson',
    'home_locations': 'home_locations.geojson',
}

# ============================================================================
# ANALYSIS FLAGS
# ============================================================================

# Enable/disable specific analysis steps
ENABLE_LOGGING = True              # Print detailed progress messages
COMPUTE_TRAJECTORIES = True        # Create LineString trajectories
COMPUTE_HOME_LOCATIONS = True      # Estimate home from night points
COMPUTE_DENSITY = False            # Compute point density grids
CREATE_VISUALIZATIONS = True       # Generate PNG maps
EXPORT_RESULTS = True              # Export results as GeoJSON

# ============================================================================
# FILTER PARAMETERS (optional)
# ============================================================================

# Geographic bounds to filter (None = use all data)
# Format: (minx, miny, maxx, maxy)
SPATIAL_FILTER = None
# Example: SPATIAL_FILTER = (24.0, 58.0, 28.0, 60.0)

# Temporal bounds to filter (None = use all data)
# Format: ('YYYY-MM-DD', 'YYYY-MM-DD')
TEMPORAL_FILTER = None
# Example: TEMPORAL_FILTER = ('2024-01-01', '2024-01-31')

# ============================================================================
# LAYER-SPECIFIC SETTINGS
# ============================================================================

# Settings for each layer type
LAYER_SETTINGS = {
    'mobile_data_user_a': {
        'enabled': True,
        'label': 'User A',
        'color': USER_A_COLOR,
    },
    'mobile_data_user_b': {
        'enabled': True,
        'label': 'User B',
        'color': USER_B_COLOR,
    },
    'gps_data': {
        'enabled': True,
        'label': 'GPS Data',
    },
    'bts_locations': {
        'enabled': True,
        'label': 'Base Stations',
        'color': BTS_COLOR,
    },
    'lau1_maakond': {
        'enabled': False,  # Set to True to use for visualization
        'label': 'Counties',
    },
    'lau2_omavalitsus': {
        'enabled': True,
        'label': 'Municipalities',
    },
}

# ============================================================================
# ADVANCED SETTINGS
# ============================================================================

# Coordinate rounding precision for trajectory simplification
COORDINATE_PRECISION = 6

# Whether to remove duplicate points before trajectory creation
REMOVE_DUPLICATES = True

# CRS for internal calculations (affects distance/area calculations)
WORKING_CRS = 'EPSG:4326'  # WGS84
# WORKING_CRS = 'EPSG:3301'  # Estonian national grid

# ============================================================================
# END OF CONFIGURATION
# ============================================================================
