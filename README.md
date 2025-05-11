# Vessel Activity Analysis

This project provides tools for analyzing vessel activities and identifying suspicious vessels through multiple visualization methods.

## Features

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

## Requirements

- Python 3.x
- Required packages:
  - pandas
  - matplotlib
  - json
  - numpy

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

## Notes

- The analysis focuses on fishing vessels and their activities
- Special attention is given to three locations: Nemo Reef, Ghoti Preserve, and Don Limpet Preserve
- The May 14, 2035 reference line helps identify changes in vessel behavior
- High-resolution output ensures clear visualization of vessel activities
- All vessel dwell time plots are automatically saved in the `fishing_vessel_plots` directory