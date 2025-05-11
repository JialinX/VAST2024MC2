import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter, defaultdict
from itertools import combinations

# Read JSON data
with open('./fishing_vessel_routes.json', 'r') as f:
    data = json.load(f)

# Define protected areas
protected_areas = ['Don Limpet Preserve', 'Ghoti Preserve', 'Nemo Reef']

# Get all possible locations
all_locations = set()
for vessel in data['fishing_vessels']:
    for point in vessel['route']:
        all_locations.add(point['location'])
all_locations = sorted(list(all_locations))

# Create location index mapping
location_to_idx = {loc: idx for idx, loc in enumerate(all_locations)}

def get_location_sequence_features(route):
    """Calculate location sequence features"""
    # Initialize features
    features = {
        'sequence': [],  # Location sequence
        'protected_visits': [],  # Protected area visit sequence
        'before_protected': defaultdict(list),  # Sequence before protected areas
        'after_protected': defaultdict(list),  # Sequence after protected areas
        'protected_transitions': defaultdict(int)  # Transitions between protected areas
    }
    
    # Record location sequence
    for point in route:
        location = point['location']
        features['sequence'].append(location)
        if location in protected_areas:
            features['protected_visits'].append(location)
    
    # Analyze sequences before and after protected areas
    for i, location in enumerate(features['sequence']):
        if location in protected_areas:
            # Record two locations before protected area
            if i >= 2:
                prev_locs = features['sequence'][i-2:i]
                if not any(loc in protected_areas for loc in prev_locs):
                    features['before_protected'][location].extend(prev_locs)
            
            # Record two locations after protected area
            if i < len(features['sequence'])-2:
                next_locs = features['sequence'][i+1:i+3]
                if not any(loc in protected_areas for loc in next_locs):
                    features['after_protected'][location].extend(next_locs)
    
    # Analyze transitions between protected areas
    for i in range(len(features['protected_visits'])-1):
        from_area = features['protected_visits'][i]
        to_area = features['protected_visits'][i+1]
        features['protected_transitions'][(from_area, to_area)] += 1
    
    return features

