import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np  # Add numpy import

# Read JSON data
with open('./fishing_vessel_routes.json', 'r') as f:
    data = json.load(f)

# Define the list of vessel IDs to display
target_vessel_ids = [
    'roachrobberdb6', 'snappersnatcher7be', 'yellowbullheadbuccaneer968',
    'whitemarlinmasterfa1', 'whitefishwrangler7df', 'whitefishwhisperer6df',
    'wavewranglerc2', 'wahoowrangler016', 'wahoowarriord42', 'turbottakerd86',
    'tunatrawlerafd', 'swordfishsaboteur22f', 'squidsquad7fd',
    'speckledtroutsaboteur509', 'soleseeker47a', 'snooksnatcherbdb',
    'skipjacktunatakerf85', 'seasirenf43', 'sardineseeker62e',
    'sailfishseeker8d5', 'redfishraider677', 'pompanoplunderere5d',
    'opheliacac', 'musselmaraudere9b', 'marlinmaster8ab',
    'mackerelmaster0a5', 'longfintunalooterf32', 'kingfisher87d',
    'huron1b3', 'halibuthunterd84', 'haddockhunter1a7',
    'europeanseabassbuccaneer777', 'eelenthusiast8c6', 'costasmeraldaac7',
    'cobiacapturere5e', 'catfishcapturer7a8', 'brownbullheadbriganded2',
    'brooktroutbuccaneerc0b', 'bluemarlinbandit292', 'bluegillbandita5f',
    'bluefintunabandit177', 'bigeyetunabanditb73', 'barracudabandit836',
    'baitedbreath538', 'arcticgraylingangler094', 'aquaticpursuitf31',
    'americaneelenthusiastcfa', 'albacoreangler47d'
]

# Define protected areas list (sorted alphabetically)
protected_areas = sorted(['Don Limpet Preserve', 'Ghoti Preserve', 'Nemo Reef'])

# Process all vessel data
all_processed_data = []
protected_processed_data = []
vessels_through_protected = set()

# Process all vessel data
for vessel in data['fishing_vessels']:
    vessel_id = vessel['vessel_id']
    if vessel_id not in target_vessel_ids:
        continue
        
    company = vessel['company']
    has_visited_protected = False
    
    for route_point in vessel['route']:
        # Extract time part (format: 2023-01-01T12:34:56.789307)
        time_parts = route_point['time'].split('T')[1].split('.')[0].split(':')
        hours = float(time_parts[0]) + float(time_parts[1])/60 + float(time_parts[2])/3600
        
        # Add to all vessel data
        all_processed_data.append({
            'vessel_id': vessel_id,
            'company': company,
            'location': route_point['location'],
            'time': hours,  # Use hours
            'dwell': route_point['dwell']
        })
        
        # Check if vessel has visited protected area
        if route_point['location'] in protected_areas:
            has_visited_protected = True
            vessels_through_protected.add(vessel_id)
            # Only add data related to protected area
            protected_processed_data.append({
                'vessel_id': vessel_id,
                'company': company,
                'location': route_point['location'],
                'time': hours,  # Use hours
                'dwell': route_point['dwell']
            })

# Convert to DataFrame
all_df = pd.DataFrame(all_processed_data)
protected_df = pd.DataFrame(protected_processed_data)

# Calculate average dwell time for each protected area
protected_avg_dwell = protected_df.groupby('location')['dwell'].mean().reset_index()
protected_avg_dwell_dict = dict(zip(protected_avg_dwell['location'], protected_avg_dwell['dwell']))

# Add average dwell time column to protected area data
protected_df['avg_dwell'] = protected_df['location'].map(protected_avg_dwell_dict)

# Create color mapping
def get_color_value(vessel_id, company, time=None, dwell=None, is_protected_view=False):
    if vessel_id == 'snappersnatcher7be':
        return 2  # Red
    elif is_protected_view and time is not None and dwell is not None:
        # In protected area view, set colors based on time, dwell time, etc.
        if (time < protected_df[protected_df['vessel_id'] == 'snappersnatcher7be']['time'].min() or 
            time >= 19) and (200000 <= dwell <= 400000):
            return 1  # Orange
    elif company == 'SouthSeafood Express Corp':
        return 1  # Orange
    return 0  # Light blue

# Apply color mapping
all_df['color_value'] = [get_color_value(row['vessel_id'], row['company']) for _, row in all_df.iterrows()]
protected_df['color_value'] = [get_color_value(row['vessel_id'], row['company'], row['time'], row['dwell'], True) for _, row in protected_df.iterrows()]

# Create color scale
color_scale = [
    [0, 'rgba(173, 216, 230, 1)'],  # Light blue with full opacity
    [0.5, 'rgba(255, 165, 0, 1)'],  # Orange with full opacity
    [1, 'rgba(255, 0, 0, 1)']       # Red with full opacity
]

# Create base figure
fig = go.Figure()

