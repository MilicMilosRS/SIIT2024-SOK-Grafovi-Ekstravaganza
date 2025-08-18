from collections.abc import Callable
import json
from graph_api import Graph, GraphVisualizer, Node
from TreeVIew.tree_view import TreeNode, ForestView
from operator import eq, ne, gt, lt, ge, le

class Platform():
    def __init__(self, graph: Graph = Graph(False), visualizer: GraphVisualizer = None):
        self.graph_update_listeners = []
        self.graph = graph
        self._filtered_graph = graph
        self.visualizer = visualizer
        self.forestView = ForestView(graph)
        self.selected_node = None
        self.operands = {
            "eq": eq,
            "ne": ne,
            "gt": gt,
            "lt": lt,
            "ge": ge,
            "le": le,
        }

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
        self.graph.add_vertex(vertex)
        self.visualizer.add_node(vertex)
        self._graph_updated()

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
        self.delete_vertex(vertex)
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
        self._graph_updated()
        self.visualizer.on_selection_changed(node)
        return self.selected_node
    
    def deselect_node(self):
        self.selected_node = None
        self._graph_updated()
        self.visualizer.on_selection_changed(None)

    #Filter stuff
    def add_filter(self, filter):
        self.graph.add_filter(filter)
        self._graph_updated()
        self._create_filtered_graph()
        return self.visualizer.visualize_graph(self._filtered_graph, self.selected_node)

    def remove_filter(self, index: int):
        self.graph.remove_filter(index)
        self._graph_updated()
        self._create_filtered_graph()
        return self.visualizer.visualize_graph(self._filtered_graph, self.selected_node)
    
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
            if filter.type == "search":
                self._filtered_graph._vertices = {
                    key: node for key, node in self._filtered_graph._vertices.items()
                    if any(filter.attribute in str(k) or filter.attribute in str(v)
                        for k, v in node._attributes.items()) }           
            else:
                attr = filter.attribute
                operand = self.operands[filter.type]
                value = filter.value
                self._filtered_graph._vertices = [
                    node for node in self._filtered_graph._vertices
                    if attr in node and operand(node[attr], value)
                ]
            
        node_mapping = {}
        for node_id, node in self.graph._vertices.items():
            node_mapping[node_id] = node

        for source, targets in self.graph._edges.items():
            if source in node_mapping:
                for target in targets:
                    if target in node_mapping:
                        self._filtered_graph.create_edge(node_mapping[source].get_id(), node_mapping[target].get_id())