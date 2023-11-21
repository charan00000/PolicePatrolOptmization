import ast
import geopandas as gpd 
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import scipy as sp
import json
import re 
import osmnx as ox
from shapely.geometry import MultiLineString, LineString

def convert_to_graph_road_nodes(geojson_file, dest = 'new_graph.graphml'):
    print("here")
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

def convert_to_graph_road_edges(geojson_file, dest = 'new_graph.graphml', formatted_road_name = 'FullStName'):
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
            for start, target in zip(list(linestring.coords[:-1]), list(linestring.coords[1:])):
                G.add_edge(start, target, name = road[formatted_road_name])

    # Save the graph to a GraphML file
    nx.write_graphml(G, dest)

def convert_to_geojson(graphml_file, dest = 'output_geojson.geojson', formatted_road_name = 'FullStName'):
    G = nx.read_graphml(graphml_file)
    gdf = gpd.GeoDataFrame(columns = ['order', formatted_road_name, 'geometry'])
    order = 0 # count for each road to be taken to follow eularian path. Later used to label each road
    first_road = list(G.edges(data = True))[0]
    previous_road_name = first_road[2]['name']
    for source, target, data in G.edges(data = True):
        source = ast.literal_eval(source)
        target = ast.literal_eval(target)
        new_road = gpd.GeoDataFrame({
            'order': [str(order) + ", "],
            formatted_road_name: [data['name']], # 'FullStName' is the column name for the road name in the geojson file
            'geometry': [LineString([source, target])]
        })
        if data['name'] != previous_road_name:
            order += 1
        previous_road_name = data['name']
        gdf = pd.concat([gdf, new_road], ignore_index = True)
    gdf.to_file(dest, driver = 'GeoJSON')



#pos = nx.spring_layout(G) # Position dictionary
#nx.draw(G, pos, with_labels=False, node_size=5)
#plt.axis('off')
#plt.show()


