 for u, v, attributes in G.edges(data=True):
        u_attributes = G.nodes[u]
        v_attributes = G.nodes[v]

        u_coordinates_str = u_attributes.get("coordinates", "")
        v_coordinates_str = v_attributes.get("coordinates", "")

        u_coordinates = list(map(float, u_coordinates_str.split(',')) if u_coordinates_str else [])
        v_coordinates = list(map(float, v_coordinates_str.split(',')) if v_coordinates_str else [])
        properties = {"attributes": attributes}  # Include edge attributes
        coordinates = [[G.nodes[u]['x'], G.nodes[u]['y']],
                       [G.nodes[v]['x'], G.nodes[v]['y']]]  # Adjust as needed
        if u_coordinates and v_coordinates:
            # Create a LineString feature for the edge
            line_string = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [u_coordinates, v_coordinates]
                },
                "properties": {}
            }
            geojson_data["features"].append(line_string)

    # Write the GeoJSON data to a file
    


def graph_to_geojson(graphml_path, geojson_path):
    # Read the GraphML file
    G = nx.read_graphml(graphml_path)

    # Create a GeoDataFrame to store node geometries
    nodes = gpd.GeoDataFrame(geometry=gpd.points_from_xy([float(G.nodes[node]['Longitude']) for node in G.nodes()],
                                                         [float(G.nodes[node]['Latitude']) for node in G.nodes()]),
                             crs="EPSG:4326")

    # Create a GeoDataFrame to store edge geometries
    edges = gpd.GeoDataFrame(columns=['id', 'geometry'], crs="EPSG:4326")

    for edge in G.edges():
        # Extract coordinates of the edge nodes
        coords = [edge[], float(G.nodes[edge[0]]['Latitude'])],
                  (float(G.nodes[edge[1]]['Longitude']), float(G.nodes[edge[1]]['Latitude']))]

        # Create a LineString geometry for the edge
        line = LineString(coords)

        # Add the edge to the GeoDataFrame
        edges = edges.append({'id': edge, 'geometry': line}, ignore_index=True)

    # Write GeoDataFrames to GeoJSON file
    nodes.to_file(geojson_path, driver='GeoJSON')
    edges.to_file(geojson_path, driver='GeoJSON', mode='a')


def convert_to_geojson_inactive(graphml_file, dest):
    G = nx.read_graphml(graphml_file)
    geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }

    # Convert nodes to Point features
    for node, attributes in G.nodes(data=True):
        coordinates_str = attributes.get("coordinates", "")
        coordinate_sets = re.findall(r'\[([-+]?\d*\.\d+),\s*([-+]?\d*\.\d+),\s*([-+]?\d*\.\d+)\]', coordinates_str)
        coordinates = [[float(x), float(y), float(z)] for x, y, z in coordinate_sets]

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates  # Adjust as needed
            },
            "properties": {
                "name": str(node),
            }
        }
        geojson_data["features"].append(feature)

    # Convert edges to LineString features
    with open(dest, 'w') as f:
        json.dump(geojson_data, f, indent = 2)