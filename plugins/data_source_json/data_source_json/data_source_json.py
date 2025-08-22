import json
import networkx as nx
from graph_api import Node, Graph, GraphVisualizer
from datetime import datetime

class JSONDataSource:
    def __init__(self, json_file):
        self.json_file = json_file
        self.graph = Graph(directed=True)

    def parse_json(self):
        with open(self.json_file, 'r') as f:
            data = json.load(f)

        self.build_graph(data)
        return self.graph

    def build_graph(self, data, parent_node: Node = None):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) or isinstance(value, list):
                    # Create a node for this key
                    node = Node(id=str(key) + "_" + str(id(value)))
                    node.set_attribute("name", key)
                    self.graph.add_vertex(node)

                    if parent_node:
                        self.graph.create_edge(parent_node.get_id(), node.get_id())

                    # Recursively build child nodes
                    self.build_graph(value, node)
                else:
                    # Leaf node: store just the value
                    node = Node(id=str(key) + "_" + str(id(value)))
                    node.set_attribute("name", value)
                    self.graph.add_vertex(node)

                    if parent_node:
                        self.graph.create_edge(parent_node.get_id(), node.get_id())

        elif isinstance(data, list):
            for item in data:
                self.build_graph(item, parent_node)
