import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
from datetime import datetime
import os

def get_fishing_vessel_ids(data):
    # Convert nodes data to DataFrame
    nodes_df = pd.DataFrame(data['nodes'])
    
    # Filter fishing vessels
    fishing_vessels = nodes_df[nodes_df['type'] == 'Entity.Vessel.FishingVessel']
    
    # Get unique vessel IDs
    vessel_ids = sorted(fishing_vessels['id'].unique())
    
    print(f"Found {len(vessel_ids)} fishing vessels:")
    for vessel_id in vessel_ids:
        print(f"- {vessel_id}")
    
    return vessel_ids

def get_location_color(location):
    # Define colors for specific locations
    special_locations = {
        'Nemo Reef': '#FFA500',  # Orange
        'Ghoti Preserve': '#FFA500',  # Orange
        'Don Limpet Preserve': '#FFA500'  # Orange
    }
    return special_locations.get(location, 'steelblue')

def analyze_vessel_dwell_time(data, target_vessel, output_dir):
    # Convert edge data to DataFrame
    edges_df = pd.DataFrame(data['links'])
    
    # Filter TransponderPing type edges
    pings_df = edges_df[edges_df['type'] == 'Event.TransportEvent.TransponderPing'].copy()
    
    # Filter target vessel data
    vessel_data = pings_df[pings_df['target'] == target_vessel].copy()
    
    # If no data found for this vessel, skip
    if len(vessel_data) == 0:
        print(f"No transponder data found for vessel {target_vessel}")
        return
    
    # Convert time strings to datetime objects
    vessel_data['datetime'] = pd.to_datetime(vessel_data['time'], format='ISO8601')
    
    # Create figure
    plt.figure(figsize=(15, 8))
    plt.gca().set_facecolor('#f8f8f8')
    
    # Get all unique locations
    locations = sorted(vessel_data['source'].unique())
    
    # Create timeline for each location
    for idx, location in enumerate(locations):
        # Get data for this location
        location_data = vessel_data[vessel_data['source'] == location]
        
        # Draw dwell time lines
        for _, row in location_data.iterrows():
            dwell_time = float(row['dwell'])  # Ensure dwell is numeric
            if dwell_time > 0:  # Only draw records with dwell time
                # Draw vertical lines to represent dwell time
                plt.vlines(x=row['datetime'], ymin=idx-0.3, ymax=idx+0.3,
                         color=get_location_color(location), alpha=0.6, linewidth=2)
    
    # Add red vertical line for May 14, 2035
    target_date = pd.to_datetime('2035-05-14')
    plt.axvline(x=target_date, color='red', alpha=0.8, linewidth=3)
    
    # Set y-axis ticks and labels
    plt.yticks(range(len(locations)), locations)
    
    # Set x-axis format
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.xticks(rotation=45)
    
    # Set title and labels
    plt.title(f'Vessel Dwell Time Distribution ({target_vessel})', pad=20, fontsize=14)
    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Location', fontsize=12)
    
    # Add grid lines
    plt.grid(True, axis='x', linestyle='--', alpha=0.2)
    plt.margins(x=0.01)
    
    # Add horizontal separators
    for y in range(len(locations)-1):
        plt.axhline(y=y+0.5, color='gray', linestyle='-', alpha=0.1)
    
    # Remove top and right borders
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_alpha(0.2)
    plt.gca().spines['bottom'].set_alpha(0.2)
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(os.path.join(output_dir, f'vessel_{target_vessel}_dwell_time.png'),
                bbox_inches='tight',
                dpi=300,
                facecolor='#f8f8f8')
    print(f"Generated dwell time plot for vessel {target_vessel}")
    plt.close()

def create_summary_plot(data, vessel_ids, output_dir):
    # Convert edge data to DataFrame
    edges_df = pd.DataFrame(data['links'])
    
    # Filter TransponderPing type edges
    pings_df = edges_df[edges_df['type'] == 'Event.TransportEvent.TransponderPing'].copy()
    
    # Create figure
    plt.figure(figsize=(20, 15))
    plt.gca().set_facecolor('#f8f8f8')
    
    # Calculate grid dimensions
    n_vessels = len(vessel_ids)
    n_cols = 2  # 2 columns
    n_rows = (n_vessels + 1) // 2  # Round up division
    
    # Create subplots
    for idx, vessel_id in enumerate(vessel_ids, 1):
        plt.subplot(n_rows, n_cols, idx)
        
        # Filter vessel data
        vessel_data = pings_df[pings_df['target'] == vessel_id].copy()
        if len(vessel_data) == 0:
            continue
        
        # Convert time strings to datetime objects
        vessel_data['datetime'] = pd.to_datetime(vessel_data['time'], format='ISO8601')
        
        # Get all unique locations
        locations = sorted(vessel_data['source'].unique())
        
        # Create timeline for each location
        for loc_idx, location in enumerate(locations):
            location_data = vessel_data[vessel_data['source'] == location]
            for _, row in location_data.iterrows():
                dwell_time = float(row['dwell'])
                if dwell_time > 0:
                    plt.vlines(x=row['datetime'], ymin=loc_idx-0.3, ymax=loc_idx+0.3,
                             color=get_location_color(location), alpha=0.6, linewidth=2)
        
        # Add May 12, 2035 line
        target_date = pd.to_datetime('2035-05-12')
        plt.axvline(x=target_date, color='red', alpha=0.8, linewidth=3)
        
        # Customize subplot
        plt.yticks(range(len(locations)), locations, fontsize=8)
        plt.xticks(rotation=45, fontsize=8)
        plt.title(f'Vessel {vessel_id}', pad=10, fontsize=10)
        
        # Add grid
        plt.grid(True, axis='x', linestyle='--', alpha=0.2)
        
        # Remove borders
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['left'].set_alpha(0.2)
        plt.gca().spines['bottom'].set_alpha(0.2)
    
    plt.suptitle('Summary of All Vessels Dwell Time Distribution', fontsize=16, y=0.95)
    plt.tight_layout()
    
    # Save summary plot
    plt.savefig(os.path.join(output_dir, 'all_vessels_summary.png'),
                bbox_inches='tight',
                dpi=300,
                facecolor='#f8f8f8')
    print("\nGenerated summary plot for all vessels")
    plt.close()

def analyze_all_fishing_vessels(file_path):
    # Read JSON file
    print("Reading data...")
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Get all fishing vessel IDs
    vessel_ids = get_fishing_vessel_ids(data)
    
    # Create output directory
    output_dir = 'fishing_vessel_plots'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"\nCreated output directory: {output_dir}")
    
    # Generate individual plots for each vessel
    print("\nGenerating dwell time plots for each vessel...")
    for vessel_id in vessel_ids:
        analyze_vessel_dwell_time(data, vessel_id, output_dir)
    
    # Generate summary plot
    # create_summary_plot(data, vessel_ids, output_dir)

if __name__ == "__main__":
    try:
        analyze_all_fishing_vessels("MC2/mc2.json")
        print("\nAll plots have been generated successfully")
    except FileNotFoundError:
        print("Error: Could not find data file 'MC2/mc2.json'")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc() 