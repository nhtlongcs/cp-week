import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style for better aesthetics
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def to_time_str(minutes):
    """Convert minutes since midnight to HH:MM format"""
    h = minutes // 60
    m = minutes % 60
    m = int(m)
    h = int(h)
    return f"{h:02d}:{m:02d}"

def filter_trips_data(trips, destination=None, time_range=None):
    """Filter trips data by destination and/or time range"""
    df = pd.DataFrame(trips)
    
    # Filter by destination if specified
    if destination:
        df = df[df['destination'] == destination]
        if df.empty:
            print(f"No trips found for destination: {destination}")
            return None
    
    # Filter by time range if specified
    if time_range:
        start_hour, end_hour = time_range
        start_minutes = start_hour * 60
        end_minutes = end_hour * 60
        
        # Filter trips that start within the time range
        df = df[(df['departure'] >= start_minutes) & (df['departure'] < end_minutes)]
        if df.empty:
            print(f"No trips found in time range {start_hour:02d}:00-{end_hour:02d}:00")
            return None
    
    return df

def get_color_map(destinations):
    """Create a consistent color mapping for destinations"""
    colors = plt.cm.Set3(np.linspace(0, 1, len(destinations)))
    return dict(zip(destinations, colors))

def setup_time_axis(ax, df, padding_minutes=15, tick_interval=30):
    """Setup time axis with consistent formatting and tight bounds"""
    # Calculate actual min and max times from the data (tight bounds)
    all_departure_times = list(df["departure"])
    all_return_times = [trip["arrival"] + trip["drivingTime"] if "drivingTime" in df.columns 
                       else trip["arrival"] for _, trip in df.iterrows()]
    
    actual_min_time = min(all_departure_times)
    actual_max_time = max(all_return_times)
    
    # Add padding
    start_time = actual_min_time - padding_minutes
    end_time = actual_max_time + padding_minutes
    
    # Create ticks at specified interval within the actual range
    xticks = range(int(start_time), int(end_time) + tick_interval, tick_interval)
    ax.set_xticks(xticks)
    ax.set_xticklabels([to_time_str(x) for x in xticks])
    
    # Set tight x-axis limits
    ax.set_xlim(start_time, end_time)
    
    return start_time, end_time

