import networkx as nx
import statistics
import sys
import math
import random as rnd
import matplotlib.pyplot as plt

def generate_random_edges(n_nodes, edges):
    # Generate Edge's vertices
    firstVert = rnd.randint(0, n_nodes)

    secondVert = rnd.randint(0, n_nodes)
    
    edge = (firstVert, secondVert)

    # Check if it is valid
    if firstVert == secondVert or (firstVert, secondVert) in edges:
        edge =  generate_random_edges(n_nodes, edges)
    
    return edge

def generate_graph(n_nodes):
    G = nx.Graph()

    # Add nodes to the graph
    for x in range(n_nodes):
        G.add_node(x)

    edges_generated = 0

    # While the graph is not connected create new edges
    while not nx.is_connected(G):
        edge = generate_random_edges(n_nodes, G.edges)
        G.add_edge(edge[0], edge[1])
        edges_generated += 1

    return edges_generated

def calculate_median(n_nodes):
    edges_generated_list = []
    
    # Create median of the edges generated to create a connected graph
    for i in range(100):
        edges_generated_list.append(generate_graph(n_nodes))

    return statistics.median(edges_generated_list)

def get_median_values(node_list):
    median_values = []

    # Calculate all the median values for nodes in node_list
    for i in node_list:
        print(i)
        median_values.append(calculate_median(i))

    return median_values

# Script is run "connectedComponents.py n_intervals power_to"
arguments = sys.argv[1:]

n_intervals = int(arguments[0])

nodes_list = []

# Generate Node List
if arguments[0] == '1':
    for i in range(1, n_intervals + 1):
        nodes_list.append(math.pow(2, i))
else:
    for i in range(1, n_intervals + 1):
        nodes_list.append(i*10)


fig, ax = plt.subplots()  # Create a figure containing a single axes.
print(nodes_list)
ax.plot(nodes_list, get_median_values(nodes_list))  # Plot some data on the axes.
plt.show()

