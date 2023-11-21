import ast
import networkx as nx
import matplotlib.pyplot as plt
import heapq
from math import radians, sin, cos, sqrt, atan2

def modify_graph(graphml_input = 'new_graph.graphml', dest = 'euler_path_output.graphml', method = "base"):
    G = nx.read_graphml(graphml_input)
    if method == "min_weights":
        euler_G = eulerize_minimize_weights(G)
    else:
        euler_G = eulerize_base(G)
    circuit = list(nx.eulerian_circuit(euler_G))
    #print(circuit)
    new_G = nx.MultiDiGraph(nx.create_empty_copy(euler_G))

    for source, target in circuit:
        edge_data = euler_G.get_edge_data(source, target)
        if (len(edge_data[0]) == 0 or len(edge_data) == 0 or 'name' not in edge_data[0]):
            road_name = "unnamed"
        else:
            road_name = edge_data[0]['name']
            new_G.add_edge(source, target, name = road_name, length = edge_data[0]['length'])

    nx.write_graphml(new_G, dest)

    total_distance = 0
    for (source, target) in circuit:
        if new_G.get_edge_data(source, target) is None:
            source = ast.literal_eval(source)
            target = ast.literal_eval(target)
            total_distance += calculate_distance(source[0], source[1], target[0], target[1])
        else: 
            total_distance += new_G.get_edge_data(source, target)[0]['length']
    return total_distance

def eulerize_base(G):
    return nx.eulerize(G)

def eulerize_minimize_weights(old_G):
    # Create a copy of the graph to avoid modifying the original graph
    G = old_G.copy()
    print("started eulerize_minimize_weights")
    # Find all nodes with odd degree
    odd_degree_nodes = [node for node, degree in G.degree() if degree % 2 == 1]
    #print("odd degree nodes: ", odd_degree_nodes)

    # Calculate shortest paths between all pairs of odd-degree nodes
    shortest_paths = dict(nx.all_pairs_shortest_path(G))

    # Create a priority queue of pairs of odd-degree nodes, with distances as priorities
    pair_queue = [(len(shortest_paths[node1][node2]), node1, node2) for i, node1 in enumerate(odd_degree_nodes) for node2 in odd_degree_nodes[i+1:]]
    heapq.heapify(pair_queue)

    # While there are nodes with odd degree
    while pair_queue:
    
        # Pop the pair with the shortest distance
        _, node1, node2 = heapq.heappop(pair_queue)

        if node1 in odd_degree_nodes and node2 in odd_degree_nodes:

            # Add an edge between node1 and node2
            G.add_edge(node1, node2)

            # Remove node1 and node2 from the list of nodes with odd degree
            odd_degree_nodes.remove(node1)
            odd_degree_nodes.remove(node2)
    odd_degree_nodes = [node for node, degree in G.degree() if degree % 2 == 1]
    print("odd degree nodes: ", odd_degree_nodes)
    return nx.eulerize(G)

def calculate_distance(lon1, lat1, lon2, lat2):
    # approximate radius of earth in miles
    R = 3958.8

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance