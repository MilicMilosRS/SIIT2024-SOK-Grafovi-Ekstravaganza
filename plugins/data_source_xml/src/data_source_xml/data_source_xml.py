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
        self.pending_refs = []   #(parent_id, ref_target)
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
        self.pending_refs = []
        self._parse_element(root, graph, parent_node=None)

        #resolve references after all nodes are parsed
        for parent_id, ref_target in self.pending_refs:
            if ref_target in self.node_map:
                graph.create_edge(parent_id, self.node_map[ref_target].get_id())
            else:
                print(f"Warning: unresolved reference '{ref_target}'")

        return graph

    def get_input_fields(self) -> list[str]:
        return ["file_path"]

    def _convert_value(self, value: str):
        """Try to convert value to int, float, or datetime; fallback to string."""
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            pass
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
        return value

    def _parse_element(self, element, graph: Graph, parent_node: Node = None):
        """Recursively parse XML element into Graph nodes and edges."""
        #check for reference
        ref_target = element.attrib.get(self.ref_attr)
        if ref_target:
            if ref_target in self.node_map:
                target_node = self.node_map[ref_target]
                if parent_node:
                    graph.create_edge(parent_node.get_id(), target_node.get_id())
                return target_node
            else:
                if parent_node:
                    self.pending_refs.append((parent_node.get_id(), ref_target))
                return None

        #element has children - make a node
        if len(element) > 0:
            node_id = element.attrib.get(self.id_attr, f"{element.tag}_{uuid.uuid4().hex[:6]}")
            if node_id in self.node_map:
                node = self.node_map[node_id]
            else:
                node = Node(id=node_id)
                node.set_attribute("tag", element.tag)

                #copy attributes except id/ref
                for k, v in element.attrib.items():
                    if k not in (self.id_attr, self.ref_attr):
                        node.set_attribute(k, self._convert_value(v))

                graph.add_vertex(node)
                self.node_map[node_id] = node

            if parent_node:
                graph.create_edge(parent_node.get_id(), node.get_id())

            #recursion
            for child in element:
                self._parse_element(child, graph, parent_node=node)

            return node

        #element has no children - treat as attribute
        else:
            if parent_node is not None and element.text and element.text.strip():
                parent_node.set_attribute(element.tag, self._convert_value(element.text.strip()))
            return parent_node