import folium
import json
from datetime import datetime
from folium.plugins import MarkerCluster
import random

def get_random_color():
    """Generate random color"""
    return '#{:06x}'.format(random.randint(0, 0xFFFFFF))

def get_location_coords(geojson_data):
    """Get coordinates for all locations"""
    location_coords = {}
    
    # Special areas list
    special_areas = ['Wrasse Beds', 'Cod Table', 'Tuna Shelf', 'Don Limpet Preserve', 'Ghoti Preserve']
    
    # Label position offset settings
    label_offsets = {
        'Wrasse Beds': {'lat': 0, 'lon': -0.1},
        'Cod Table': {'lat': 0, 'lon': 0},
        'Tuna Shelf': {'lat': 0, 'lon': -0.1},
        'Don Limpet Preserve': {'lat': 0, 'lon': -0.2},
        'Ghoti Preserve': {'lat': 0, 'lon': -0.15},
        'Suna Island': {'lat': 0, 'lon': 0},
        'Thalassa Retreat': {'lat': 0.15, 'lon': -0.25},
        'Makara Shoal': {'lat': 0, 'lon': 0},
        'Silent Sanctuary': {'lat': 0, 'lon': 0},
        'Nemo Reef': {'lat': 0, 'lon': 0},
        # City offset settings
        'Haacklee': {'lat': 0, 'lon': 0},
        'Port Grove': {'lat': 0, 'lon': 0},
        'Lomark': {'lat': 0, 'lon': 0},
        'Himark': {'lat': 0, 'lon': 0},
        'Paackland': {'lat': 0, 'lon': 0},
        'Centralia': {'lat': 0, 'lon': 0},
        'South Paackland': {'lat': 0, 'lon': 0},
        # Buoy offset settings
        'Nav 3': {'lat': 0.05, 'lon': 0},
        'Nav 2': {'lat': 0.05, 'lon': 0}
    }
    
    # Process coordinates for each feature
    for feature in geojson_data['features']:
        name = feature['properties']['Name']
        
        if feature['geometry']['type'] == 'Point':
            coords = feature['geometry']['coordinates']
            location_coords[name] = [coords[1], coords[0]]  # folium uses [lat, lon] order
        elif feature['geometry']['type'] == 'Polygon':
            # For polygon features, use center point coordinates
            coords = feature['geometry']['coordinates'][0]
            lat_max = max(coord[1] for coord in coords)
            lat_min = min(coord[1] for coord in coords)
            lon_max = max(coord[0] for coord in coords)
            lon_min = min(coord[0] for coord in coords)
            center_lat = (lat_max + lat_min) / 2
            center_lon = (lon_max + lon_min) / 2
            location_coords[name] = [center_lat, center_lon]
    
    # Add city prefix locations
    for city in ['Himark', 'Lomark', 'Paackland']:
        if city in location_coords:
            location_coords[f'City of {city}'] = location_coords[city]
    
    # Manually add possible alias mappings
    location_coords['Exit East'] = location_coords.get('Exit East', [-1, -1])
    location_coords['Wrasse Beds'] = location_coords.get('Wrasse Beds', [-1, -1])
    location_coords['Cod Table'] = location_coords.get('Cod Table', [-1, -1])
    location_coords['Nav 1'] = location_coords.get('Nav 1', [-1, -1])
    location_coords['Nav 2'] = location_coords.get('Nav 2', [-1, -1])
    location_coords['Nav C'] = location_coords.get('Nav C', [-1, -1])
    location_coords['Nav E'] = location_coords.get('Nav E', [-1, -1])
    location_coords['Nav A'] = location_coords.get('Nav A', [-1, -1])
    location_coords['Ghoti Preserve'] = location_coords.get('Ghoti Preserve', [-1, -1])
    
    return location_coords