def create_filtered_timeline(trips, destination=None, time_range=None):
    """Create a timeline view filtered by destination and/or time range"""
    df = filter_trips_data(trips, destination, time_range)
    if df is None:
        return None
    
    # Filter by destination if specified
    if destination:
        df = df[df['destination'] == destination]
        if df.empty:
            print(f"No trips found for destination: {destination}")
            return None
    
    # Filter by time range if specified
    if time_range:
        start_hour, end_hour = time_range
        start_minutes = start_hour * 60
        end_minutes = end_hour * 60
        
        # Filter trips that start within the time range
        df = df[(df['departure'] >= start_minutes) & (df['departure'] < end_minutes)]
        if df.empty:
            print(f"No trips found in time range {start_hour:02d}:00-{end_hour:02d}:00")
            return None
    
    
    # Filter by destination if specified
    if destination:
        df = df[df['destination'] == destination]
        if df.empty:
            print(f"No trips found for destination: {destination}")
            return None
    
    # Filter by time range if specified
    if time_range:
        start_hour, end_hour = time_range
        start_minutes = start_hour * 60
        end_minutes = end_hour * 60
        
        # Filter trips that start within the time range
        df = df[(df['departure'] >= start_minutes) & (df['departure'] < end_minutes)]
        if df.empty:
            print(f"No trips found in time range {start_hour:02d}:00-{end_hour:02d}:00")
            return None

    # Create single timeline plot
    fig, ax1 = plt.subplots(1, 1, figsize=(16, 8))
    
    # Timeline view with journey segments
    destinations = df["destination"].unique()
    color_map = get_color_map(destinations)
    
    y_positions = {}
    current_y = 0
    
    # Group by destination for cleaner visualization
    for dest in destinations:
        dest_trips = df[df["destination"] == dest].sort_values('departure')
        y_positions[dest] = current_y
        
        for _, trip in dest_trips.iterrows():
            # ret_dep, ret_arr = calculate_return_time(trip)
            
            # Journey segments
            start_time = trip["departure"]
            end_time = trip["arrival"] 
            # return_time = ret_arr
            
            # Draw the complete journey as connected segments
            # Segment 1: Departure to destination (outbound)
            outbound_duration = (end_time - start_time) / 2
            ax1.barh(current_y, outbound_duration, left=start_time, 
                    height=0.4, color=color_map[dest], alpha=0.8,
                    edgecolor='white', linewidth=2, label=f'{dest.title()}' if trip['nr'] == dest_trips['nr'].iloc[0] else "")
            
            # Segment 2: Return journey (gray)
            inbound_duration = (end_time - start_time) / 2
            ax1.barh(current_y, inbound_duration, left=start_time + outbound_duration, 
                    height=0.4, color='lightgray', alpha=0.7,
                    edgecolor='white', linewidth=2, label='Return Journey' if current_y == 0 else "")
            
            # Add connecting line to show it's the same trip
            ax1.plot([start_time, end_time], [current_y, current_y], 
                    color='black', alpha=0.3, linewidth=1, linestyle=':')
            
            # Trip annotations
            ax1.text(start_time + outbound_duration / 2, current_y, f"#{trip['nr']}", 
                    ha='center', va='center', fontweight='bold', 
                    fontsize=8, color='white')

            ax1.text(start_time + outbound_duration + inbound_duration / 2, current_y, f"#{trip['nr']}↩", 
                    ha='center', va='center', fontweight='bold', 
                    fontsize=8, color='black')
            
            # Time markers
            total_journey_time = end_time - start_time
            ax1.annotate(f"{to_time_str(start_time)}", 
                        xy=(start_time, current_y), xytext=(-10, 20),
                        textcoords='offset points', ha='right', va='bottom',
                        fontsize=8, alpha=0.7,
                        arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5))
            
            ax1.annotate(f"{to_time_str(start_time + outbound_duration)}", 
                        xy=(start_time + outbound_duration, current_y), xytext=(0, 25),
                        textcoords='offset points', ha='center', va='bottom',
                        fontsize=8, alpha=0.7,
                        arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5))
            
            ax1.annotate(f"{to_time_str(end_time)}\n({to_time_str(total_journey_time)}m)", 
                        xy=(end_time, current_y), xytext=(10, 0),
                        textcoords='offset points', ha='left', va='bottom',
                        fontsize=8, alpha=0.7)
            
            current_y += 1
    
    # Customize timeline
    ax1.set_yticks(list(y_positions.values()))
    ax1.set_yticklabels([dest.title() for dest in y_positions.keys()])
    
    # Dynamic title based on filters
    title = "Complete Journey Timeline"
    if destination:
        title += f" - {destination.title()} Routes"
    if time_range:
        title += f" - {time_range[0]:02d}:00 to {time_range[1]:02d}:00"
    title += " - Start → Destination → Return to Source"
    
    ax1.set_title(title, fontsize=16, fontweight='bold')
    ax1.set_xlabel("Time of Day", fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')
    ax1.legend(loc='upper right', framealpha=0.9)
    
    # Setup time axis with consistent formatting
    setup_time_axis(ax1, df)
    
    
    return fig

def create_interval_partitioning_visualization(trips, destination=None, time_range=None):
    """Create interval partitioning visualization showing maximum overlaps and minimum trains needed"""
    df = filter_trips_data(trips, destination, time_range)
    if df is None:
        return None
    
    # Create intervals for each trip (complete round trip)
    intervals = []
    for _, trip in df.iterrows():
        intervals.append({
            'start': trip['departure'],
            'end': trip["arrival"],
            'trip_nr': trip['nr'],
            'destination': trip['destination']
        })
    
    # Calculate overlap counts at each time point
    all_times = set()
    for interval in intervals:
        all_times.add(interval['start'])
        all_times.add(interval['end'])
    
    all_times = sorted(all_times)
    overlap_counts = []
    
    for time_point in all_times:
        count = 0
        for interval in intervals:
            if interval['start'] <= time_point < interval['end']:
                count += 1
        overlap_counts.append(count)
    
    # Find maximum overlap and corresponding time
    max_overlap = max(overlap_counts)
    max_overlap_time = all_times[overlap_counts.index(max_overlap)]
    
    # Create figure with two subplots
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1], hspace=0.3)
    
    # Main timeline plot
    ax_main = fig.add_subplot(gs[0])
    
    
    # Color scheme
    destinations = df['destination'].unique()
    color_map = get_color_map(destinations)
    
    # Draw intervals
    for i, interval in enumerate(intervals):
        duration = interval['end'] - interval['start']
        color = color_map[interval['destination']]
        
        # Draw the interval bar
        bar = ax_main.barh(i, duration, left=interval['start'], 
                          height=0.6, color=color, alpha=0.7,
                          edgecolor='white', linewidth=2)
        
        # Add trip number label
        ax_main.text(interval['start'] + duration/2, i, 
                    f"#{interval['trip_nr']}", 
                    ha='center', va='center', fontweight='bold', 
                    fontsize=9, color='white')
    
    # Highlight maximum overlap region
    overlap_intervals = []
    for interval in intervals:
        if interval['start'] <= max_overlap_time < interval['end']:
            overlap_intervals.append(interval)
    
    # Add vertical line at maximum overlap time
    ax_main.axvline(max_overlap_time, color='red', linestyle='--', linewidth=3, alpha=0.8)
    ax_main.text(max_overlap_time, len(intervals) * 0.9, 
                f'Max Overlap\n{max_overlap} trains\nat {to_time_str(max_overlap_time)}',
                ha='center', va='center', fontweight='bold', fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="red", alpha=0.8, edgecolor="white"),
                color='white')
    
    # Customize main plot
    ax_main.set_yticks(range(len(intervals)))
    ax_main.set_yticklabels([f"Trip #{interval['trip_nr']} ({interval['destination'].title()})" 
                            for interval in intervals])
    
    # X-axis formatting
    start_time, end_time = setup_time_axis(ax_main, df, padding_minutes=30, tick_interval=60)
    
    title = "🚂 Interval Partitioning Analysis"
    if destination:
        title += f" - {destination.title()}"
    if time_range:
        title += f" ({time_range[0]:02d}:00-{time_range[1]:02d}:00)"
    
    ax_main.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax_main.set_xlabel("Time of Day", fontsize=12, fontweight='bold')
    ax_main.set_ylabel("Train Trips (Round Trip Intervals)", fontsize=12, fontweight='bold')
    ax_main.grid(True, alpha=0.3, axis='x')
    
    # Add legend
    legend_elements = []
    for dest in destinations:
        legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=color_map[dest], alpha=0.7, label=dest.title()))
    ax_main.legend(handles=legend_elements, loc='upper right')
    
    # Overlap count plot
    ax_overlap = fig.add_subplot(gs[1])
    
    # Create time series for overlap visualization
    time_series = []
    overlap_series = []
    
    for i in range(len(all_times) - 1):
        start_t = all_times[i]
        end_t = all_times[i + 1]
        overlap_count = overlap_counts[i]
        
        time_series.extend([start_t, end_t])
        overlap_series.extend([overlap_count, overlap_count])
    
    # Color the bars based on overlap count
    colors_overlap = plt.cm.YlOrRd(np.array(overlap_series) / max_overlap)
    
    # Plot as step function
    ax_overlap.step(time_series, overlap_series, where='post', linewidth=3, alpha=0.8)
    ax_overlap.fill_between(time_series, overlap_series, step='post', alpha=0.3, color='orange')
    
    # Highlight maximum overlap
    max_overlap_mask = np.array(overlap_series) == max_overlap
    if any(max_overlap_mask):
        max_times = np.array(time_series)[max_overlap_mask]
        max_overlaps = np.array(overlap_series)[max_overlap_mask]
        ax_overlap.scatter(max_times, max_overlaps, color='red', s=100, zorder=5, alpha=0.8)
    
    ax_overlap.axhline(max_overlap, color='red', linestyle=':', alpha=0.7)
    ax_overlap.text(0.02, 0.98, f'Minimum Trains Needed: {max_overlap}', 
                   transform=ax_overlap.transAxes, fontsize=14, fontweight='bold',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8),
                   verticalalignment='top')
    
    ax_overlap.set_xlim(start_time, end_time)
    xticks = range(int(start_time), int(end_time), 60)
    ax_overlap.set_xticks(xticks)
    ax_overlap.set_xticklabels([to_time_str(x) for x in xticks])
    ax_overlap.set_title("Number of Overlapping Train Intervals Over Time", fontsize=14, fontweight='bold')
    ax_overlap.set_xlabel("Time of Day", fontsize=12, fontweight='bold')
    ax_overlap.set_ylabel("Number of Active Trains", fontsize=12, fontweight='bold')
    ax_overlap.grid(True, alpha=0.3)
    
    # Add statistics text
    stats_text = f"""
INTERVAL PARTITIONING ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Intervals (Round Trips): {len(intervals)}
Minimum Trains Needed: {max_overlap}
Maximum Overlap occurs at: {to_time_str(max_overlap_time)}
Efficiency: {len(intervals)/max_overlap:.1f} trips per train on average
    """
    
    plt.figtext(0.02, 0.02, stats_text, fontsize=11, fontfamily='monospace',
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
    
    plt.suptitle("Train Interval Partitioning - Minimum Fleet Size Analysis", 
                fontsize=18, fontweight='bold')
    
    
    return fig

def save_and_close_figure(fig, filename, saved_files=None):
    """Save figure to file and close it, optionally tracking saved files"""
    if fig:
        fig.savefig(filename, dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        if saved_files is not None:
            saved_files.append(filename)
        plt.show()
        plt.close()
        return True
    return False

# Generate timeline images only
if __name__ == "__main__":
    import json 
    with open("data/monfri.json", "r") as f:
        timetable = json.load(f)
    
    trips = timetable["trips"][:]
    df = pd.DataFrame(trips)
    destinations = df['destination'].unique()
    
    print("=" * 80)
    print("🚂 TRAIN TIMELINE VISUALIZATION GENERATOR")
    print("=" * 80)
    print(f"Total trips: {len(trips)}")
    print(f"Destinations: {', '.join([dest.title() for dest in destinations])}")
    print()
    
    saved_files = []
    
    # Define visualization configurations
    visualizations = [
        # (description, function, args, filename_template)
        ("Creating interval partitioning analysis...", 
         create_interval_partitioning_visualization, 
         {"trips": trips}, 
         "train_interval_partitioning.png"),
        
        ("Creating overall timeline overview...", 
         create_filtered_timeline, 
         {"trips": trips}, 
         "train_timeline_overview.png"),
    ]
    
    # Time range configurations
    time_ranges = [(0, 12), (12, 24)]
    for start_hour, end_hour in time_ranges:
        visualizations.append((
            f"Creating timeline for {start_hour:02d}:00-{end_hour:02d}:00...",
            create_filtered_timeline,
            {"trips": trips, "time_range": (start_hour, end_hour)},
            f"train_timeline_{start_hour:02d}h-{end_hour:02d}h.png"
        ))
    
    # Destination-specific configurations
    for destination in destinations:
        visualizations.extend([
            (f"Creating timeline for {destination.title()}...",
             create_filtered_timeline,
             {"trips": trips, "destination": destination},
             f"train_timeline_{destination}.png"),
            
            (f"Creating interval partitioning analysis for {destination.title()}...",
             create_interval_partitioning_visualization,
             {"trips": trips, "destination": destination},
             f"train_interval_partitioning_{destination}.png"),
        ])
    
    # Destination + time range combinations
    for destination in destinations:
        for start_hour, end_hour in time_ranges:
            visualizations.append((
                f"Creating timeline for {destination.title()} ({start_hour:02d}:00-{end_hour:02d}:00)...",
                create_filtered_timeline,
                {"trips": trips, "destination": destination, "time_range": (start_hour, end_hour)},
                f"train_timeline_{destination}_{start_hour:02d}h-{end_hour:02d}h.png"
            ))
    
    # Generate all visualizations
    for description, func, kwargs, filename in visualizations:
        print(description)
        fig = func(**kwargs)
        save_and_close_figure(fig, filename, saved_files)
    
    print("\n✅ Timeline visualization system completed!")
    print("📁 Files generated:")
    for i, filename in enumerate(saved_files, 1):
        print(f"   {i:2d}. {filename}")
    
    print(f"\n📈 Summary:")
    print(f"   • 1 overall timeline")
    print(f"   • 1 overall interval partitioning analysis")
    print(f"   • {len(time_ranges)} time-range specific timelines") 
    print(f"   • {len(destinations)} destination-specific timelines")
    print(f"   • {len(destinations)} destination-specific interval partitioning analyses")
    print(f"   • {len(destinations) * len(time_ranges)} destination+time combinations")
    print(f"   • Total images: {len(saved_files)}")