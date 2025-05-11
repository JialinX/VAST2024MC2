# Vessel Activity Analysis

This project provides tools for analyzing vessel activities and identifying suspicious vessels through multiple visualization methods.

## Features
### Flow traces cargo journeys from catch regions to export cities using Sankey Diagram
- Join conditions for generating data -> final_filter.xlsx
    - Vessel-harbor city visit date - Vessel-region visit date ≤ 6 days
    - Export transaction date - Vessel-harbor city visit date ≤ 1 day
- Run sankey_diagram.py to generate the Sankey Diagram
  
### 1. Vessel Dwell Time Analysis
- Generates individual dwell time distribution graphs for each vessel
- Shows vessel activities across different locations over time
- Highlights specific locations (Nemo Reef, Ghoti Preserve, Don Limpet Preserve) in orange

### 2. Suspicious Vessel Identification
Uses four different visualization methods to identify suspicious vessels:
- Bar Graph Analysis
- Sunburst Chart Analysis
- Path Map Similarity Analysis
- Parallel Coordinates Analysis

### 3. Sunburst Chart Analysis

* **Large interactive Plotly Sunburst** (1200 × 700) centred on the page.
* **Cluster explorer**: search any cluster ID to list underlying cycles and vessels.
* **Risk table** automatically flags vessels spending > 20 % of total dwell time inside *ecological preserves*.
* SSE‑specific summaries: vessel list, cycles present in the viz, and each vessel’s cluster lineage.
* **Debug prints** at each major processing stage for transparent data‑reduction tracing.

## Requirements

- Python 3.8+
- Required packages:
  - pandas
  - matplotlib
  - json
  - numpy
  - networkx
  - scikit-learn
  - scipy
  - plotly

## Usage

### 1. Generate Vessel Dwell Time Plots

Run the following command to generate dwell time distribution plots for all vessels:

```bash
python analyze_all_vessels_dwell.py
```

This will:
- Create a `fishing_vessel_plots` directory
- Generate individual PNG files for each vessel
- Show vessel activities with:
  - Orange bars for special locations
  - Blue bars for other locations
  - Red reference line for May 14, 2035

All generated plots will be saved in the `fishing_vessel_plots` directory.

### 2. Generate Suspicious Vessel Venn Diagram

Run the following command to generate the Venn diagram showing suspicious vessels identified through different methods:

```bash
python venn_graph.py
```

This will:
- Analyze vessels using four different visualization methods
- Generate a Venn diagram showing the overlap of suspicious vessels
- Help identify vessels that are suspicious across multiple analysis methods

### 3. Generate Sunburst Chart 

```bash
python sunburst.py
```

Optional parameter tweaks (edit inside the script)

| Variable           | Purpose                                                      | Default      |
| ------------------ | ------------------------------------------------------------ | ------------ |
| `MIN_PINGS`        | Minimum pings between *leaving* and *returning* to any port to qualify as a cycle | `3`          |
| `SAMPLE_CYCLES`    | If not `None`, randomly subsample cycles to this number for faster prototyping | `None`       |
| `COLOR_RANGE`      | Continuous color range for foreground‑ratio heatmap (`[min,max]`) | `[0, 0.4]`   |
| `FIG_WIDTH/HEIGHT` | Sunburst dimensions in pixels                                | `1200 / 700` |

### 4. Generate Path Map

Run the following command to generate the fishing vessel routes json file first :

```bash
python extract_vessel_routes.py
```

Then run the command to generate the path map

```bash
python visualize_vessel_routes.py
```

This will:
- Filter out the other vessels that is not fishing vessel 
- Generate a Path Map showing all the trajectory and dwell bar graph of the vessels
- Help identify when the vessel enter the preserve area and which preserve they entered

### 5. Generate Parallel Coordinates

```bash
python vessel_parallel_coordinates.py
```

This will:
- Generate a Parallel Coordinates graph that can interact with
- Help identify when the vessel enter the preserve area, how long the vessel stay in the preserve and which preserve they entered 

### 6. Generate Vessel Similarity

```bash
python vessel_similarity.py
```

- Generate a Bar graph that ranking the vessels based on similarity score, closer to the left means the vessel's behaviour is more suspicious


## Output

### Dwell Time Plots
- Location: `fishing_vessel_plots/`
- Format: PNG files
- Naming: `vessel_[vessel_id]_dwell_time.png`
- Features:
  - Time-based x-axis
  - Location-based y-axis
  - Color-coded activity bars
  - Reference line for May 14, 2035

### Venn Diagram
- Shows the intersection of suspicious vessels identified by different methods
- Helps identify the most suspicious vessels based on multiple criteria

### Sunburst Chart
#### Sunburst Visualization
* **Location:** `sunburst.html`
* **Format:** Self‑contained HTML (offline; includes Plotly JS)
* **Features:**
  * Click‑to‑zoom hierarchical clusters
  * Colour scale (`RdYlBu_r`) mapped to *fg\_ratio* (0 – 0.4 by default)
  * Hover tooltip shows both *fg\_ratio* and *ep\_ratio*
  * Search box under the chart to list vessels & cycles per cluster
#### Risk Table
* Automatically flags vessels whose ecological‑preserve dwell ratio exceeds
  * **≥ 0.4** → *High* risk (red dot)
  * **0.2 – 0.4** → *Medium* risk (yellow dot)
* Presented below the chart for quick triage
#### SSE Fleet Sections
* **Vessels list** with count
* **Cycles in visualization** count
* **Cluster lineages** for every SSE vessel (easily copy‑pastable)

### Sankey Diagram
#### Sankey Diagram Visualization
* **Location:** `sankey_diagram.html`
* **Format:** Self‑contained HTML (offline; includes Plotly JS)
* **Features:**
  * Hover to see the value counts of a node(income/outcome) or name of target/source of a link 
  * Dragging the node in the blank area can see the connection more clearly

### Fishing Vessels Path Map
#### Processed data file
- Location: `fishing_vessel_routes.json`
- Format: json file
- Features:
  - Only keep the fishing vessels data
  - Simplify and reconstruct the data structure for easy data load

#### Path Map
- Location: `fishing_vessel_routes_map.html`
- Format: Self‑contained HTML (offline; includes folium)
- Features:
  - Trajectory of fishing vessels on map
  - The trajectory is draw on the real geographic location
  - Color-coded routes and zones with embedded dwell time analysis

### Parallel Coordinates
- Location: `vessel_parallel_coordinates.html`
- Format: (offline; includes Plotly JS)
- Features:
  - Can adjust the sequence of different dimension without changing the code
  - Easiler to filter the data based on time and find out the potential result

### Vessel Similarity
- Location: `vessel_similarity.html`
- Format: (offline; includes Plotly JS)
- Features:
  - Ranking the vessels' similarity score from high to low, vessels with higher score means it is more suspicious

## Notes

- The analysis focuses on fishing vessels and their activities
- Special attention is given to three locations: Nemo Reef, Ghoti Preserve, and Don Limpet Preserve
- The May 14, 2035 reference line helps identify changes in vessel behavior
- High-resolution output ensures clear visualization of vessel activities
- All vessel dwell time plots are automatically saved in the `fishing_vessel_plots` directory



