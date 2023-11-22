import ast
import networkx as nx
import matplotlib.pyplot as plt
import heapq
from pyproj import Geod

def modify_graph(graphml_input = 'new_graph.graphml', dest = 'euler_path_output.graphml', method = "fleury", length_unit = "miles"):
    """
    Modifies a graph by finding an Euler path and writing the modified graph to a GraphML file.

    Parameters:
    - graphml_input (str): Path to the input GraphML file.
    - dest (str): Path to the output GraphML file.
    - method (str): Method for Eulerization. Can be "fleury" or "min_weights" or "dijkstra".
    - length_unit (str): Unit of length for calculating distances.

    Returns:
    - list: A list containing the total distance of the Euler path and the number of artificial edges created.
    """
    G = nx.read_graphml(graphml_input)
    if method == "min_weights":
        euler_G = eulerize_minimize_weights(G)
    elif method == "dijkstra":
        euler_G = eulerize_minimize_weights_dijkistra(G)
    else:
        euler_G = eulerize_fleury(G)
    circuit = list(nx.eulerian_circuit(euler_G))
    nx.write_graphml(nx.MultiDiGraph(circuit), dest) 
    new_G = nx.MultiDiGraph()
    total_distance = 0
    artificial_edges = 0
    for source, target in circuit:
        edge_data = euler_G.get_edge_data(source, target)
        if (edge_data is None or len(edge_data[0]) == 0 or len(edge_data) == 0 or 'name' not in edge_data[0]):
            road_name = "unnamed"
            artificial_edges += 1
            init_length = calculate_distance(source, target, init_length_unit = length_unit)
        else:
            road_name = edge_data[0]['name']
            init_length = edge_data[0]['length']
            init_type = edge_data[0]['type']
        new_G.add_edge(source, target, name = road_name, length = init_length, type = init_type)
        total_distance += init_length
    
    nx.write_graphml(new_G, dest)
    old_length = G.graph['total_distance']
    circuit_length_multiplier = total_distance / old_length
    return [total_distance, old_length, circuit_length_multiplier, "artificial edges: " + str(artificial_edges)]

def eulerize_fleury(G):
    """
    Eulerizes a graph by adding edges.
    Doesn't add an edge between nodes that dont already have a single edge between them

    Parameters:
    G (networkx.Graph): The input graph.

    Returns:
    networkx.Graph: The Eulerized graph.
    """
    return nx.eulerize(G)

def eulerize_minimize_weights(old_G):
    """
    Eulerize the given graph by adding edges between pairs of odd-degree nodes
    to minimize the weights of the resulting Eulerian circuit.

    Parameters:
    old_G (networkx.Graph): The input graph.

    Returns:
    networkx.Graph: The Eulerized graph.
    """
    # Create a copy of the graph to avoid modifying the original graph
    G = old_G.copy()
    print("started eulerize_minimize_weights")
    # Find all nodes with odd degree
    odd_degree_nodes = [node for node, degree in G.degree() if degree % 2 == 1]

    # Calculate shortest paths between all pairs of odd-degree nodes
    shortest_paths = dict(nx.all_pairs_shortest_path(G))

    # Create a priority queue of pairs of odd-degree nodes, with distances as priorities
    pair_queue = [(len(shortest_paths[node_A][node_B]), node_A, node_B) for i, node_A in enumerate(odd_degree_nodes) for node_B in odd_degree_nodes[i+1:]]
    heapq.heapify(pair_queue)

    # While there are nodes with odd degree
    while pair_queue:
    
        # Pop the pair with the shortest distance
        _, node_A, node_B = heapq.heappop(pair_queue)

        if node_A in odd_degree_nodes and node_B in odd_degree_nodes:

            # Duplicate all edges in the shortest path between node1 and node2
            path = shortest_paths[node_A][node_B]
            for i in range(len(path) - 1):
                G.add_edge(path[i], path[i+1])

            # Remove node1 and node2 from the list of nodes with odd degree
            odd_degree_nodes.remove(node_A)
            odd_degree_nodes.remove(node_B)
    odd_degree_nodes = [node for node, degree in G.degree() if degree % 2 == 1]
    print("odd degree nodes: ", odd_degree_nodes)
    return nx.eulerize(G)