# Create location mapping for all vessels
all_locations = sorted(all_df['location'].unique())
all_location_codes = {loc: idx for idx, loc in enumerate(all_locations)}
all_df['location_code'] = all_df['location'].apply(lambda x: all_location_codes.get(x, -1))

# Create location mapping for protected area vessels
protected_location_codes = {loc: idx for idx, loc in enumerate(protected_areas)}
protected_df['location_code'] = protected_df['location'].apply(lambda x: protected_location_codes.get(x, -1))

# Create vessel ID mapping
protected_vessel_ids = sorted(protected_df['vessel_id'].unique())
protected_vessel_codes = {vessel: idx for idx, vessel in enumerate(protected_vessel_ids)}
protected_df['vessel_code'] = protected_df['vessel_id'].apply(lambda x: protected_vessel_codes.get(x, -1))

# Generate time ticks and labels (every 5 minutes)
time_ticks = [i/12 for i in range(0, 24*12 + 1)]  # Every 5 minutes
time_labels = []
for t in time_ticks:
    hours = int(t)
    minutes = int((t - hours) * 60)
    time_labels.append(f"{hours:02d}:{minutes:02d}:00")

# Add parallel coordinates for all vessels
fig.add_trace(
    go.Parcoords(
        visible=True,
        line=dict(
            color=all_df['color_value'],
            colorscale=color_scale,
            showscale=False
        ),
        unselected=dict(
            line=dict(
                color='rgba(0,0,0,0)',  # 完全透明
                opacity=0  # 确保完全隐藏
            )
        ),
        dimensions=list([
            dict(range=[0, 24],
                 label='Time',
                 values=all_df['time'],
                 ticktext=time_labels[::12],
                 tickvals=time_ticks[::12]),
            dict(range=[0, len(all_locations)-1],
                 label='Location',
                 values=all_df['location_code'],
                 ticktext=all_locations,
                 tickvals=list(range(len(all_locations)))),
            dict(range=[0, len(all_df['vessel_id'].unique())-1],
                 label='Vessel ID',
                 values=pd.Categorical(all_df['vessel_id']).codes,
                 ticktext=sorted(all_df['vessel_id'].unique()),
                 tickvals=list(range(len(all_df['vessel_id'].unique())))),
            dict(range=[all_df['dwell'].min(), all_df['dwell'].max()],
                 label='Dwell Time',
                 values=all_df['dwell'])
        ])
    )
)

# Add parallel coordinates for protected area vessels
fig.add_trace(
    go.Parcoords(
        visible=False,
        line=dict(
            color=protected_df['color_value'],
            colorscale=color_scale,
            showscale=False
        ),
        unselected=dict(
            line=dict(
                color='rgba(0,0,0,0)',  # 完全透明
                opacity=0  # 确保完全隐藏
            )
        ),
        dimensions=list([
            dict(range=[0, 24],
                 label='Time',
                 values=protected_df['time'],
                 ticktext=time_labels[::12],
                 tickvals=time_ticks[::12]),
            dict(range=[0, len(protected_areas)-1],
                 label='Location',
                 values=protected_df['location_code'],
                 ticktext=protected_areas,
                 tickvals=list(range(len(protected_areas)))),
            dict(range=[0, len(protected_vessel_ids)-1],
                 label='Vessel ID',
                 values=protected_df['vessel_code'],
                 ticktext=protected_vessel_ids,
                 tickvals=list(range(len(protected_vessel_ids)))),
            dict(range=[protected_df['dwell'].min(), protected_df['dwell'].max()],
                 label='Dwell Time in Protected Areas',
                 values=protected_df['dwell']),
            dict(range=[protected_df['dwell'].min(), protected_df['dwell'].max()],  # Use same range as Dwell Time
                 label='Average Dwell Time by Area',
                 values=protected_df['avg_dwell'])
        ])
    )
)

# Add buttons
fig.update_layout(
    title='Vessel Route Parallel Coordinates',
    title_x=0.5,
    height=800,
    width=1500,
    showlegend=True,
    margin=dict(
        l=180,
        r=150,
        t=100,
        b=50
    ),
    updatemenus=[
        dict(
            type="buttons",
            direction="right",
            active=0,
            x=0.57,
            y=1.2,
            buttons=list([
                dict(label="All Vessels",
                     method="update",
                     args=[{"visible": [True, False]},
                           {"title": "All Vessel Routes Parallel Coordinates"}]),
                dict(label="Protected Area Activity",
                     method="update",
                     args=[{"visible": [False, True]},
                           {"title": "Vessel Protected Area Activity Parallel Coordinates"}])
            ]),
        )
    ]
)

# Add instruction text
# fig.add_annotation(
#     text="Tip: Click and drag on the Location axis to filter vessels in specific areas<br>Average Dwell Time shows the average dwell time for each protected area",
#     xref="paper", yref="paper",
#     x=0.5, y=1.1,
#     showarrow=False,
#     font=dict(size=12)
# )

# Save the chart
fig.write_html('vessel_parallel_coordinates.html')