def visualize_vessel_routes():
    print("Starting to create vessel route visualization map...")
    
    try:
        # Read GeoJSON file
        print("Reading GeoJSON file...")
        with open('MC2/Oceanus Information/Oceanus Geography.geojson', 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)
        print("GeoJSON file read successfully")
        
        # Create map, set center point and zoom level
        m = folium.Map(location=[39.0, -165.0], zoom_start=8, tiles='OpenStreetMap')
        
        # Add map container style
        map_container_style = '''
        <style>
        #map {
            position: absolute !important;
            left: 0;
            top: 0;
            bottom: 0;
            width: calc(100% - 440px) !important;
            height: 100% !important;
            transition: width 0.3s ease;
        }
        
        #imageViewer {
            transition: all 0.3s ease;
        }
        
        #imageContainer {
            transition: all 0.3s ease;
        }
        
        /* Add scrollbar style */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 3px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        
        /* Optimize legend item style */
        .legend-item {
            padding: 8px !important;
            margin: 4px 0 !important;
            border-radius: 4px;
            transition: background-color 0.2s;
        }
        
        .legend-item:hover {
            background-color: #f5f5f5;
        }
        </style>
        '''
        
        # Set colors for different areas
        color_dict = {
            'Island': 'green',
            'Ecological Preserve': 'red',
            'Fishing Ground': 'blue',
            'city': 'purple',
            'buoy': 'orange'
        }
        
        # Special areas list
        special_areas = ['Wrasse Beds', 'Cod Table', 'Tuna Shelf', 'Don Limpet Preserve', 'Ghoti Preserve']
        
        # Add zoom-responsive JavaScript
        m.get_root().html.add_child(folium.Element("""
        <script>
        var zoom_labels = document.getElementsByClassName('zoom-label');
        map.on('zoomend', function() {
            var zoom = map.getZoom();
            var scale = Math.max(0.5, zoom/12);
            for (var i = 0; i < zoom_labels.length; i++) {
                zoom_labels[i].style.transform = 'scale(' + scale + ')';
                zoom_labels[i].style.transformOrigin = 'center center';
            }
        });
        </script>
        """))
        
        # Add area name labels
        for feature in geojson_data['features']:
            name = feature['properties']['Name']
            kind = feature['properties']['*Kind']
            
            if feature['geometry']['type'] == 'Point':
                coords = feature['geometry']['coordinates']
                if kind == 'city':
                    # Add orange circle marker for cities
                    folium.CircleMarker(
                        location=[coords[1], coords[0]],
                        radius=4,
                        color='orange',
                        fill=True,
                        fillColor='orange',
                        fillOpacity=1.0,
                        popup=name,
                        weight=1
                    ).add_to(m)
                    
                    # Add city name label
                    folium.Marker(
                        location=[coords[1], coords[0]],
                        popup=name,
                        icon=folium.DivIcon(html=f'<div class="zoom-label" style="font-size: 12pt; color: black; text-shadow: 1px 1px 1px white; white-space: nowrap;">{name}</div>')
                    ).add_to(m)
                elif kind == 'buoy':
                    # Add circle marker for buoys
                    folium.CircleMarker(
                        location=[coords[1], coords[0]],
                        radius=4,
                        color='orange',
                        fill=True,
                        fillColor='orange',
                        fillOpacity=1.0,
                        popup=name,
                        weight=1
                    ).add_to(m)
                    
                    # Add buoy name label
                    label_class = 'label-below' if name in ['Nav 3', 'Nav 2'] else 'label-above'
                    position_style = 'position: relative; ' + ('top: 15px;' if name in ['Nav 3', 'Nav 2'] else 'bottom: 15px;')
                    
                    folium.Marker(
                        location=[coords[1], coords[0]],
                        popup=name,
                        icon=folium.DivIcon(html=f'<div class="{label_class}" style="{position_style}"><div class="zoom-label" style="font-size: 10pt; color: black; text-shadow: 1px 1px 1px white; white-space: nowrap;">{name}</div></div>')
                    ).add_to(m)
            else:
                # For polygon features (areas)
                coords = feature['geometry']['coordinates'][0]
                lat_max = max(coord[1] for coord in coords)
                lat_min = min(coord[1] for coord in coords)
                lon_max = max(coord[0] for coord in coords)
                lon_min = min(coord[0] for coord in coords)
                center_lat = (lat_max + lat_min) / 2
                center_lon = (lon_max + lon_min) / 2
                
                # Set different font sizes and styles
                font_size = '14pt' if name in special_areas else '11pt'
                font_weight = 'bold' if (name in special_areas or kind == 'Island') else 'normal'
                
                # Handle special name line breaks
                display_name = 'Don Limpet<br>Preserve' if name == 'Don Limpet Preserve' else name
                
                # Add area name label
                folium.Marker(
                    location=[center_lat, center_lon],
                    popup=name,
                    icon=folium.DivIcon(html=f'<div class="zoom-label" style="font-size: {font_size}; font-weight: {font_weight}; color: black; text-shadow: 1px 1px 2px white; white-space: nowrap; text-align: center;">{display_name}</div>')
                ).add_to(m)
                
                # Add center point marker for islands
                if kind == 'Island':
                    folium.CircleMarker(
                        location=[center_lat, center_lon],
                        radius=4,
                        color='orange',
                        fill=True,
                        fillColor='orange',
                        fillOpacity=1.0,
                        popup=name,
                        weight=1
                    ).add_to(m)
        
        # Create filtered GeoJSON data (excluding buoys and city points)
        filtered_geojson = {
            "type": "FeatureCollection",
            "features": [feature for feature in geojson_data["features"] 
                        if not (feature["geometry"]["type"] == "Point" and 
                                (feature["properties"]["*Kind"] == "buoy" or 
                                 feature["properties"]["*Kind"] == "city"))]
        }
        
        # Add filtered GeoJSON layer
        print("Adding geographic information layer...")
        folium.GeoJson(
            filtered_geojson,
            style_function=lambda x: {
                'fillColor': color_dict.get(x['properties']['*Kind'], 'gray'),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.5
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['Name', '*Kind', 'Description'],
                aliases=['Name', 'Type', 'Description'],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
            )
        ).add_to(m)
        
        # Read fishing vessel route data
        print("Reading fishing vessel route data...")
        with open('./fishing_vessel_routes.json', 'r', encoding='utf-8') as f:
            vessel_data = json.load(f)
        print(f"Successfully read vessel data, found {len(vessel_data['fishing_vessels'])} vessels")
        
        # Get location coordinate mapping
        print("Creating location coordinate mapping...")
        location_coords = get_location_coords(geojson_data)
        
        # Check if each vessel has passed through specified preserves
        target_preserves = ["Don Limpet Preserve", "Ghoti Preserve", "Nemo Reef"]
        vessels_through_preserves = set()
        
        for vessel in vessel_data['fishing_vessels']:
            vessel_id = vessel['vessel_id']
            route_locations = set(point['location'] for point in vessel['route'])
            if any(preserve in route_locations for preserve in target_preserves):
                vessels_through_preserves.add(vessel_id)
        
        # Assign colors to each vessel
        vessel_colors = {}
        for vessel in vessel_data['fishing_vessels']:
            vessel_id = vessel['vessel_id']
            if vessel_id in vessels_through_preserves:
                vessel_colors[vessel_id] = get_random_color()
        
        # Add vessel routes
        print("Adding vessel routes...")
        missing_locations = set()
        vessel_routes_js = []  # Store all route JavaScript objects

        for vessel in vessel_data['fishing_vessels']:
            vessel_id = vessel['vessel_id']
            if vessel_id not in vessels_through_preserves:
                continue
                
            route_points = []
            print(f"Processing vessel ID: {vessel_id}")
            for point in vessel['route']:
                location = point['location']
                if location in location_coords and location_coords[location][0] != -1:
                    route_points.append(location_coords[location])
                else:
                    missing_locations.add(location)
            if route_points:
                print(f"Found {len(route_points)} valid waypoints")
                # Add route
                route = folium.PolyLine(
                    locations=route_points,
                    color=vessel_colors[vessel_id],
                    weight=2,
                    opacity=0.7,
                    tooltip=f"Vessel ID: {vessel_id}",
                    name=f"route_{vessel_id}"
                ).add_to(m)
                vessel_routes_js.append({
                    'id': vessel_id,
                    'color': vessel_colors[vessel_id]
                })
                
                # Create custom start icon
                start_icon_html = f'''
                    <div class="custom-marker start-{vessel_id}" 
                         style="background-color: #4CAF50; 
                                width: 28px; 
                                height: 28px; 
                                border-radius: 50%; 
                                display: flex; 
                                align-items: center; 
                                justify-content: center; 
                                position: relative;
                                border: 2px solid white;
                                box-shadow: 0 0 4px rgba(0,0,0,0.3);">
                        <i class="fa fa-play" 
                           style="color: white; 
                                  position: absolute; 
                                  left: 50%; 
                                  top: 50%; 
                                  transform: translate(-35%, -50%); 
                                  font-size: 16px;"></i>
                    </div>
                '''
                # Create custom end icon
                end_icon_html = f'''
                    <div class="custom-marker end-{vessel_id}" 
                         style="background-color: #f44336; 
                                width: 24px; 
                                height: 24px; 
                                border-radius: 50%; 
                                display: flex; 
                                align-items: center; 
                                justify-content: center; 
                                position: relative;
                                border: 2px solid white;
                                box-shadow: 0 0 4px rgba(0,0,0,0.3);">
                        <i class="fa fa-stop" 
                           style="color: white; 
                                  position: absolute; 
                                  left: 50%; 
                                  top: 50%; 
                                  transform: translate(-50%, -50%); 
                                  font-size: 14px;"></i>
                    </div>
                '''
                
                # Check if start and end points overlap
                start_point = route_points[0]
                end_point = route_points[-1]
                is_overlapping = start_point == end_point

                if is_overlapping:
                    # Create combined icon (when start and end points overlap)
                    combined_icon_html = f'''
                        <div style="position: relative; width: 40px; height: 40px;">
                            <div class="custom-marker start-{vessel_id}" 
                                 style="background-color: #4CAF50; 
                                        width: 28px; 
                                        height: 28px; 
                                        border-radius: 50%; 
                                        position: absolute;
                                        left: 0;
                                        top: 0;
                                        border: 2px solid white;
                                        box-shadow: 0 0 4px rgba(0,0,0,0.3);
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;">
                                <i class="fa fa-play" 
                                   style="color: white; 
                                          position: absolute;
                                          left: 50%;
                                          top: 50%;
                                          transform: translate(-35%, -50%);
                                          font-size: 16px;"></i>
                            </div>
                            <div class="custom-marker end-{vessel_id}" 
                                 style="background-color: #f44336; 
                                        width: 24px; 
                                        height: 24px; 
                                        border-radius: 50%; 
                                        position: absolute;
                                        right: 0;
                                        bottom: 0;
                                        border: 2px solid white;
                                        box-shadow: 0 0 4px rgba(0,0,0,0.3);
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;">
                                <i class="fa fa-stop" 
                                   style="color: white; 
                                          position: absolute;
                                          left: 50%;
                                          top: 50%;
                                          transform: translate(-50%, -50%);
                                          font-size: 14px;"></i>
                            </div>
                        </div>
                    '''
                    
                    # Add combined marker
                    folium.Marker(
                        location=start_point,
                        popup=f"Vessel ID: {vessel_id}<br>Start and end points overlap",
                        icon=folium.DivIcon(
                            html=combined_icon_html,
                            icon_size=(40, 40),
                            icon_anchor=(20, 20)
                        )
                    ).add_to(m)
                else:
                    # Add start marker
                    folium.Marker(
                        location=start_point,
                        popup=f"Vessel ID: {vessel_id}<br>Start point",
                        icon=folium.DivIcon(
                            html=start_icon_html,
                            icon_size=(28, 28),
                            icon_anchor=(14, 14)
                        )
                    ).add_to(m)
                    
                    # Add end marker
                    folium.Marker(
                        location=end_point,
                        popup=f"Vessel ID: {vessel_id}<br>End point",
                        icon=folium.DivIcon(
                            html=end_icon_html,
                            icon_size=(24, 24),
                            icon_anchor=(12, 12)
                        )
                    ).add_to(m)
            else:
                print(f"Warning: Vessel {vessel_id} has no valid waypoints")
        
        if missing_locations:
            print("\nLocations with missing coordinates:")
            for loc in sorted(missing_locations):
                print(f"- {loc}")
        
        # Add legend and interactive features
        print("Adding legend...")
        total_vessels = len(vessel_data['fishing_vessels'])
        vessels_through_count = len(vessels_through_preserves)
        
        # Add image viewer area
        image_viewer_html = '''
        <div id="imageViewer" style="position: fixed; 
             bottom: 20px; right: 20px; 
             width: 600px; 
             height: calc(100vh - 500px);
             min-height: 350px;
             max-height: 450px;
             background-color: white;
             border: 2px solid grey;
             border-radius: 5px;
             padding: 12px;
             display: none;
             z-index: 1000;
             overflow-y: auto;">
            <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                <span id="imageTitle" style="font-weight: bold; font-size: 14px;"></span>
                <button onclick="closeImageViewer()" 
                        style="cursor: pointer; 
                               background-color: #f44336; 
                               color: white; 
                               border: none; 
                               padding: 4px 8px; 
                               border-radius: 3px;
                               font-size: 12px;">
                    Close
                </button>
            </div>
            <div id="imageContainer" style="width: 100%; text-align: center;">
                <img id="vesselImage" src="" style="width: 100%; height: auto; margin-top: 8px;" />
            </div>
        </div>
        '''
        
        # Modify legend position to top right
        legend_html = f'''
        <div style="position: fixed; 
             top: 20px; right: 20px; 
             width: 400px; 
             height: 300px; 
             border: 2px solid grey; 
             z-index: 1001; 
             font-size: 12px;
             background-color: white; 
             padding: 10px;
             border-radius: 5px;
             box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
             <div style="margin-bottom: 8px">
                <b style="font-size: 14px;">Vessel Routes Through Protected Areas Legend</b>
                <div style="margin-top: 4px; font-size: 11px; color: #666;">
                    Total Vessels: <span style="font-weight: bold">{total_vessels}</span>
                    <br/>
                    Vessels Through Protected Areas: <span style="font-weight: bold">{vessels_through_count}</span>
                </div>
             </div>
             <div style="height: calc(100% - 60px); overflow-y: auto;">
        '''
        
        # Add clickable legend items for each vessel
        for vessel in vessel_data['fishing_vessels']:
            vessel_id = vessel['vessel_id']
            if vessel_id not in vessels_through_preserves:
                continue
                
            color = vessel_colors[vessel_id]
            legend_html += f'''
            <div class="legend-item" data-vessel-id="{vessel_id}" 
                 style="display: flex; align-items: center; margin-bottom: 2px; cursor: pointer; padding: 3px;">
                <div style="min-width: 16px; height: 3px; background-color: {color}; margin-right: 8px;"></div>
                <span style="white-space: nowrap; font-size: 11px;">Vessel ID: {vessel_id}</span>
            </div>
            '''
        
        legend_html += '''
            </div>
        </div>
        '''

        # Modify showVesselImage function in JavaScript
        js = """
        <script>
        var vesselRoutes = """ + json.dumps(vessel_routes_js) + """;
        var selectedVessel = null;
        var originalColors = {};  // Store original colors

        function showVesselImage(vesselId) {
            var imageViewer = document.getElementById('imageViewer');
            var vesselImage = document.getElementById('vesselImage');
            var imageTitle = document.getElementById('imageTitle');
            var map = document.getElementById('map');
            
            // Set image path
            vesselImage.src = 'fishing_vessel_plots/vessel_' + vesselId + '_dwell_time.png';
            imageTitle.textContent = 'Vessel ID: ' + vesselId + ' Dwell Time Analysis';
            
            // Show image viewer
            imageViewer.style.display = 'block';
            
            // Add image loading error handling
            vesselImage.onerror = function() {
                imageTitle.textContent = 'No dwell time analysis chart found for this vessel';
                vesselImage.style.display = 'none';
            };
            
            vesselImage.onload = function() {
                vesselImage.style.display = 'block';
            };
        }
        
        function closeImageViewer() {
            var imageViewer = document.getElementById('imageViewer');
            imageViewer.style.display = 'none';
        }

        // Add class to all route paths after map loads
        function addRouteClasses() {
            // Get color to id mapping for all legends
            var color2id = {};
            vesselRoutes.forEach(function(v){ 
                color2id[v.color.toLowerCase()] = v.id;
                originalColors[v.id] = v.color;  // Save original color
            });
            
            // Iterate through all path elements
            var paths = document.querySelectorAll('path');
            var count = 0;
            paths.forEach(function(p){
                var stroke = p.getAttribute('stroke');
                if(stroke) {
                    var c = stroke.toLowerCase();
                    if(color2id[c]) {
                        p.classList.add('route-' + color2id[c]);
                        count++;
                    }
                }
            });
        }
        
        function showOnlyVessel(vesselId) {
            vesselRoutes.forEach(function(vessel) {
                var rid = vessel.id;
                var show = (rid === vesselId);
                // Route
                var routeEls = document.querySelectorAll('path.route-' + rid);
                for (var i = 0; i < routeEls.length; i++) {
                    routeEls[i].style.display = show ? '' : 'none';
                    if (show) {
                        routeEls[i].setAttribute('stroke', '#ff0000');
                    }
                }
                // Start point
                var startEls = document.getElementsByClassName('start-' + rid);
                for (var i = 0; i < startEls.length; i++) {
                    startEls[i].style.display = show ? '' : 'none';
                }
                // End point
                var endEls = document.getElementsByClassName('end-' + rid);
                for (var i = 0; i < endEls.length; i++) {
                    endEls[i].style.display = show ? '' : 'none';
                }
            });
            
            // Show selected vessel's image
            showVesselImage(vesselId);
        }
        
        function initializeLegendItems() {
            var legendItems = document.getElementsByClassName('legend-item');
            Array.from(legendItems).forEach(function(item) {
                item.addEventListener('click', function() {
                    var vesselId = this.getAttribute('data-vessel-id');
                    if(selectedVessel === vesselId) {
                        vesselRoutes.forEach(function(vessel) {
                            var rid = vessel.id;
                            var routeEls = document.querySelectorAll('path.route-' + rid);
                            for (var i = 0; i < routeEls.length; i++) {
                                routeEls[i].style.display = '';
                                routeEls[i].setAttribute('stroke', originalColors[rid]);
                            }
                            var startEls = document.getElementsByClassName('start-' + rid);
                            for (var i = 0; i < startEls.length; i++) {
                                startEls[i].style.display = '';
                            }
                            var endEls = document.getElementsByClassName('end-' + rid);
                            for (var i = 0; i < endEls.length; i++) {
                                endEls[i].style.display = '';
                            }
                        });
                        selectedVessel = null;
                        closeImageViewer();
                        Array.from(legendItems).forEach(function(li) {
                            li.style.backgroundColor = 'transparent';
                            var colorBar = li.querySelector('div');
                            var vid = li.getAttribute('data-vessel-id');
                            if (colorBar && vid) {
                                colorBar.style.backgroundColor = originalColors[vid];
                            }
                        });
                    } else {
                        showOnlyVessel(vesselId);
                        selectedVessel = vesselId;
                        Array.from(legendItems).forEach(function(li) {
                            li.style.backgroundColor = 'transparent';
                            var colorBar = li.querySelector('div');
                            if (colorBar) {
                                colorBar.style.backgroundColor = li === this ? '#ff0000' : originalColors[li.getAttribute('data-vessel-id')];
                            }
                        }, this);
                        this.style.backgroundColor = '#e6e6e6';
                    }
                });
            });
        }
        
        window.addEventListener('load', function() {
            setTimeout(addRouteClasses, 1000);
            setTimeout(initializeLegendItems, 1200);
        });
        </script>
        """
        
        # Add all elements to map
        m.get_root().html.add_child(folium.Element(map_container_style))
        m.get_root().html.add_child(folium.Element(image_viewer_html))
        m.get_root().html.add_child(folium.Element(legend_html))
        m.get_root().html.add_child(folium.Element(js))
        
        # Save map
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'fishing_vessel_routes_map.html'
        print(f"Saving map to file: {output_file}")
        m.save(output_file)
        print(f"\nMap successfully saved as {output_file}")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    visualize_vessel_routes() 