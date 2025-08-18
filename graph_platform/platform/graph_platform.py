from collections.abc import Callable
import json
from graph_api import Graph, GraphVisualizer, Node
from TreeVIew.tree_view import TreeNode, ForestView

class Platform():
    def __init__(self, graph: Graph = Graph(False), visualizer: GraphVisualizer = None):
        self.graph_update_listeners = []
        self.graph = graph
        self.visualizer = visualizer
        self.forestView = ForestView(graph)
        self.selected_node = None

    #Graph update listener stuff
    def attach_update_listener(self, func: Callable[[None],None]):
        if func not in self.graph_update_listeners:
            self.graph_update_listeners.append(func)
    
    def detach_update_listener(self, func: Callable[[None],None]):
        if func in self.graph_update_listeners:
            self.graph_update_listeners.remove(func)

    def _graph_updated(self):
        self.forestView.graph_updated()
        for func in self.graph_update_listeners:
            func()

    #Graph stuff
    def add_vertex(self, vertex: Node) -> bool:
        if not self.graph.add_vertex(vertex):
            return False
        self.visualizer.add_node(vertex)
        self._graph_updated()
        return True

    def edit_vertex(self, vertex: Node) -> bool:
        self.graph.edit_vertex(vertex)
        self.visualizer.edit_node(vertex)
        self._graph_updated()

    def create_vertex(self) -> Node:
        node = self.graph.create_vertex()
        self.visualizer.add_node(node)
        self._graph_updated()
        return node
    
    def delete_vertex(self, vertex: Node) -> None:
        self.graph.delete_vertex(vertex)
        self.visualizer.remove_node(vertex)
        self._graph_updated()
    
    def edit_edge(self, old_source: str, new_target: str) -> None:
        self.graph.edit_edge(old_source, new_target)
        self.visualizer.edit_link(old_source, new_target)
        self._graph_updated()

    def delete_edge(self, node1_id: str, node2_id: str) -> bool:
        self.visualizer.remove_link(node1_id, node2_id)
        self._graph_updated()
        return self.graph.delete_edge(node1_id, node2_id)

    def create_edge(self, id1: str, id2: str) -> None:
        self.graph.create_edge(id1, id2)
        self.visualizer.add_link(id1, id2)
        self._graph_updated()

    #TreeView stuff
    def get_tree_view(self) -> str:
        data = {
            'selected_id': self.selected_node.get_id() if self.selected_node is not None else None,
            'treeview': self.forestView.convert_to_json()
                }
        return data
    
    def expand_tree_view(self, tree_id: str):
        self.forestView.expand_node_by_tree_id(tree_id)
        self._graph_updated()

    def collapse_tree_view(self, tree_id: str):
        self.forestView.collapse_node_by_tree_id(tree_id)
        self._graph_updated()


    #Visualizer stuff
    def set_visualizer(self, visualizer: GraphVisualizer) -> None:
        if self.visualizer is not None:
            self.visualizer.on_switched_from()
        self.visualizer = visualizer
        self.visualizer.on_switched_to()

    def generate_main_view(self) -> str:
        ret = self.visualizer.visualize_graph(self.graph, self.selected_node)
        self.visualizer.on_selection_changed(self.selected_node)
        return ret
    
    #Selection stuff
    def select_node(self, node_id: str) -> Node:
        node = self.graph._vertices.get(node_id)
        if node is None:
            return None
        
        self.selected_node = node
        self.forestView.expand_path_to_node(node_id)
        self._graph_updated()
        self.visualizer.on_selection_changed(node)
        return self.selected_node
    
    def deselect_node(self):
        self.selected_node = None
        self._graph_updated()
        self.visualizer.on_selection_changed(None)