import networkx as nx
import matplotlib.pyplot as plt

def builtin_method(graphml_input = 'new_graph.graphml', dest = 'euler_path_output.graphml'):
    G = nx.read_graphml(graphml_input)
    euler_G = custom_eulerize(G)
    circuit = list(nx.eulerian_circuit(euler_G))
    new_G = nx.MultiDiGraph(nx.create_empty_copy(euler_G))

    for start, target in circuit:
        edge_data = euler_G.get_edge_data(start, target)
        if edge_data is None:
            road_name = "unnamed"
        else:
            road_name = edge_data[0]['name']
        new_G.add_edge(start, target, name = road_name)

    nx.write_graphml(new_G, dest)

def custom_eulerize(G):
    # Create a copy of the graph to avoid modifying the original graph
    G = G.copy()
    # Find all nodes with odd degree
    odd_degree_nodes = [node for node, degree in G.degree() if degree % 2 == 1]
    # While there are nodes with odd degree
    while odd_degree_nodes:
        # Pick the first node with odd degree
        node1 = odd_degree_nodes.pop(0)
        # Try to find another node with odd degree that is connected to node1
        for node2 in odd_degree_nodes:
            if G.number_of_edges(node1, node2) > 0:
                # Add an edge between node1 and node2
                G.add_edge(node1, node2)
                # Remove node2 from the list of nodes with odd degree
                odd_degree_nodes.remove(node2)
                break
    return G