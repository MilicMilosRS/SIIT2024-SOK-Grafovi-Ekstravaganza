import json
import networkx as nx


class JSONDataSource:
    def __init__(self,json_file):
        self.json_file = json_file
        self.graph = nx.DiGraph()

    def parse_json(self):
        with open(self.json_file, 'r') as f:
            data = json.load(f)

        self.build_graph(data)
        return self.graph

    def save_graph(self, output_file='output_graph.gml'):
        nx.write_gml(self.graph, output_file)

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