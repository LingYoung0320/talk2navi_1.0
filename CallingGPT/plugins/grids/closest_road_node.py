import matplotlib
import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt
import math


def closest_road_node(Cu: str, De: str) -> str:
    """Find the closest ROAD node between two store nodes Cu and De, with an improved approach.

    Args:
        Cu: The label of the left store node.
        De: The label of the right store node.

    Returns:
        The label of the closest ROAD node, or None if no such node is found.
    """

    class GridGraph:
        def __init__(self, width, height):
            """Initialize a GridGraph with given width and height.

            Args:
                width (int): The width of the grid.
                height (int): The height of the grid.
            """
            self.width = width
            self.height = height
            self.graph = nx.grid_2d_graph(width, height)
            self.node_attributes = {}  # Dictionary to hold node attributes

            # Initialize all nodes as EMPTY with no label
            for node in self.graph.nodes:
                self.node_attributes[node] = ('EMPTY', '')  # ('type', 'label')

            nx.set_node_attributes(self.graph, 'EMPTY', 'type')
            nx.set_node_attributes(self.graph, '', 'label')

        def set_node_attribute(self, x, y, attribute, label=''):
            """Set the attribute and label for a specific node.

            Args:
                x (int): The x-coordinate of the node.
                y (int): The y-coordinate of the node.
                attribute (str): The type of the node (e.g., 'ROAD', 'STORE').
                label (str): The label of the node (e.g., store name).
            """
            if (x, y) in self.graph.nodes:
                self.node_attributes[(x, y)] = (attribute, label)
                nx.set_node_attributes(self.graph, {(x, y): attribute}, 'type')
                nx.set_node_attributes(self.graph, {(x, y): label}, 'label')

        def from_config_file(self, config_file):
            """Load grid and node attributes from a configuration file.

            Args:
                config_file (str): The path to the configuration file.
            """
            with open(config_file, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                # Read grid size
                size_line = lines[0].strip().split()
                new_width, new_height = int(size_line[0]), int(size_line[1])

                # Reinitialize the grid if dimensions have changed
                if (new_width, new_height) != (self.width, self.height):
                    self.width = new_width
                    self.height = new_height
                    self.graph = nx.grid_2d_graph(new_width, new_height)
                    self.node_attributes = {}
                    for node in self.graph.nodes:
                        self.node_attributes[node] = ('EMPTY', '')
                    nx.set_node_attributes(self.graph, 'EMPTY', 'type')
                    nx.set_node_attributes(self.graph, '', 'label')

                # Read node attributes
                for line in lines[1:]:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        x, y, attribute, label = int(parts[0]), int(parts[1]), parts[2], ' '.join(parts[3:])
                        self.set_node_attribute(x, y, attribute, label)

        def save_to_file(self, file_name):
            """Save node attributes to a CSV file.

            Args:
                file_name (str): The name of the output CSV file.
            """
            node_data = pd.DataFrame.from_dict(self.node_attributes, orient='index', columns=['type', 'label'])
            node_data.index.names = ['Node']
            node_data.to_csv(file_name)

        def get_node_by_label(self, label):
            """Find the coordinates of a node by its label.

            Args:
                label (str): The label of the node.

            Returns:
                tuple: The coordinates (x, y) of the node.

            Raises:
                ValueError: If no node with the specified label is found.
            """
            for node, attrs in self.node_attributes.items():
                if attrs[1] == label:
                    return node
            raise ValueError("No node with the specified label found")

        def get_road_node_by_label(self, label):
            """Find the nearest ROAD node to the specified store node label.

            Args:
                label (str): The label of the store node.

            Returns:
                tuple: The coordinates (x, y) of the nearest ROAD node, or None if no ROAD node is found.
            """
            store_node = self.get_node_by_label(label)
            # Check the four neighboring nodes for a ROAD node
            neighbors = [
                (store_node[0] + dx, store_node[1] + dy)
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
            ]
            for neighbor in neighbors:
                if neighbor in self.graph and self.node_attributes[neighbor][0] == 'ROAD':
                    return neighbor
            return None

    # Helper function to calculate the distance between two nodes
    def calculate_distance(node1, node2):
        """Calculate the distance between two nodes."""
        dx = abs(node1[0] - node2[0])
        dy = abs(node1[1] - node2[1])

        # Use 1 for vertical/horizontal distance, and 1.5 for diagonal
        if dx == 0 or dy == 0:
            return dx + dy  # Horizontal or vertical neighbors
        else:
            return 1.5 * (dx + dy)  # Diagonal neighbors

    # Create the grid and load configuration
    grid = GridGraph(15, 15)
    grid.from_config_file(r'D:\9py\CallingGPT\plugins\grids\HCH2.txt')

    # Get the coordinates of Cu and De
    start_node = grid.get_node_by_label(Cu)
    end_node = grid.get_node_by_label(De)

    # Get the neighbors of Cu and De
    start_neighbors = [
        (start_node[0] + dx, start_node[1] + dy)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    ]
    end_neighbors = [
        (end_node[0] + dx, end_node[1] + dy)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    ]

    # Find the intersection of neighbors of Cu and De
    common_neighbors = set(start_neighbors) & set(end_neighbors)

    # Check for the nearest ROAD node
    closest_node = None
    min_distance = float('inf')

    for neighbor in common_neighbors:
        if neighbor in grid.graph.nodes and grid.node_attributes[neighbor][0] == 'ROAD':
            dist_start = calculate_distance(start_node, neighbor)
            dist_end = calculate_distance(end_node, neighbor)
            total_distance = dist_start + dist_end

            if total_distance < min_distance:
                min_distance = total_distance
                closest_node = neighbor

    # Return the label of the closest ROAD node, or None if no such node is found
    if closest_node:
        return grid.node_attributes[closest_node][1]
    else:
        return None