def eulerize_minimize_weights_dijkistra(old_G):
    """
    Eulerize the given graph by adding edges between pairs of odd-degree nodes
    to minimize the weights of the resulting Eulerian circuit.

    Parameters:
    old_G (networkx.Graph): The input graph.

    Returns:
    networkx.Graph: The Eulerized graph.
    """
    # Create a copy of the graph to avoid modifying the original graph
    G = old_G.copy()
    print("started eulerize_minimize_weights")
    # Find all nodes with odd degree
    odd_degree_nodes = [node for node, degree in G.degree() if degree % 2 == 1]

    # Calculate shortest paths between all pairs of odd-degree nodes
    shortest_paths = dict(nx.all_pairs_dijkstra_path(G, weight='length'))

    # Calculate the lengths of the shortest paths
    path_lengths = dict(nx.all_pairs_dijkstra_path_length(G, weight='length'))

    # Create a priority queue of pairs of odd-degree nodes, with distances as priorities
    pair_queue = [(path_lengths[node_A][node_B], node_A, node_B) for i, node_A in enumerate(odd_degree_nodes) for node_B in odd_degree_nodes[i+1:]]
    heapq.heapify(pair_queue)

    # While there are nodes with odd degree
    while pair_queue:
    
        # Pop the pair with the shortest distance
        _, node_A, node_B = heapq.heappop(pair_queue)

        if node_A in odd_degree_nodes and node_B in odd_degree_nodes:

            # Duplicate all edges in the shortest path between node1 and node2
            path = shortest_paths[node_A][node_B]
            for i in range(len(path) - 1):
                # Add the edge with the same weight as the original
                G.add_edge(path[i], path[i+1], length=G[path[i]][path[i+1]][0]['length'])
                print(G[path[i]][path[i+1]])
            # Remove node1 and node2 from the list of nodes with odd degree
            odd_degree_nodes.remove(node_A)
            odd_degree_nodes.remove(node_B)
    odd_degree_nodes = [node for node, degree in G.degree() if degree % 2 == 1]
    print("odd degree nodes: ", odd_degree_nodes)
    return nx.eulerize(G)

def calculate_distance_raw(lon1, lat1, lon2, lat2, in_init_length_unit = "miles"):
    """
    Calculate the distance between two points on the Earth's surface using longitude and latitude coordinates.

    Parameters:
    lon1 (float): The longitude of the first point.
    lat1 (float): The latitude of the first point.
    lon2 (float): The longitude of the second point.
    lat2 (float): The latitude of the second point.
    in_init_length_unit (str, optional): The unit of length for the calculated distance. Default is "miles".

    Returns:
    float: The calculated distance between the two points.

    """
    geod = Geod(ellps = 'WGS84')
    _, _, distance = geod.inv(lon1, lat1, lon2, lat2)
    if in_init_length_unit == "kilometers":
        return distance / 1000
    return distance / 1609.344

def calculate_distance(source, target, init_length_unit = "miles"):
    """
    Calculate the distance between two points.

    Args:
        source (str): The coordinates of the source point in the format "(latitude, longitude)".
        target (str): The coordinates of the target point in the format "(latitude, longitude)".
        init_length_unit (str, optional): The initial length unit. Defaults to "miles".

    Returns:
        float: The calculated distance between the source and target points.
    """
    tup_source = ast.literal_eval(source)
    tup_target = ast.literal_eval(target)  
    return calculate_distance_raw(tup_source[0],
                              tup_source[1],
                              tup_target[0],
                              tup_target[1],
                              in_init_length_unit = init_length_unit)