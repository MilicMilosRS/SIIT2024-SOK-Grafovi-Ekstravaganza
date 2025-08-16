from graph_api import Graph, GraphVisualizer, Node
import json
import os

class SimpleVisualizer(GraphVisualizer):
    #Returns DOM for main visualization window
    def visualize_graph(self, g: Graph, selected_node: Node)->str:
        parsedNodes = []
        for node in g._vertices.values():
            parsedNodes.append(node._attributes)

        parsedLinks = []
        for source, targets in g._edges.items():
            for target in targets:
                parsedLinks.append({"source": source, "target": target})

        html = ""
        template_path = os.path.join(os.path.dirname(__file__))
        with open(template_path + "/templates/layout.html") as file:
            html = file.read()
        
        return html.replace("NODES", json.dumps(parsedNodes)).replace("LINKS", json.dumps(parsedLinks))
    
    def on_switched_to(self):
        pass
    
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

    def on_switched_from(self):
        pass

    def on_selection_changed(self, node):
        pass