"""
Advanced Trajectory Analysis - Daily Rhythms, Outlier Detection, and Temporal Patterns

This script extends the basic spatial analysis with:
- Daily rhythm decomposition
- Inactivity periods (when nothing happens)
- Outlier detection (speed, distance anomalies)
- Temporal filtering (by month, day, hour)
- Time series visualization
- Statistics tables and graphs

Author: Advanced Trajectory Analysis
Date: March 2026
"""

import os
import warnings
import pandas as pd
import geopandas as gpd
import fiona
from shapely.geometry import Point, LineString
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.dates import DateFormatter, HourLocator
from matplotlib.gridspec import GridSpec
import numpy as np
from scipy.stats import zscore
from datetime import datetime, timedelta
import seaborn as sns

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

GDB_PATH = "cvic04.gdb"
OUTPUT_DIR = "out/iter_02_advanced_temporal"
NIGHT_START_HOUR = 0
NIGHT_END_HOUR = 6

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_output_directory():
    """Create output directory if it doesn't exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created output directory: {OUTPUT_DIR}")

def load_layer(gdb_path, layer_name):
    """Load a single layer from GDB."""
    try:
        gdf = gpd.read_file(gdb_path, layer=layer_name)
        print(f"✓ Loaded '{layer_name}': {len(gdf)} features")
        return gdf
    except Exception as e:
        print(f"✗ Failed to load '{layer_name}': {e}")
        return None

# ============================================================================
# TEMPORAL ANALYSIS FUNCTIONS
# ============================================================================

def extract_temporal_features(gdf, timestamp_col):
    """Extract temporal features from timestamp column."""
    gdf = gdf.copy()
    gdf[timestamp_col] = pd.to_datetime(gdf[timestamp_col])
    
    gdf['year'] = gdf[timestamp_col].dt.year
    gdf['month'] = gdf[timestamp_col].dt.month
    gdf['month_name'] = gdf[timestamp_col].dt.strftime('%B')
    gdf['day'] = gdf[timestamp_col].dt.day
    gdf['weekday'] = gdf[timestamp_col].dt.dayofweek  # 0=Monday, 6=Sunday
    gdf['weekday_name'] = gdf[timestamp_col].dt.strftime('%A')
    gdf['hour'] = gdf[timestamp_col].dt.hour
    gdf['minute'] = gdf[timestamp_col].dt.minute
    gdf['date'] = gdf[timestamp_col].dt.date
    
    return gdf

def calculate_distances(points_gdf):
    """Calculate distance between consecutive points in meters."""
    points_gdf = points_gdf.copy()
    
    # Project to metric CRS for accurate distance
    points_metric = points_gdf.to_crs('EPSG:3301')  # Estonian grid
    
    # Calculate distance to next point
    distances = []
    for i in range(len(points_metric)):
        if i < len(points_metric) - 1:
            point1 = points_metric.geometry.iloc[i]
            point2 = points_metric.geometry.iloc[i + 1]
            dist = point1.distance(point2)
        else:
            dist = np.nan
        distances.append(dist)
    
    points_gdf['distance_to_next_m'] = distances
    return points_gdf

def calculate_time_gaps(points_gdf, timestamp_col):
    """Calculate time gaps between consecutive points in hours."""
    points_gdf = points_gdf.copy()
    
    time_gaps = []
    for i in range(len(points_gdf)):
        if i < len(points_gdf) - 1:
            time_diff = points_gdf[timestamp_col].iloc[i + 1] - points_gdf[timestamp_col].iloc[i]
            gap_hours = time_diff.total_seconds() / 3600
        else:
            gap_hours = np.nan
        time_gaps.append(gap_hours)
    
    points_gdf['time_gap_hours'] = time_gaps
    return points_gdf

def calculate_speed(points_gdf):
    """Calculate speed between consecutive points in km/h."""
    points_gdf = points_gdf.copy()
    
    # Speed = distance / time
    speeds = []
    for i in range(len(points_gdf)):
        if i < len(points_gdf) - 1:
            dist_m = points_gdf['distance_to_next_m'].iloc[i]
            time_h = points_gdf['time_gap_hours'].iloc[i]
            
            if pd.notna(dist_m) and pd.notna(time_h) and time_h > 0:
                speed_kmh = (dist_m / 1000) / time_h
            else:
                speed_kmh = np.nan
        else:
            speed_kmh = np.nan
        speeds.append(speed_kmh)
    
    points_gdf['speed_kmh'] = speeds
    return points_gdf

def detect_inactivity_periods(points_gdf, timestamp_col, min_gap_hours=1):
    """Detect periods where user was inactive (same location)."""
    inactivity = []
    
    for i in range(len(points_gdf)):
        if i < len(points_gdf) - 1:
            dist = points_gdf['distance_to_next_m'].iloc[i]
            gap = points_gdf['time_gap_hours'].iloc[i]
            
            # Inactivity: very small distance + time gap
            if pd.notna(dist) and pd.notna(gap):
                is_inactive = (dist < 50 and gap >= min_gap_hours)  # <50m movement
            else:
                is_inactive = False
        else:
            is_inactive = False
        
        inactivity.append(is_inactive)
    
    points_gdf['is_inactive'] = inactivity
    return points_gdf

def detect_outliers(points_gdf, speed_threshold_kmh=100, gap_threshold_hours=24):
    """Detect outliers: unrealistic speeds and unusual gaps."""
    points_gdf = points_gdf.copy()
    
    outliers = []
    for i in range(len(points_gdf)):
        speed = points_gdf['speed_kmh'].iloc[i]
        gap = points_gdf['time_gap_hours'].iloc[i]
        
        is_outlier = False
        
        # Unrealistic speed (e.g., >100 km/h movement between points)
        if pd.notna(speed) and speed > speed_threshold_kmh:
            is_outlier = True
        
        # Unusual time gap (e.g., >24 hours)
        if pd.notna(gap) and gap > gap_threshold_hours:
            is_outlier = True
        
        outliers.append(is_outlier)
    
    points_gdf['is_outlier'] = outliers
    return points_gdf

def generate_inactivity_summary(points_gdf, timestamp_col, user_name):
    """Generate summary of inactivity periods."""
    print(f"\n{'='*70}")
    print(f"Inactivity Analysis: {user_name}")
    print(f"{'='*70}\n")
    
    total_points = len(points_gdf)
    inactive_points = points_gdf['is_inactive'].sum()
    inactive_ratio = (inactive_points / total_points * 100) if total_points > 0 else 0
    
    print(f"Total points: {total_points}")
    print(f"Inactive periods: {inactive_points} ({inactive_ratio:.1f}%)")
    print(f"Mobile periods: {total_points - inactive_points} ({100 - inactive_ratio:.1f}%)")
    
    # Inactivity by hour
    inactive_by_hour = points_gdf[points_gdf['is_inactive']].groupby('hour').size()
    print(f"\nInactivity by hour of day:")
    for hour in range(24):
        count = inactive_by_hour.get(hour, 0)
        bar = '█' * (count // (max(inactive_by_hour.max() // 10, 1)) if len(inactive_by_hour) > 0 else 0)
        print(f"  {hour:02d}:00 - {hour+1:02d}:00  {bar}  ({count} periods)")
    
    return {
        'total_points': total_points,
        'inactive_points': inactive_points,
        'inactive_ratio': inactive_ratio,
        'inactive_by_hour': inactive_by_hour
    }

def generate_outlier_summary(points_gdf, user_name):
    """Generate summary of detected outliers."""
    print(f"\n{'='*70}")
    print(f"Outlier Detection: {user_name}")
    print(f"{'='*70}\n")
    
    total_points = len(points_gdf)
    outlier_count = points_gdf['is_outlier'].sum()
    outlier_ratio = (outlier_count / total_points * 100) if total_points > 0 else 0
    
    print(f"Total points: {total_points}")
    print(f"Detected outliers: {outlier_count} ({outlier_ratio:.1f}%)")
    
    # Speed statistics
    valid_speeds = points_gdf[points_gdf['speed_kmh'].notna()]['speed_kmh']
    if len(valid_speeds) > 0:
        print(f"\nSpeed statistics (km/h):")
        print(f"  Mean: {valid_speeds.mean():.2f}")
        print(f"  Median: {valid_speeds.median():.2f}")
        print(f"  Max: {valid_speeds.max():.2f}")
        print(f"  95th percentile: {valid_speeds.quantile(0.95):.2f}")
        
        # Count outlier speeds
        outlier_speeds = points_gdf[points_gdf['speed_kmh'] > 100]
        print(f"  Points with speed >100 km/h: {len(outlier_speeds)}")
    
    # Time gap statistics
    valid_gaps = points_gdf[points_gdf['time_gap_hours'].notna()]['time_gap_hours']
    if len(valid_gaps) > 0:
        print(f"\nTime gap statistics (hours):")
        print(f"  Mean: {valid_gaps.mean():.3f}")
        print(f"  Median: {valid_gaps.median():.3f}")
        print(f"  Max: {valid_gaps.max():.2f}")
        print(f"  95th percentile: {valid_gaps.quantile(0.95):.3f}")
        
        # Count unusual gaps
        unusual_gaps = points_gdf[points_gdf['time_gap_hours'] > 24]
        print(f"  Points with gap >24 hours: {len(unusual_gaps)}")
    
    # Show top 5 outliers
    outliers = points_gdf[points_gdf['is_outlier']].copy()
    if len(outliers) > 0:
        print(f"\nTop 5 outliers:")
        for idx, row in outliers.head(5).iterrows():
            speed_str = f"{row.get('speed_kmh'):.1f}" if pd.notna(row.get('speed_kmh')) else 'N/A'
            gap_str = f"{row.get('time_gap_hours'):.1f}" if pd.notna(row.get('time_gap_hours')) else 'N/A'
            print(f"  {idx}: Speed={speed_str} km/h, Gap={gap_str} hours")
    
    return {
        'total_points': total_points,
        'outlier_count': outlier_count,
        'outlier_ratio': outlier_ratio,
        'outlier_speeds': (points_gdf['speed_kmh'] > 100).sum(),
        'unusual_gaps': (points_gdf['time_gap_hours'] > 24).sum()
    }

# ============================================================================
# TEMPORAL FILTERING & AGGREGATION
# ============================================================================

def generate_hourly_statistics(points_gdf):
    """Generate hourly activity statistics."""
    hourly_stats = points_gdf.groupby('hour').agg({
        'geometry': 'count',
        'distance_to_next_m': 'sum',
        'speed_kmh': 'mean'
    }).rename(columns={'geometry': 'point_count'})
    
    # Ensure all 24 hours are present
    hourly_stats = hourly_stats.reindex(range(24), fill_value=0)
    
    hourly_stats['avg_distance_m'] = (
        hourly_stats['distance_to_next_m'] / hourly_stats['point_count']
    ).fillna(0)
    
    return hourly_stats

def generate_daily_statistics(points_gdf):
    """Generate daily activity statistics."""
    daily_stats = points_gdf.groupby(['date', 'weekday_name']).agg({
        'geometry': 'count',
        'distance_to_next_m': 'sum',
        'speed_kmh': 'mean',
        'is_inactive': 'sum'
    }).rename(columns={'geometry': 'point_count', 'is_inactive': 'inactive_count'})
    
    daily_stats['total_distance_km'] = daily_stats['distance_to_next_m'] / 1000
    
    return daily_stats

def generate_monthly_statistics(points_gdf):
    """Generate monthly activity statistics."""
    monthly_stats = points_gdf.groupby(['month', 'month_name']).agg({
        'geometry': 'count',
        'distance_to_next_m': 'sum',
        'speed_kmh': 'mean'
    }).rename(columns={'geometry': 'point_count'})
    
    monthly_stats['total_distance_km'] = monthly_stats['distance_to_next_m'] / 1000
    monthly_stats['days_with_data'] = points_gdf.groupby('month')['date'].nunique()
    monthly_stats['avg_points_per_day'] = (
        monthly_stats['point_count'] / monthly_stats['days_with_data']
    ).fillna(0)
    
    return monthly_stats

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_daily_rhythm(points_gdf, user_name, output_path=None):
    """Create comprehensive daily rhythm visualization."""
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)
    
    # 1. Hourly point count
    hourly_stats = generate_hourly_statistics(points_gdf)
    ax1 = fig.add_subplot(gs[0, :])
    bars = ax1.bar(range(24), hourly_stats['point_count'], color='steelblue', alpha=0.7)
    ax1.set_xlabel('Hour of day')
    ax1.set_ylabel('Number of points recorded')
    ax1.set_title(f'{user_name} - Hourly Activity Pattern', fontsize=12, fontweight='bold')
    ax1.set_xticks(range(24))
    ax1.set_xticklabels([f'{h:02d}' for h in range(24)])
    ax1.grid(True, alpha=0.3)
    
    # Add night zone highlighting
    for i in range(NIGHT_START_HOUR, NIGHT_END_HOUR):
        ax1.axvspan(i - 0.5, i + 0.5, alpha=0.1, color='navy', label='Night' if i == NIGHT_START_HOUR else '')
    
    # 2. Hourly average speed
    ax2 = fig.add_subplot(gs[1, 0])
    valid_speeds = hourly_stats['speed_kmh'].dropna()
    if len(valid_speeds) > 0:
        ax2.bar(range(len(hourly_stats)), hourly_stats['speed_kmh'].fillna(0), color='coral', alpha=0.7)
        ax2.set_xlabel('Hour of day')
        ax2.set_ylabel('Average speed (km/h)')
        ax2.set_title('Average Speed by Hour', fontsize=11, fontweight='bold')
        ax2.set_xticks(range(24))
        ax2.set_xticklabels([f'{h:02d}' for h in range(24)], fontsize=8)
        ax2.grid(True, alpha=0.3)
    
    # 3. Inactivity distribution
    ax3 = fig.add_subplot(gs[1, 1])
    inactive_by_hour = points_gdf[points_gdf['is_inactive']].groupby('hour').size()
    inactive_by_hour = inactive_by_hour.reindex(range(24), fill_value=0)
    ax3.bar(range(24), inactive_by_hour.values, color='seagreen', alpha=0.7)
    ax3.set_xlabel('Hour of day')
    ax3.set_ylabel('Number of inactive periods')
    ax3.set_title('Inactivity Distribution by Hour', fontsize=11, fontweight='bold')
    ax3.set_xticks(range(24))
    ax3.set_xticklabels([f'{h:02d}' for h in range(24)], fontsize=8)
    ax3.grid(True, alpha=0.3)
    
    # 4. Weekday distribution
    ax4 = fig.add_subplot(gs[2, 0])
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_points = points_gdf.groupby('weekday_name').size().reindex(weekday_order)
    colors = ['steelblue' if day in ['Saturday', 'Sunday'] else 'steelblue' for day in weekday_order]
    ax4.bar(range(len(weekday_order)), weekday_points.values, color=colors, alpha=0.7)
    ax4.set_xticks(range(len(weekday_order)))
    ax4.set_xticklabels([d[:3] for d in weekday_order], rotation=45)
    ax4.set_ylabel('Number of points')
    ax4.set_title('Activity by Day of Week', fontsize=11, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 5. Monthly distribution
    ax5 = fig.add_subplot(gs[2, 1])
    monthly_points = points_gdf.groupby('month').size()
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    ax5.bar(monthly_points.index, monthly_points.values, color='mediumpurple', alpha=0.7)
    ax5.set_xticks(range(1, 13))
    ax5.set_xticklabels([month_names[i-1] for i in range(1, 13)], rotation=45)
    ax5.set_ylabel('Number of points')
    ax5.set_title('Activity by Month', fontsize=11, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    
    plt.suptitle(f'{user_name} - Daily Rhythm Analysis', fontsize=14, fontweight='bold', y=0.995)
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
    
    plt.close()

def plot_speed_distribution(points_gdf, user_name, output_path=None):
    """Visualize speed distribution and outliers."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    valid_speeds = points_gdf[points_gdf['speed_kmh'].notna()]['speed_kmh']
    outlier_speeds = valid_speeds[valid_speeds > 100]
    normal_speeds = valid_speeds[valid_speeds <= 100]
    
    # 1. Speed histogram
    ax = axes[0, 0]
    ax.hist(normal_speeds, bins=50, alpha=0.7, color='steelblue', label='Normal', edgecolor='black')
    if len(outlier_speeds) > 0:
        ax.hist(outlier_speeds, bins=20, alpha=0.7, color='red', label='Outliers (>100 km/h)', edgecolor='black')
    ax.set_xlabel('Speed (km/h)')
    ax.set_ylabel('Frequency')
    ax.set_title('Speed Distribution', fontsize=11, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Box plot
    ax = axes[0, 1]
    ax.boxplot([normal_speeds], labels=['Speed (km/h)'])
    ax.set_ylabel('Speed (km/h)')
    ax.set_title('Speed Box Plot', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 3. Speed by hour
    ax = axes[1, 0]
    hourly_speeds = points_gdf.groupby('hour')['speed_kmh'].mean()
    # Ensure all hours present
    hourly_speeds = hourly_speeds.reindex(range(24), fill_value=0)
    ax.plot(range(24), hourly_speeds.values, marker='o', linewidth=2, markersize=6)
    ax.axhline(y=100, color='red', linestyle='--', linewidth=2, label='Outlier threshold')
    ax.set_xlabel('Hour of day')
    ax.set_ylabel('Average speed (km/h)')
    ax.set_title('Speed Trend Throughout Day', fontsize=11, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. Statistics text
    ax = axes[1, 1]
    ax.axis('off')
    stats_text = f"""
    Speed Statistics
    ─────────────────────────
    Mean: {valid_speeds.mean():.2f} km/h
    Median: {valid_speeds.median():.2f} km/h
    Std Dev: {valid_speeds.std():.2f} km/h
    Min: {valid_speeds.min():.2f} km/h
    Max: {valid_speeds.max():.2f} km/h
    
    Percentiles:
    25th: {valid_speeds.quantile(0.25):.2f} km/h
    50th: {valid_speeds.quantile(0.50):.2f} km/h
    75th: {valid_speeds.quantile(0.75):.2f} km/h
    95th: {valid_speeds.quantile(0.95):.2f} km/h
    
    Outliers (>100 km/h): {len(outlier_speeds)}
    """
    ax.text(0.1, 0.5, stats_text, fontsize=10, family='monospace', 
            verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle(f'{user_name} - Speed Analysis', fontsize=13, fontweight='bold')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
    
    plt.close()

def plot_heatmap_hourly(points_gdf, user_name, output_path=None):
    """Create heatmap of activity by hour and day."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Create pivot table: rows=day of week, columns=hour
    heatmap_data = pd.crosstab(
        index=pd.Categorical(points_gdf['weekday_name'], 
                             categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                                       'Friday', 'Saturday', 'Sunday'],
                             ordered=True),
        columns=pd.Categorical(points_gdf['hour'], categories=range(24), ordered=True)
    ).fillna(0)
    
    sns.heatmap(heatmap_data, cmap='YlOrRd', annot=False, fmt='d', cbar_kws={'label': 'Point count'},
                ax=ax, linewidths=0.5, linecolor='gray')
    
    ax.set_xlabel('Hour of day')
    ax.set_ylabel('Day of week')
    ax.set_title(f'{user_name} - Activity Heatmap (Day vs Hour)', fontsize=12, fontweight='bold')
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
    
    plt.close()

# ============================================================================
# STATISTICS TABLE GENERATION
# ============================================================================

def create_statistics_tables(points_gdf, user_name, output_dir):
    """Create CSV tables with statistics."""
    
    # Hourly statistics
    hourly_stats = generate_hourly_statistics(points_gdf)
    hourly_path = os.path.join(output_dir, f'{user_name.lower()}_hourly_stats.csv')
    hourly_stats.to_csv(hourly_path)
    print(f"✓ Saved hourly statistics: {hourly_path}")
    
    # Daily statistics
    daily_stats = generate_daily_statistics(points_gdf)
    daily_path = os.path.join(output_dir, f'{user_name.lower()}_daily_stats.csv')
    daily_stats.to_csv(daily_path)
    print(f"✓ Saved daily statistics: {daily_path}")
    
    # Monthly statistics
    monthly_stats = generate_monthly_statistics(points_gdf)
    monthly_path = os.path.join(output_dir, f'{user_name.lower()}_monthly_stats.csv')
    monthly_stats.to_csv(monthly_path)
    print(f"✓ Saved monthly statistics: {monthly_path}")
    
    # Inactivity periods
    inactive_periods = points_gdf[points_gdf['is_inactive']][['hour', 'weekday_name', 'distance_to_next_m', 'time_gap_hours']].copy()
    inactive_path = os.path.join(output_dir, f'{user_name.lower()}_inactivity_periods.csv')
    inactive_periods.to_csv(inactive_path, index=False)
    print(f"✓ Saved inactivity periods: {inactive_path}")
    
    # Outlier points
    outlier_points = points_gdf[points_gdf['is_outlier']][
        ['hour', 'speed_kmh', 'time_gap_hours', 'distance_to_next_m']
    ].copy()
    outlier_path = os.path.join(output_dir, f'{user_name.lower()}_outlier_points.csv')
    outlier_points.to_csv(outlier_path, index=False)
    print(f"✓ Saved outlier points: {outlier_path}")

# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_user_trajectory(gdb_path, layer_name, user_label):
    """Complete trajectory analysis pipeline."""
    print(f"\n{'='*70}")
    print(f"Advanced Analysis: {user_label}")
    print(f"{'='*70}\n")
    
    # Load data
    gdf = load_layer(gdb_path, layer_name)
    if gdf is None:
        return None
    
    # Extract temporal features
    gdf = extract_temporal_features(gdf, 'pos_time')
    gdf = gdf.sort_values('pos_time')
    print(f"✓ Extracted temporal features")
    
    # Calculate motion metrics
    gdf = calculate_distances(gdf)
    gdf = calculate_time_gaps(gdf, 'pos_time')
    gdf = calculate_speed(gdf)
    print(f"✓ Calculated motion metrics (distance, time gaps, speed)")
    
    # Detect patterns
    gdf = detect_inactivity_periods(gdf, 'pos_time', min_gap_hours=1)
    gdf = detect_outliers(gdf, speed_threshold_kmh=100, gap_threshold_hours=24)
    print(f"✓ Detected inactivity periods and outliers")
    
    # Generate summaries
    generate_inactivity_summary(gdf, 'pos_time', user_label)
    generate_outlier_summary(gdf, user_label)
    
    # Create visualizations
    print(f"\nGenerating visualizations...")
    plot_daily_rhythm(gdf, user_label, 
                     os.path.join(OUTPUT_DIR, f'{user_label.lower()}_daily_rhythm.png'))
    plot_speed_distribution(gdf, user_label,
                           os.path.join(OUTPUT_DIR, f'{user_label.lower()}_speed_analysis.png'))
    plot_heatmap_hourly(gdf, user_label,
                       os.path.join(OUTPUT_DIR, f'{user_label.lower()}_heatmap.png'))
    
    # Create statistics tables
    print(f"\nGenerating statistics tables...")
    create_statistics_tables(gdf, user_label.lower(), OUTPUT_DIR)
    
    return gdf

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main analysis workflow."""
    print("\n" + "="*70)
    print("ADVANCED TRAJECTORY ANALYSIS - Daily Rhythms & Outlier Detection")
    print("="*70 + "\n")
    
    create_output_directory()
    
    # Analyze User A
    user_a_data = analyze_user_trajectory(GDB_PATH, 'mobile_data_user_a', 'User_A')
    
    # Analyze User B
    user_b_data = analyze_user_trajectory(GDB_PATH, 'mobile_data_user_b', 'User_B')
    
    print(f"\n{'='*70}")
    print("Analysis Complete!")
    print(f"{'='*70}")
    print(f"Results saved to: {OUTPUT_DIR}/\n")
    print("Generated files:")
    print("  - Visualizations: *_daily_rhythm.png, *_speed_analysis.png, *_heatmap.png")
    print("  - Statistics: *_hourly_stats.csv, *_daily_stats.csv, *_monthly_stats.csv")
    print("  - Patterns: *_inactivity_periods.csv, *_outlier_points.csv")

if __name__ == "__main__":
    main()
