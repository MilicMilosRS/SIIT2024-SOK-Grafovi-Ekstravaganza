import asyncio
import os
import threading
import websockets
import json
from graph_api import Graph, Node, GraphVisualizer

class BlockVisualizer(GraphVisualizer):
    def __init__(self):
        pass

    def on_switched_to(self):
        pass

    def on_switched_from(self):
        pass

    def visualize_graph(self, g: Graph, selected_node: Node) -> str:
        parsedNodes = []
        for node in g._vertices.values():
            parsedNodes.append({"attributes": node._attributes})

        parsedLinks = []
        for source, targets in g._edges.items():
            for target in targets:
                parsedLinks.append({"source": source, "target": target, "attrs": g._edges[source][target]})

        template_path = os.path.join(os.path.dirname(__file__))
        with open(template_path + "/templates/layout.html") as file:
            html = file.read()

        html = html.replace("NODES", json.dumps(parsedNodes))
        html = html.replace("LINKS", json.dumps(parsedLinks))
        html = html.replace("IS_DIRECTED", "true" if g._is_directed else "false")
        html = html.replace("SELECTED_ID", '"' + str(selected_node.get_id()) + '"' if selected_node is not None else "null")

        return html

    def add_node(self, node: Node):
        pass

    def edit_node(self, node: Node):
        pass

    def remove_node(self, node: Node):
        pass

    def add_link(self, id_source: str, id_target: str, **attrs):
        pass

    def edit_link(self, id_source: str, id_target: str, **attrs):
        pass

    def remove_link(self, id_source: str, id_target: str):
        pass

    def on_selection_changed(self, node):
        pass

    #Visualize the graph dynamically, without returning a whole new html page
    def revisualize_graph(self, graph: Graph):
        pass