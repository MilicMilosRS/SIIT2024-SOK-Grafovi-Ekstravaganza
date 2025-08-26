from abc import ABC
from datasource_api import DataSourcePlugin
from graph_api import Graph, Node
import xml.etree.ElementTree as ET
import uuid
from datetime import datetime

class XmlDataSourcePlugin(DataSourcePlugin, ABC):
    """
    XML DataSource Plugin parses XML files into Graphs.
    Supports acyclic and cyclic references using a configurable attribute.
    """
    def __init__(self, **kwargs):
        self.node_map = {}
        self.id_attr = kwargs.get("id_attr", "id")
        self.ref_attr = kwargs.get("ref_attr", "ref")
        self.directed = kwargs.get("directed", True)

    
    def load_graph(self, **kwargs) -> Graph:
        file_path = kwargs.get("file_path")
        if file_path is None:
            raise ValueError("file_path is required")

        self.id_attr = kwargs.get("id_attr", self.id_attr)
        self.ref_attr = kwargs.get("ref_attr", self.ref_attr)
        self.directed = kwargs.get("directed", self.directed)

        tree = ET.parse(file_path)
        root = tree.getroot()
        graph = Graph(directed=self.directed)

        self.node_map = {}
        self._parse_element(root, graph, parent_node=None)
        return graph
    
    def get_input_fields(self) -> list[str]:
        """
        Return list of fields the user must provide for this plugin.
        """
        return ["file_path"]
    
    def _convert_value(self, value: str):
        """Try to convert value to int, float, or datetime; fallback to string."""
        if value.isdigit():
            return int(value)
        try:
            f = float(value)
            return f
        except ValueError:
            pass
        try:
            dt = datetime.fromisoformat(value)
            return dt
        except ValueError:
            pass
        return value
    
    def _parse_element(self, element, graph: Graph, parent_node: Node = None):
        """
        Recursively parse XML element into Graph nodes and edges.
        - Creates nodes for complex elements (with children)
        - Maps leaf tags as attributes
        - Supports cyclic references via ref_attr
        """
        # check for reference
        ref_target = element.attrib.get(self.ref_attr)
        if ref_target and ref_target in self.node_map:
            target_node = self.node_map[ref_target]
            if parent_node:
                graph.create_edge(parent_node.get_id(), target_node.get_id())
            return target_node

        # element ima decu → kreiraj čvor
        if len(element) > 0:
            node_id = element.attrib.get(self.id_attr, f"{element.tag}_{uuid.uuid4().hex[:6]}")
            if node_id in self.node_map:
                node = self.node_map[node_id]
            else:
                node = Node(id=node_id)
                node.set_attribute("tag", element.tag)

                # kopiraj atribute
                for k, v in element.attrib.items():
                    if k not in (self.id_attr, self.ref_attr):
                        node.set_attribute(k, self._convert_value(v))

                graph.add_vertex(node)
                self.node_map[node_id] = node

            # poveži sa roditeljem
            if parent_node:
                graph.create_edge(parent_node.get_id(), node.get_id())

            # rekurzija
            for child in element:
                self._parse_element(child, graph, parent_node=node)

            return node

        # element bez dece → atribut roditelja
        else:
            if parent_node is not None and element.text and element.text.strip():
                parent_node.set_attribute(element.tag, self._convert_value(element.text.strip()))
            return parent_node
