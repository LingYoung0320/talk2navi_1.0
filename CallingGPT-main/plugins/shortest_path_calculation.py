import matplotlib
import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt

def shortest_path_calculation(Cu: str, De: str) -> str:
    """Calculate shortest_path_calculation by Dij.

    Args:
        Cu: The current position, is also the starting position.
        De: The destination, is also the destination.

    Returns:
        a shortest path
    """

    class GridGraph:
        def __init__(self, width, height):
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
            if (x, y) in self.graph.nodes:
                self.node_attributes[(x, y)] = (attribute, label)
                nx.set_node_attributes(self.graph, {(x, y): attribute}, 'type')
                nx.set_node_attributes(self.graph, {(x, y): label}, 'label')

        def from_config_file(self, config_file):
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
            # Save node attributes to CSV
            node_data = pd.DataFrame.from_dict(self.node_attributes, orient='index', columns=['type', 'label'])
            node_data.index.names = ['Node']
            node_data.to_csv(file_name)

        def get_node_by_label(self, label):
            # Find the node coordinates by label
            for node, attrs in self.node_attributes.items():
                if attrs[1] == label:
                    return node
            raise ValueError("No node with the specified label found")

        def get_shortest_path(self, start_label, end_label):
            # Convert labels to coordinates
            start = self.get_node_by_label(start_label)
            end = self.get_node_by_label(end_label)

            # Create a subgraph with only ROAD nodes
            road_nodes = [node for node in self.graph.nodes if self.node_attributes[node][0] == 'ROAD']
            subgraph = self.graph.subgraph(road_nodes).copy()

            # Ensure start and end are in the ROAD nodes
            if start not in road_nodes or end not in road_nodes:
                raise ValueError("Start or end node is not of type ROAD")

            # Find the shortest path in the ROAD subgraph
            try:
                path = nx.shortest_path(subgraph, source=start, target=end, weight=None)
                return path
            except nx.NetworkXNoPath:
                return None

        def format_path(self, path):
            if not path:
                return ""

            formatted_path = []
            current_group = [self.node_attributes[path[0]][1]]
            same_x = same_y = True

            for current in path[1:]:
                previous = path[path.index(current) - 1]
                if current[0] != previous[0]:
                    same_x = False
                if current[1] != previous[1]:
                    same_y = False

                if not same_x and not same_y:
                    formatted_path.append("{" + ",".join(current_group) + "}")
                    current_group = [self.node_attributes[current][1]]
                    same_x = same_y = True
                else:
                    current_group.append(self.node_attributes[current][1])

            if current_group:
                formatted_path.append("{" + ",".join(current_group) + "}")

            return "".join(formatted_path)

        def format_path_with_labels(self, path):
            if not path:
                return ""

            formatted_path = []
            current_group = []
            same_x = same_y = True

            for current in path:
                # 如果当前节点是ROAD节点，尝试获取邻近的店铺名称
                if self.node_attributes[current][0] == 'ROAD':
                    nearest_store = self.get_nearest_store(self.node_attributes[current][1])
                    # 如果有邻近的店铺，使用店铺名称，否则跳过此节点
                    if nearest_store:
                        label = nearest_store
                    else:
                        continue  # 如果没有邻近的STORE，则跳过这个ROAD节点
                else:
                    label = self.node_attributes[current][1]

                # 若相邻坐标在同一水平或垂直方向，则继续归类
                if len(current_group) > 0:
                    previous = path[path.index(current) - 1]
                    if current[0] != previous[0]:
                        same_x = False
                    if current[1] != previous[1]:
                        same_y = False

                # 如果方向改变，则将当前组内容添加到格式化列表中，并重新开始新组
                if not same_x and not same_y:
                    # 去除连续重复的店铺名称
                    filtered_group = self.remove_consecutive_duplicates(current_group)
                    formatted_path.append("{" + ",".join(filtered_group) + "}")
                    current_group = [label]
                    same_x = same_y = True
                else:
                    current_group.append(label)

            # 将最后一组的内容添加到列表中
            if current_group:
                filtered_group = self.remove_consecutive_duplicates(current_group)
                formatted_path.append("{" + ",".join(filtered_group) + "}")

            return "".join(formatted_path)

        def remove_consecutive_duplicates(self, group):
            """
            去除列表中连续重复的元素，只保留一个
            """
            if not group:
                return group
            filtered_group = [group[0]]  # 初始化为第一个元素
            for item in group[1:]:
                if item != filtered_group[-1]:  # 仅在与前一个元素不同时添加
                    filtered_group.append(item)
            return filtered_group

        def get_nearest_store(self, road_label, radius=1):
            """
            Find the nearest STORE node within a specified radius around a given ROAD node.

            Parameters:
            road_label (str): The label of the ROAD node.
            radius (int): The maximum distance (in grid units) to look for STORE nodes.

            Returns:
            str: The label of the nearest STORE node found, or None if no STORE is found.
            """
            # Convert label to coordinates
            road_node = self.get_node_by_label(road_label)

            # Calculate the neighborhood range
            neighbors = [(road_node[0] + dx, road_node[1] + dy)
                         for dx in range(-radius, radius + 1)
                         for dy in range(-radius, radius + 1)
                         if (dx, dy) != (0, 0)]

            # Filter and find the first STORE node within the neighborhood
            for neighbor in neighbors:
                if neighbor in self.graph.nodes and self.node_attributes[neighbor][0] == 'STORE':
                    return self.node_attributes[neighbor][1]

            return None

        def get_shortest_path_with_stores(self, start_label, end_label):
            """
            Calculate the shortest path and replace each node with the nearest STORE if available.

            Parameters:
            start_label (str): Label of the starting node.
            end_label (str): Label of the ending node.

            Returns:
            list: List of labels of STORE nodes or None for each node in the path.
            """
            # Get shortest path first
            path = self.get_shortest_path(start_label, end_label)
            if path is None:
                return None

            # Replace ROAD nodes with nearest STOREs
            store_path = []
            for node in path:
                if self.node_attributes[node][0] == 'ROAD':
                    store_label = self.get_nearest_store(node)
                    store_path.append(store_label if store_label else None)
                else:
                    store_path.append(None)  # Append None for non-ROAD nodes or if no STORE is nearby

            return store_path

        def visualize(self):
            # Set up matplotlib to support Chinese characters if needed
            matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # Use a font that supports Chinese characters
            matplotlib.rcParams['axes.unicode_minus'] = False  # Ensure minus sign is displayed correctly
            pos = {(x, y): (y, -x) for x, y in self.graph.nodes()}

            filtered_nodes = [node for node in self.graph.nodes if self.node_attributes[node][0] != 'EMPTY']
            filtered_labels = {node: self.node_attributes[node][1] for node in filtered_nodes}

            nx.draw(self.graph, pos, nodelist=filtered_nodes, node_size=500, node_color="lightblue", font_size=10,
                    font_weight="bold", edge_color="gray")
            nx.draw_networkx_labels(self.graph, pos, labels=filtered_labels)

            plt.show()

    grid = GridGraph(15, 15)
    grid.from_config_file(r'D:\9py\CallingGPT-main\plugins\grids\HCH2.txt')
    start_label = Cu
    end_label = De
    path = grid.get_shortest_path(start_label, end_label)
    formatted_path = grid.format_path_with_labels(path)

    return formatted_path
