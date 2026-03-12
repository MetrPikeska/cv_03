"""
Interactive Filtering Tool - Filter Trajectories by Month, Day, Hour

Umožňuje filtrovat mobilní data a generovat analýzu pro specifické časové období.

Příklady:
  - Analyzuj User A pouze v létě (červen-srpen)
  - Analyzuj User B jen v pracovní doby (9-17:00)
  - Porovnej víkend vs. pracovní den
  - Co se děje v určitý měsíc?

Author: Time-based Filtering Tool
Date: March 2026
"""

import os
import warnings
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns

try:
    import contextily as ctx
    CONTEXTILY_AVAILABLE = True
except ImportError:
    CONTEXTILY_AVAILABLE = False
    print("[!] contextily not available - maps will be generated without basemap")

warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================

GDB_PATH = "cvic04.gdb"
OUTPUT_DIR = "out/iter_03_interactive_filtering"

# ============================================================================
# FILTERING FUNCTIONS
# ============================================================================

def load_and_prepare_data(gdb_path, layer_name):
    """Load and prepare data for filtering."""
    gdf = gpd.read_file(gdb_path, layer=layer_name)
    gdf['pos_time'] = pd.to_datetime(gdf['pos_time'])
    
    # Extract temporal features
    gdf['year'] = gdf['pos_time'].dt.year
    gdf['month'] = gdf['pos_time'].dt.month
    gdf['month_name'] = gdf['pos_time'].dt.strftime('%B')
    gdf['day'] = gdf['pos_time'].dt.day
    gdf['weekday'] = gdf['pos_time'].dt.dayofweek
    gdf['weekday_name'] = gdf['pos_time'].dt.strftime('%A')
    gdf['hour'] = gdf['pos_time'].dt.hour
    gdf['date'] = gdf['pos_time'].dt.date
    
    gdf = gdf.sort_values('pos_time')
    return gdf

def filter_by_months(gdf, months):
    """Filter by month numbers (1-12)."""
    return gdf[gdf['month'].isin(months)].copy()

def filter_by_days(gdf, days):
    """Filter by day of month (1-31)."""
    return gdf[gdf['day'].isin(days)].copy()

def filter_by_hours(gdf, hours):
    """Filter by hour of day (0-23)."""
    return gdf[gdf['hour'].isin(hours)].copy()

def filter_by_weekdays(gdf, weekday_names):
    """Filter by day names (Monday, Tuesday, etc.)."""
    return gdf[gdf['weekday_name'].isin(weekday_names)].copy()

def filter_by_date_range(gdf, start_date, end_date):
    """Filter by date range."""
    mask = (gdf['date'] >= start_date) & (gdf['date'] <= end_date)
    return gdf[mask].copy()

# ============================================================================
# ANALYSIS FOR FILTERED DATA
# ============================================================================

def calculate_metrics(gdf):
    """Calculate key metrics for filtered data."""
    if len(gdf) == 0:
        return None
    
    # Project to metric CRS
    gdf_metric = gdf.to_crs('EPSG:3301')
    
    # Calculate distances
    distances = []
    for i in range(len(gdf_metric) - 1):
        p1 = gdf_metric.geometry.iloc[i]
        p2 = gdf_metric.geometry.iloc[i + 1]
        distances.append(p1.distance(p2))
    distances.append(np.nan)
    
    # Calculate time gaps
    time_gaps = []
    for i in range(len(gdf) - 1):
        gap = (gdf['pos_time'].iloc[i + 1] - gdf['pos_time'].iloc[i]).total_seconds() / 3600
        time_gaps.append(gap)
    time_gaps.append(np.nan)
    
    # Calculate speeds
    speeds = []
    for i in range(len(distances)):
        if pd.notna(distances[i]) and pd.notna(time_gaps[i]) and time_gaps[i] > 0:
            speed = (distances[i] / 1000) / time_gaps[i]
        else:
            speed = np.nan
        speeds.append(speed)
    
    gdf['distance_m'] = distances
    gdf['time_gap_h'] = time_gaps
    gdf['speed_kmh'] = speeds
    
    return gdf