def calculate_sequence_similarity(seq1, seq2):
    """Calculate similarity between two sequences"""
    # Use longest common subsequence algorithm
    m, n = len(seq1), len(seq2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if seq1[i-1] == seq2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    lcs_length = dp[m][n]
    return lcs_length / max(m, n) if max(m, n) > 0 else 0

def calculate_protected_similarity(features1, features2):
    """Calculate similarity of protected area visit patterns"""
    similarity = 0
    
    # Protected area visit sequence similarity
    seq_similarity = calculate_sequence_similarity(
        features1['protected_visits'],
        features2['protected_visits']
    )
    similarity += seq_similarity * 0.3
    
    # Similarity of sequences before and after protected areas
    for area in protected_areas:
        # Similarity of sequences before protected area
        before1 = features1['before_protected'][area]
        before2 = features2['before_protected'][area]
        if before1 and before2:
            before_similarity = calculate_sequence_similarity(before1, before2)
            similarity += before_similarity * 0.2
        
        # Similarity of sequences after protected area
        after1 = features1['after_protected'][area]
        after2 = features2['after_protected'][area]
        if after1 and after2:
            after_similarity = calculate_sequence_similarity(after1, after2)
            similarity += after_similarity * 0.2
    
    # Similarity of transitions between protected areas
    transitions1 = set(features1['protected_transitions'].keys())
    transitions2 = set(features2['protected_transitions'].keys())
    transition_similarity = len(transitions1 & transitions2) / max(len(transitions1 | transitions2), 1)
    similarity += transition_similarity * 0.3
    
    return similarity

# Process data
vessel_features = []
sequence_features = {}

for vessel in data['fishing_vessels']:
    vessel_id = vessel['vessel_id']
    company = vessel['company']
    
    # Extract basic features
    locations = set()
    dwell_times = []
    times = []
    
    for point in vessel['route']:
        locations.add(point['location'])
        dwell_times.append(point['dwell'])
        time_parts = point['time'].split('T')[1].split('.')[0].split(':')
        hours = float(time_parts[0]) + float(time_parts[1])/60 + float(time_parts[2])/3600
        times.append(hours)
    
    # Calculate statistical features
    avg_dwell = np.mean(dwell_times) if dwell_times else 0
    std_dwell = np.std(dwell_times) if dwell_times else 0
    max_dwell = max(dwell_times) if dwell_times else 0
    min_dwell = min(dwell_times) if dwell_times else 0
    
    avg_time = np.mean(times) if times else 0
    std_time = np.std(times) if times else 0
    
    # Calculate location sequence features
    sequence_features[vessel_id] = get_location_sequence_features(vessel['route'])
    
    vessel_features.append({
        'vessel_id': vessel_id,
        'company': company,
        'num_locations': len(locations),
        'avg_dwell': avg_dwell,
        'std_dwell': std_dwell,
        'max_dwell': max_dwell,
        'min_dwell': min_dwell,
        'avg_time': avg_time,
        'std_time': std_time
    })

# Convert to DataFrame
df = pd.DataFrame(vessel_features)

# Select numeric features for similarity calculation
numeric_features = ['num_locations', 'avg_dwell', 'std_dwell', 'max_dwell', 'min_dwell', 'avg_time', 'std_time']
X = df[numeric_features]

# Standardize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Calculate basic feature similarity
basic_similarity_matrix = cosine_similarity(X_scaled)

# Calculate sequence feature similarity
sequence_similarity_matrix = np.zeros((len(df), len(df)))
for i, vessel1 in enumerate(df['vessel_id']):
    for j, vessel2 in enumerate(df['vessel_id']):
        if i <= j:
            similarity = calculate_protected_similarity(
                sequence_features[vessel1],
                sequence_features[vessel2]
            )
            sequence_similarity_matrix[i, j] = similarity
            sequence_similarity_matrix[j, i] = similarity

# Combine both similarities
combined_similarity_matrix = 0.5 * basic_similarity_matrix + 0.5 * sequence_similarity_matrix

# Get target vessel similarity
target_vessel = 'snappersnatcher7be'
target_idx = df[df['vessel_id'] == target_vessel].index[0]
similarities = combined_similarity_matrix[target_idx]

# Create similarity DataFrame
similarity_df = pd.DataFrame({
    'vessel_id': df['vessel_id'],
    'company': df['company'],
    'similarity': similarities,
    'basic_similarity': basic_similarity_matrix[target_idx],
    'sequence_similarity': sequence_similarity_matrix[target_idx]
})

# Sort by similarity
similarity_df = similarity_df.sort_values('similarity', ascending=False)

# Create HTML content
html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Vessel Similarity Analysis</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        .container {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .chart-container {{
            width: 100%;
            height: 600px;
        }}
        .table-container {{
            width: 100%;
            overflow-x: auto;
            margin-top: 110px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .target-vessel {{
            background-color: #ffcccc;
        }}
        .similarity-details {{
            font-size: 0.9em;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Similarity Analysis with Vessel {target_vessel}</h1>
        
        <div class="chart-container">
            {go.Figure(
                data=[go.Bar(
                    x=similarity_df['vessel_id'],
                    y=similarity_df['similarity'],
                    text=similarity_df['company'],
                    textposition='auto',
                    marker_color=['red' if vessel == target_vessel else 'blue' for vessel in similarity_df['vessel_id']],
                    textfont=dict(size=10),
                    hovertemplate='<b>Vessel ID:</b> %{x}<br><b>Company:</b> %{text}<br><b>Similarity:</b> %{y:.3f}<extra></extra>'
                )],
                layout=go.Layout(
                    title='Similarity Ranking',
                    xaxis=dict(
                        title='Vessel ID',
                        tickangle=45,
                        tickfont=dict(size=10),
                        automargin=True
                    ),
                    yaxis=dict(title='Similarity'),
                    height=800,
                    showlegend=False,
                    margin=dict(l=50, r=50, t=50, b=150)
                )
            ).to_html(full_html=False, include_plotlyjs='cdn')}
        </div>
        
        <div class="table-container">
            <h2>Detailed Similarity Information</h2>
            <table>
                <tr>
                    <th>Vessel ID</th>
                    <th>Company</th>
                    <th>Total Similarity</th>
                    <th>Basic Feature Similarity</th>
                    <th>Sequence Similarity</th>
                    <th>Protected Area Visit Pattern</th>
                </tr>
"""

# Add table rows
for _, row in similarity_df.iterrows():
    row_class = "target-vessel" if row['vessel_id'] == target_vessel else ""
    
    # Get protected area visit pattern description
    vessel_features = sequence_features[row['vessel_id']]
    protected_pattern = []
    for area in protected_areas:
        if area in vessel_features['protected_visits']:
            before = vessel_features['before_protected'][area]
            after = vessel_features['after_protected'][area]
            pattern = f"{area}: Before visit={before}, After visit={after}"
            protected_pattern.append(pattern)
    
    html_content += f"""
                <tr class="{row_class}">
                    <td>{row['vessel_id']}</td>
                    <td>{row['company']}</td>
                    <td>{row['similarity']:.3f}</td>
                    <td>{row['basic_similarity']:.3f}</td>
                    <td>{row['sequence_similarity']:.3f}</td>
                    <td class="similarity-details">{'<br>'.join(protected_pattern)}</td>
                </tr>
"""

# Complete HTML content
html_content += """
            </table>
        </div>
    </div>
</body>
</html>
"""

# Save HTML file
with open('vessel_similarity.html', 'w') as f:
    f.write(html_content)

# Print similarity analysis for all vessels
print("\nSimilarity analysis for all vessels:")
print(similarity_df.to_string(index=False)) 