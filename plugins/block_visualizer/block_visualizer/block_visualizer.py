from graph_api import Graph
import json
import os

class BlockVisualizer():
    #Returns DOM for main visualization window
    def visualize_graph(self, g: Graph)->str:
        parsedNodes = []
        for node in g._vertices.values():
            parsedNodes.append(node._attributes)

        parsedLinks = []
        for source, targets in g._edges.items():
            for target in targets:
                print(g._edges[source][target])
                parsedLinks.append({"source": source, "target": target, "attrs": g._edges[source][target]})

        html = ""
        template_path = os.path.join(os.path.dirname(__file__))
        with open(template_path + "/templates/layout.html") as file:
            html = file.read()
        
        return html.replace("NODES", json.dumps(parsedNodes)).replace("LINKS", json.dumps(parsedLinks)).replace("IS_DIRECTED", "true" if g._is_directed else "false")