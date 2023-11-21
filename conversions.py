import ast
import math
import geopandas as gpd 
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import scipy as sp
import json
import re 
import osmnx as ox
from find_euler_path import calculate_distance_raw
from shapely.geometry import MultiLineString, LineString

def convert_to_graph_road_nodes(geojson_file, dest = 'new_graph.graphml'):
    G = nx.Graph()
    with open(geojson_file, 'r') as f:
        geojson_data = json.load(f)

    node_count = 0
    for feature in geojson_data['features']:
        coordinates = feature['geometry']['coordinates']
        coordinates_str = ",".join(map(str, coordinates))
        G.add_node(node_count, coordinates=coordinates_str)
        node_count += 1

    nx.write_graphml(G, dest)

def convert_to_graph_road_edges(geojson_file, dest = 'new_graph.graphml', formatted_road_name = 'FullStName', has_properties = True, length_unit = "Miles"):
    """
    Converts a GeoJSON file containing road data into a NetworkX graph with road edges.

    Parameters:
    - geojson_file (str): The path to the GeoJSON file.
    - dest (str): The destination path to save the resulting graph file (default: 'new_graph.graphml').
    - formatted_road_name (str): The name of the road property in the GeoJSON file (default: 'FullStName').
    - has_properties (bool): Indicates whether the GeoJSON file has road properties (default: True).
    - length_unit (str): The unit of length for calculating road distances (default: 'Miles').

    Returns:
    - None

    """
    # Load the GeoJSON file
    gdf = gpd.read_file(geojson_file)

    # Create a NetworkX graph
    G = nx.MultiGraph()

    # Add edges to the graph
    for _, road in gdf.iterrows():
        geometry = road.geometry
        if isinstance(geometry, LineString):
            line = [geometry]
        elif isinstance(geometry, MultiLineString):
            line = list(geometry)

        for linestring in line:
            for source, target in zip(list(linestring.coords[:-1]), list(linestring.coords[1:])):
                if has_properties:
                    rd_name = road[formatted_road_name]
                else:
                    rd_name = "unnamed"
                G.add_edge(source,
                           target,
                           name = rd_name,
                           length = calculate_distance_raw(source[0],
                                                           source[1],
                                                           target[0],
                                                           target[1],
                                                           in_init_length_unit = length_unit))

    # Save the graph to a GraphML file
    nx.write_graphml(G, dest)

def convert_to_geojson(graphml_file, dest = 'output_geojson.geojson', formatted_road_name = 'FullStName'):
    """
    Convert a GraphML file to GeoJSON format.

    Args:
        graphml_file (str): The path to the GraphML file.
        dest (str, optional): The destination path for the GeoJSON output file. Defaults to 'output_geojson.geojson'.
        formatted_road_name (str, optional): The column name for the road name in the GeoJSON file. Defaults to 'FullStName'.

    Returns:
        None
    """
    G = nx.read_graphml(graphml_file)
    gdf = gpd.GeoDataFrame(columns = ['order', formatted_road_name, "length", 'heading', 'geometry'])
    order = 0 # count for each road to be taken to follow eularian path. Later used to label each road
    first_road = list(G.edges(data = True))[0]
    previous_road_name = first_road[2]['name']
    for source, target, data in G.edges(data = True):
        source = ast.literal_eval(source)
        target = ast.literal_eval(target)
        if data['name'] != previous_road_name:
            order += 1
        previous_road_name = data['name']
        heading = find_heading(source, target)
        new_road = gpd.GeoDataFrame({
            'order': [str(order) + ", "],
            formatted_road_name: [data['name']], # 'FullStName' is the column name for the road name in the geojson file
            'length': [data['length']], # 'Miles' is the column name for the road length in the geojson file
            'heading': [heading],
            'geometry': [LineString([source, target])]
        })
        gdf = pd.concat([gdf, new_road], ignore_index = True)
    gdf.to_file(dest, driver = 'GeoJSON')

def find_heading(source, target):
    """
    Calculates the bearing between two points.
    The formulae used is the following:
        θ = atan2(sin(Δlong).cos(lat2),
                  cos(lat1).sin(lat2) − sin(lat1).cos(lat2).cos(Δlong))
    :Parameters:
      - `source: The tuple representing the longitude/lattitude for the
        first point. Latitude and longitude must be in decimal degrees
      - `target: The tuple representing the long/lat for the
        second point. Latitude and longitude must be in decimal degrees
    :Returns:
      The bearing in degrees
    :Returns Type:
      float
    """
    if (type(source) != tuple) or (type(target) != tuple):
        raise TypeError("Only tuples are supported as arguments")

    lat1 = math.radians(source[1])
    lat2 = math.radians(target[1])

    diffLong = math.radians(target[0] - source[0])

    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1)
            * math.cos(lat2) * math.cos(diffLong))

    initial_bearing = math.atan2(x, y)

    # Now we have the initial bearing but math.atan2 return values
    # from -180° to + 180° which is not what we want for a compass bearing
    # The solution is to normalize the initial bearing as shown below
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing

