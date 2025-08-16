from graph_api import Graph, GraphVisualizer, Node

class Platform():
    def __init__(self, graph: Graph = Graph(False), visualizer: GraphVisualizer = None):
        self.graph = graph
        self.visualizer = visualizer
    
    #Graph stuff
    def add_vertex(self, vertex: Node) -> bool:
        self.graph.add_vertex(vertex)
        self.visualizer.add_node(vertex)

    def edit_vertex(self, vertex: Node) -> bool:
        self.graph.edit_vertex(vertex)
        self.visualizer.edit_node(vertex)

    def create_vertex(self) -> Node:
        node = self.graph.create_vertex()
        self.visualizer.add_node(node)
        return node
    
    def delete_vertex(self, vertex: Node) -> None:
        self.graph.delete_vertex(vertex)
        self.visualizer.remove_node(vertex)
    
    def edit_edge(self, old_source: str, new_target: str) -> None:
        self.graph.edit_edge(old_source, new_target)
        self.visualizer.edit_link(old_source, new_target)

    def delete_edge(self, node1_id: str, node2_id: str) -> bool:
        self.graph.delete_edge(node1_id, node2_id)
        return self.graph.delete_edge(node1_id, node2_id)

    def create_edge(self, id1: str, id2: str) -> None:
        self.graph.create_edge(id1, id2)
        self.visualizer.add_link(id1, id2)


    #Visualizer stuff
    def set_visualizer(self, visualizer: GraphVisualizer) -> None:
        self.visualizer = visualizer

    def generate_main_view(self) -> str:
        return self.visualizer.visualize_graph(self.graph)