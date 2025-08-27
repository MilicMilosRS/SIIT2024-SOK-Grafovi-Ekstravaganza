from collections.abc import Callable
import json
from graph_api import Graph, GraphVisualizer, Node
from TreeVIew.tree_view import TreeNode, ForestView
from filters import Filter

class Platform():
    _instance = None  # store the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # first time: create instance
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, graph: Graph = Graph(False), visualizer: GraphVisualizer = None, file_path=None):
        # prevent reinitialization on every call
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

        self.file_path = file_path
        self.graph_update_listeners = []
        self.graph = graph
        self._filtered_graph = graph
        self.visualizer = visualizer
        self.forestView = ForestView(graph)
        self.selected_node = None

    #graph update listener
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
    
    #Returns a json with all nodes, edges, and their attributes
    def get_graph_data(self):
        parsedNodes = []
        for node in self._filtered_graph._vertices.values():
            parsedNodes.append({"attributes": node._attributes})

        parsedLinks = []
        for source, targets in self._filtered_graph._edges.items():
            for target in targets:
                parsedLinks.append({"source": source, "target": target, "attrs": self._filtered_graph._edges[source][target]})
        
        return {'nodes': parsedNodes, 'links': parsedLinks}

    def add_vertex(self, vertex: Node) -> bool:
        if not self.graph.add_vertex(vertex):
            return False
        self.visualizer.add_node(vertex)
        self.update_graph_view()
        return True

    def edit_vertex(self, vertex: Node) -> bool:
        if not self.graph.edit_vertex(vertex):
            return False
        self.visualizer.edit_node(vertex)
        self.update_graph_view()
        return True

    def create_vertex(self) -> Node:
        node = self.graph.create_vertex()
        self.visualizer.add_node(node)
        self.update_graph_view()
        return node
    
    def delete_vertex(self, vertex: Node) -> None:
        self.graph.delete_vertex(vertex)
        self.visualizer.remove_node(vertex)
        self.update_graph_view()
    
    def edit_edge(self, old_source: str, new_target: str, **attrs) -> None:
        self.graph.edit_edge(old_source, new_target)
        self.visualizer.edit_link(old_source, new_target)
        self.update_graph_view()

    def delete_edge(self, node1_id: str, node2_id: str) -> bool:
        ret = self.graph.delete_edge(node1_id, node2_id)
        self.update_graph_view()
        return ret

    def create_edge(self, id1: str, id2: str, **attrs) -> None:
        self.graph.create_edge(id1, id2, **attrs)
        self.visualizer.add_link(id1, id2)
        self.update_graph_view()

    #TreeView stuff
    def get_tree_view(self) -> str:
        data = {
            'selected_id': self.selected_node.get_id() if self.selected_node is not None else None,
            'treeview': self.forestView.convert_to_json()
                }
        return data
    
    def expand_tree_view(self, tree_id: str):
        print("Tree id " + tree_id)
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

    #Filter stuff

    def update_graph_view(self):
        self._create_filtered_graph()
        self.forestView = ForestView(self._filtered_graph)
        self._graph_updated()
        self.visualizer.revisualize_graph(self._filtered_graph)

    def get_filters(self):
        return self.graph._filters

    def add_filter(self, filter: Filter):
        self.graph.add_filter(filter)
        self.update_graph_view()

    def remove_filter(self, index: int):
        self.graph.remove_filter(index)
        self.update_graph_view()
    
    def _create_filtered_graph(self):
        self._filtered_graph = Graph(self.graph._is_directed)

        for node_id, attrs in self.graph._vertices.items():
            node = Node(node_id)
            for key, value in attrs._attributes.items():
                if (key == 'id'):
                    continue
                node.set_attribute(key, value)
            
            self._filtered_graph.add_vertex(node)

        print(self.graph._filters)

        for filter in self.graph._filters:
            self._filtered_graph._vertices = filter.apply(self._filtered_graph._vertices)
        
        node_mapping = {}
        for node_id, node in self.graph._vertices.items():
            node_mapping[node_id] = node

        for source, targets in self.graph._edges.items():
            if source in node_mapping:
                for target in targets:
                    if target in node_mapping:
                        self._filtered_graph.create_edge(node_mapping[source].get_id(), node_mapping[target].get_id(), **self.graph._edges[source][target])


    def set_graph(self, new_graph: Graph):
        """
        Replace the current graph with a new one.
        Updates filtered_graph, forestView, visualizer, and notifies listeners.
        """
        self.graph = new_graph
        self._filtered_graph = new_graph
        self.forestView = ForestView(new_graph)
        
        if self.visualizer:
            self.visualizer.revisualize_graph(new_graph)
        
        self.selected_node = None
        self.update_graph_view()