def get_summary_stats(gdf, filter_desc):
    """Generate summary statistics."""
    if len(gdf) == 0:
        return None
    
    total_dist_mm = gdf['distance_m'].sum() if 'distance_m' in gdf.columns else 0
    
    summary = {
        'Filter': filter_desc,
        'Total Points': len(gdf),
        'Date Range': f"{gdf['date'].min()} to {gdf['date'].max()}",
        'Days with Data': gdf['date'].nunique(),
        'Total Distance (km)': total_dist_mm / 1000 if total_dist_mm > 0 else 0,
        'Avg Speed (km/h)': gdf['speed_kmh'].mean() if 'speed_kmh' in gdf.columns else 0,
        'Max Speed (km/h)': gdf['speed_kmh'].max() if 'speed_kmh' in gdf.columns else 0,
    }
    
    return summary

# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_comparison(original_gdf, filtered_gdf, filter_title, output_path=None):
    """Compare original vs. filtered data."""
    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.3)
    
    # 1. Map: Original data
    ax1 = fig.add_subplot(gs[0, 0])
    orig_projected = original_gdf.to_crs('EPSG:4326')
    orig_projected.plot(ax=ax1, color='lightblue', markersize=1, alpha=0.5)
    ax1.set_title('Original Data', fontweight='bold')
    ax1.set_xlabel('Longitude')
    ax1.set_ylabel('Latitude')
    
    # 2. Map: Filtered data
    ax2 = fig.add_subplot(gs[0, 1])
    filt_projected = filtered_gdf.to_crs('EPSG:4326')
    filt_projected.plot(ax=ax2, color='red', markersize=3, alpha=0.7)
    ax2.set_title(f'Filtered Data: {filter_title}', fontweight='bold', color='red')
    ax2.set_xlabel('Longitude')
    ax2.set_ylabel('Latitude')
    
    # 3. Map: Overlay
    ax3 = fig.add_subplot(gs[0, 2])
    orig_projected.plot(ax=ax3, color='lightblue', markersize=1, alpha=0.3, label='All data')
    filt_projected.plot(ax=ax3, color='red', markersize=3, alpha=0.7, label='Filtered')
    ax3.set_title('Overlay Comparison', fontweight='bold')
    ax3.legend()
    ax3.set_xlabel('Longitude')
    ax3.set_ylabel('Latitude')
    
    # 4. Timeline
    ax4 = fig.add_subplot(gs[1, :2])
    
    # Distribution over time
    orig_by_day = original_gdf.groupby('date').size()
    filt_by_day = filtered_gdf.groupby('date').size()
    
    ax4.plot(orig_by_day.index, orig_by_day.values, label='All data', alpha=0.5, linewidth=1)
    ax4.plot(filt_by_day.index, filt_by_day.values, label='Filtered', color='red', linewidth=2)
    ax4.set_title('Activity Over Time', fontweight='bold')
    ax4.set_xlabel('Date')
    ax4.set_ylabel('Points per day')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Statistics
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.axis('off')
    
    orig_count = len(original_gdf)
    filt_count = len(filtered_gdf)
    ratio = (filt_count / orig_count * 100) if orig_count > 0 else 0
    
    stats_text = f"""
    Comparison Statistics
    ─────────────────────────
    Original points: {orig_count:,}
    Filtered points: {filt_count:,}
    Percentage: {ratio:.1f}%
    
    Date ranges:
    Original: {original_gdf['date'].min()} 
             to {original_gdf['date'].max()}
    
    Filtered: {filtered_gdf['date'].min()}
             to {filtered_gdf['date'].max()}
    
    Days with data:
    Original: {original_gdf['date'].nunique()}
    Filtered: {filtered_gdf['date'].nunique()}
    """
    
    ax5.text(0.05, 0.5, stats_text, fontsize=10, family='monospace',
            verticalalignment='center', 
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.suptitle(f'Filter Analysis: {filter_title}', fontsize=14, fontweight='bold')
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved: {output_path}")
    
    plt.close()

def plot_density_map(original_gdf, filtered_gdf, filter_title, output_path=None):
    """Create geographic map comparison with OSM basemap (if available) using geopandas."""
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))
    
    # Prepare data
    if CONTEXTILY_AVAILABLE:
        try:
            orig_3857 = original_gdf.to_crs('EPSG:3857')
            filt_3857 = filtered_gdf.to_crs('EPSG:3857')
            add_basemap = True
        except Exception as e:
            print(f"✅ Error with basemap: {e}")
            orig_3857 = original_gdf
            filt_3857 = filtered_gdf
            add_basemap = False
    else:
        orig_3857 = original_gdf
        filt_3857 = filtered_gdf
        add_basemap = False
    
    # 1. Original data map with basemap
    ax = axes[0]
    if add_basemap:
        try:
            ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=10, alpha=0.5)
        except:
            pass
    orig_3857.plot(ax=ax, color='blue', markersize=8, alpha=0.5, edgecolor='darkblue', linewidth=0.2)
    ax.set_title(f'All Data: {filter_title}\n({len(orig_3857):,} points)', fontsize=12, fontweight='bold')
    
    # 2. Filtered data map with basemap
    ax = axes[1]
    if add_basemap:
        try:
            ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=10, alpha=0.5)
        except:
            pass
    orig_3857.plot(ax=ax, color='lightgray', markersize=3, alpha=0.15, edgecolor='none', label='Other data')
    
    if len(filt_3857) > 0:
        filt_3857.plot(ax=ax, color='red', markersize=10, alpha=0.7, edgecolor='darkred', 
                      linewidth=0.3, label=f'Filtered: {filter_title}')
    
    ax.set_title(f'Filtered Data: {filter_title}\n({len(filt_3857):,} points, {len(filt_3857)/len(orig_3857)*100:.1f}%)', 
                fontsize=12, fontweight='bold', color='darkred')
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    plt.suptitle(f'Geographic Distribution: {filter_title}', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Map saved: {output_path}")
    
    plt.close()

# ============================================================================
# EXAMPLE ANALYSES
# ============================================================================

def run_example_analyses():
    """Run multiple example analyses."""
    print("\n" + "="*70)
    print("INTERACTIVE FILTERING - EXAMPLE ANALYSES")
    print("="*70 + "\n")
    
    # Create output dir
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Load data
    print("Loading data...")
    user_a = load_and_prepare_data(GDB_PATH, 'mobile_data_user_a')
    user_b = load_and_prepare_data(GDB_PATH, 'mobile_data_user_b')
    print(f"✓ Loaded User A: {len(user_a)} points")
    print(f"✓ Loaded User B: {len(user_b)} points\n")
    
    # Examples for User A
    print("\n" + "-"*70)
    print("USER A - EXAMPLE FILTERS")
    print("-"*70)
    
    # Example 1: Summer months (red with data)
    print("\n1. Summer Analysis (June-August)...")
    summer_ua = filter_by_months(user_a, [6, 7, 8])
    summer_ua = calculate_metrics(summer_ua)
    stats = get_summary_stats(summer_ua, "User A Summer")
    print(f"   Points: {stats['Total Points']} ({stats['Total Points']/len(user_a)*100:.1f}% of year)")
    print(f"   Distance: {stats['Total Distance (km)']:.0f} km")
    plot_comparison(user_a, summer_ua, "User A - Summer (Jun-Aug)",
                   f"{OUTPUT_DIR}/user_a_summer.png")
    plot_density_map(user_a, summer_ua, "User A Summer",
                    f"{OUTPUT_DIR}/user_a_summer_density.png")
    
    # Example 2: Working hours (9-17)
    print("\n2. Working Hours Analysis (9:00-17:00)...")
    work_ua = filter_by_hours(user_a, list(range(9, 18)))
    work_ua = calculate_metrics(work_ua)
    stats = get_summary_stats(work_ua, "User A Working Hours")
    print(f"   Points: {stats['Total Points']} ({stats['Total Points']/len(user_a)*100:.1f}% of year)")
    plot_comparison(user_a, work_ua, "User A - Working Hours (9-17)",
                   f"{OUTPUT_DIR}/user_a_working_hours.png")
    plot_density_map(user_a, work_ua, "User A Working Hours",
                    f"{OUTPUT_DIR}/user_a_working_hours_density.png")
    
    # Example 3: Weekends
    print("\n3. Weekend Analysis (Saturdays & Sundays)...")
    weekend_ua = filter_by_weekdays(user_a, ['Saturday', 'Sunday'])
    weekend_ua = calculate_metrics(weekend_ua)
    stats = get_summary_stats(weekend_ua, "User A Weekends")
    print(f"   Points: {stats['Total Points']} ({stats['Total Points']/len(user_a)*100:.1f}% of year)")
    plot_comparison(user_a, weekend_ua, "User A - Weekends",
                   f"{OUTPUT_DIR}/user_a_weekends.png")
    plot_density_map(user_a, weekend_ua, "User A Weekends",
                    f"{OUTPUT_DIR}/user_a_weekends_density.png")
    
    # Example 4: Night hours
    print("\n4. Night Analysis (21:00-06:00)...")
    night_hours = list(range(21, 24)) + list(range(0, 7))
    night_ua = filter_by_hours(user_a, night_hours)
    night_ua = calculate_metrics(night_ua)
    stats = get_summary_stats(night_ua, "User A Night Hours")
    print(f"   Points: {stats['Total Points']} ({stats['Total Points']/len(user_a)*100:.1f}% of year)")
    plot_comparison(user_a, night_ua, "User A - Night (21-06)",
                   f"{OUTPUT_DIR}/user_a_night.png")
    plot_density_map(user_a, night_ua, "User A Night",
                    f"{OUTPUT_DIR}/user_a_night_density.png")
    
    # Examples for User B
    print("\n\n" + "-"*70)
    print("USER B - EXAMPLE FILTERS")
    print("-"*70)
    
    # Example 1: Summer
    print("\n1. Summer Analysis (June-August)...")
    summer_ub = filter_by_months(user_b, [6, 7, 8])
    summer_ub = calculate_metrics(summer_ub)
    stats = get_summary_stats(summer_ub, "User B Summer")
    print(f"   Points: {stats['Total Points']} ({stats['Total Points']/len(user_b)*100:.1f}% of year)")
    plot_comparison(user_b, summer_ub, "User B - Summer (Jun-Aug)",
                   f"{OUTPUT_DIR}/user_b_summer.png")
    plot_density_map(user_b, summer_ub, "User B Summer",
                    f"{OUTPUT_DIR}/user_b_summer_density.png")
    
    # Example 2: Working hours
    print("\n2. Working Hours Analysis (9:00-17:00)...")
    work_ub = filter_by_hours(user_b, list(range(9, 18)))
    work_ub = calculate_metrics(work_ub)
    stats = get_summary_stats(work_ub, "User B Working Hours")
    print(f"   Points: {stats['Total Points']} ({stats['Total Points']/len(user_b)*100:.1f}% of year)")
    plot_comparison(user_b, work_ub, "User B - Working Hours (9-17)",
                   f"{OUTPUT_DIR}/user_b_working_hours.png")
    plot_density_map(user_b, work_ub, "User B Working Hours",
                    f"{OUTPUT_DIR}/user_b_working_hours_density.png")
    
    # Example 3: Weekends
    print("\n3. Weekend Analysis (Saturdays & Sundays)...")
    weekend_ub = filter_by_weekdays(user_b, ['Saturday', 'Sunday'])
    weekend_ub = calculate_metrics(weekend_ub)
    stats = get_summary_stats(weekend_ub, "User B Weekends")
    print(f"   Points: {stats['Total Points']} ({stats['Total Points']/len(user_b)*100:.1f}% of year)")
    plot_comparison(user_b, weekend_ub, "User B - Weekends",
                   f"{OUTPUT_DIR}/user_b_weekends.png")
    plot_density_map(user_b, weekend_ub, "User B Weekends",
                    f"{OUTPUT_DIR}/user_b_weekends_density.png")
    
    # Example 4: Evening/Night (User B specific)
    print("\n4. Night Analysis (21:00-06:00) - User B more active here...")
    night_ub = filter_by_hours(user_b, night_hours)
    night_ub = calculate_metrics(night_ub)
    stats = get_summary_stats(night_ub, "User B Night Hours")
    print(f"   Points: {stats['Total Points']} ({stats['Total Points']/len(user_b)*100:.1f}% of year)")
    plot_comparison(user_b, night_ub, "User B - Night (21-06)",
                   f"{OUTPUT_DIR}/user_b_night.png")
    plot_density_map(user_b, night_ub, "User B Night",
                    f"{OUTPUT_DIR}/user_b_night_density.png")
    
    # Comparison: Weekdays only
    print("\n\n" + "-"*70)
    print("COMPARISON ANALYSES")
    print("-"*70)
    
    print("\n1. Weekday Comparison (Monday-Friday)...")
    weekday_ua = filter_by_weekdays(user_a, ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    weekday_ub = filter_by_weekdays(user_b, ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    print(f"   User A weekday points: {len(weekday_ua)}")
    print(f"   User B weekday points: {len(weekday_ub)}")
    
    print("\n✓ Analysis Complete!")
    print(f"Results saved to: {OUTPUT_DIR}/\n")
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY OF FILTERS")
    print("="*70)
    print(f"""
    User A:
    - Summer (Jun-Aug):     {len(summer_ua):>6} points ({len(summer_ua)/len(user_a)*100:>5.1f}%)
    - Work hours (9-17):    {len(work_ua):>6} points ({len(work_ua)/len(user_a)*100:>5.1f}%)
    - Weekends:             {len(weekend_ua):>6} points ({len(weekend_ua)/len(user_a)*100:>5.1f}%)
    - Night (21-06):        {len(night_ua):>6} points ({len(night_ua)/len(user_a)*100:>5.1f}%)
    
    User B:
    - Summer (Jun-Aug):     {len(summer_ub):>6} points ({len(summer_ub)/len(user_b)*100:>5.1f}%)
    - Work hours (9-17):    {len(work_ub):>6} points ({len(work_ub)/len(user_b)*100:>5.1f}%)
    - Weekends:             {len(weekend_ub):>6} points ({len(weekend_ub)/len(user_b)*100:>5.1f}%)
    - Night (21-06):        {len(night_ub):>6} points ({len(night_ub)/len(user_b)*100:>5.1f}%)
    """)

# ============================================================================
# CUSTOM FILTER TEMPLATE
# ============================================================================

def custom_filter_example():
    """Template for custom filters."""
    print("\n" + "="*70)
    print("CUSTOM FILTER TEMPLATE")
    print("="*70)
    print("""
    Use these functions to create your own filters:
    
    # Load data
    user_a = load_and_prepare_data(GDB_PATH, 'mobile_data_user_a')
    
    # Single filters
    winter = filter_by_months(user_a, [12, 1, 2])
    mornings = filter_by_hours(user_a, list(range(6, 12)))
    mondays = filter_by_weekdays(user_a, ['Monday'])
    
    # Combine filters
    winter_mornings = filter_by_months(winter, [12, 1, 2])
    winter_mornings = filter_by_hours(winter_mornings, list(range(6, 12)))
    
    # Date range
    from datetime import date
    specific_period = filter_by_date_range(user_a, date(2009, 1, 1), date(2009, 12, 31))
    
    # Calculate metrics
    winter_mornings = calculate_metrics(winter_mornings)
    
    # Get statistics
    stats = get_summary_stats(winter_mornings, "User A Winter Mornings")
    print(stats)
    """)

if __name__ == "__main__":
    run_example_analyses()
