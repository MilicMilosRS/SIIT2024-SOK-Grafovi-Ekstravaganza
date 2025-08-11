import json
import networkx as nx
from graph_api import Node, Graph, GraphVisualizer
from datetime import datetime


class JSONDataSource:
    def __init__(self, json_file):
        self.json_file = json_file
        self.graph = nx.DiGraph()

    def parse_json(self):
        with open(self.json_file, 'r') as f:
            data = json.load(f)

        self.build_graph(data)
        return self.graph


    def build_graph(self, data, parent=None):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) or isinstance(value, list):
                    node_id = f"{key}_{id(value)}"
                    self.graph.add_node(node_id, label=key)
                    if parent:
                        self.graph.add_edge(parent, node_id)
                    self.build_graph(value, node_id)
                else:
                    node_id = f"{key}_{id(value)}"
                    self.graph.add_node(node_id, label=f"{key}: {value}")
                    if parent:
                        self.graph.add_edge(parent, node_id)
        elif isinstance(data, list):
            for item in data:
                self.build_graph(item, parent)

    def convert_to_api_graph(self):
        api_graph = Graph(directed=True)

        node_mapping = {}
        for node_id, data in self.graph.nodes(data=True):
            node = Node(id=len(node_mapping) + 1)
            for key, value in data.items():
                node.set_attribute(key, value)
            node_mapping[node_id] = node
            api_graph.add_vertex(node)

        for source, target in self.graph.edges():
            if source in node_mapping and target in node_mapping:
                api_graph.create_edge(node_mapping[source].get_id(), node_mapping[target].get_id())

        return api_graph
