from abc import ABC
from datasource_api import DataSourcePlugin
import json
import networkx as nx
from graph_api import Node, Graph, GraphVisualizer
from datetime import datetime

class JSONDataSource(DataSourcePlugin, ABC):
    def __init__(self, **kwargs):
        self.json_file = kwargs.get("file_path")
        self.graph = Graph(directed=True)

    def load_graph(self, **kwargs):
        with open(self.json_file, 'r') as f:
            data = json.load(f)

        self.build_graph(data)
        return self.graph
    
    def get_input_fields(self) -> list[str]:
        """
        Return list of fields the user must provide for this plugin.
        """
        return ["file_path"]

    def build_graph(self, data, parent_node: Node = None):
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict) or isinstance(value, list):
                    node = Node(id=str(key) + "_" + str(id(value)))
                    node.set_attribute("name", key)
                    self.graph.add_vertex(node)

                    if parent_node:
                        self.graph.create_edge(parent_node.get_id(), node.get_id())

                    self.build_graph(value, node)
                else:
                    node = Node(id=str(key) + "_" + str(id(value)))
                    node.set_attribute("name", value)
                    self.graph.add_vertex(node)

                    if parent_node:
                        self.graph.create_edge(parent_node.get_id(), node.get_id())

        elif isinstance(data, list):
            for item in data:
                self.build_graph(item, parent_node)
