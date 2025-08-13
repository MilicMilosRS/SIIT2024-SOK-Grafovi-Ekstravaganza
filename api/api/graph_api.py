from datetime import datetime
from abc import ABC, abstractmethod

class Node(object):
    def __init__(self, id: str) -> None:
        self._attributes = {'id': id}

    def set_attribute(self, attr_name: str, value) -> None:
        if attr_name == 'id':
            raise ValueError("The id attribute is reserved.")
        
        if not isinstance(value, (str, int, float, datetime)):
            raise TypeError("Value is not a supported type")

        self._attributes[attr_name] = value

    def remove_attribute(self, attr_name: str) -> bool:
        if attr_name == 'id':
            raise ValueError("The id attribute is reserved.")
        
        if attr_name not in self._attributes:
            return False
        
        del self._attributes[attr_name]
        return True
        
    def get_attributes(self) -> dict:
        return self._attributes
    
    def get_id(self) -> str:
        return self._attributes['id']
    
class Graph(object):
    def __init__(self, directed: bool) -> None:
        self._vertices = {}
        self._edges = {}
        self._is_directed = directed

    def add_vertex(self, vertex: Node) -> bool:
        if vertex.get_id() in self._vertices:
            return False
        
        self._vertices[vertex.get_id()] = vertex

    def edit_vertex(self, vertex: Node) -> bool:
        vid = vertex.get_id()
        if vid not in self._vertices:
            return ("ERROR: That node/edge doesn't exist in the graph.")
    
        existing_node = self._vertices[vid]
        for key,value in vertex.get_attributes().items():
            if key != 'id':
                existing_node.set_attribute(key, value)
        return True

    def create_vertex(self) -> Node:
        i = 1
        while i in self._vertices:
            i += 1
        new_vertex = Node(i)
        self.add_vertex(new_vertex)
        return new_vertex
    
    def delete_vertex(self, vertex: Node) -> None:
        vid = vertex.get_id()
        if vid not in self._vertices:
            return False
        
        if vid in self._edges:
            del self._edges[vid]  # remove outgoing edges
        # Remove edge from other edges adjacent
        for src, targets in self._edges.items():
            if vid in targets:
                targets.remove(vid)

        # And then remove edge itself
        del self._vertices[vid]
        return True


    
    def _add_edge(self, id1: int, id2: int) -> None:
        if id1 not in self._vertices or id2 not in self._vertices:
            return

        if id1 not in self._edges:
            self._edges[id1] = []
        if id2 not in self._edges[id1]:
            self._edges[id1].append(id2)
    
    def edit_edge(self, old_source: str, new_target: str) -> None:
        # See if both nodes exist
        if old_source not in self._vertices or new_target not in self._vertices:
            return "ERROR: One or both nodes do not exist."

        # Make sure there is an edge or we won't have an edge to edit xd
        if old_source not in self._edges or not self._edges[old_source]:
            return "ERROR: That source node has no edges to edit."

        # First we remove old edge.
        old_target = self._edges[old_source][0]
        if old_target in self._edges[old_source]:
            self._edges[old_source].remove(old_target)

        # If undirected, remove reverse connection safely
        if not self._is_directed:
            if old_target not in self._edges:
                self._edges[old_target] = []
            if old_source in self._edges[old_target]:
                self._edges[old_target].remove(old_source)

        # Then we Add new connection
        if old_source not in self._edges:
            self._edges[old_source] = []
        if new_target not in self._edges[old_source]:
            self._edges[old_source].append(new_target)

        # If undirected, add reverse connection safely
        if not self._is_directed:
            if new_target not in self._edges:
                self._edges[new_target] = []
            if old_source not in self._edges[new_target]:
                self._edges[new_target].append(old_source)

        return f"Edge updated: {old_source} -> {new_target} (was {old_source} -> {old_target})"

    def delete_edge(self, node1_id: str, node2_id: str) -> bool:
       #If nodes ids are located in edges, we remove the edge from 1 node to another
        if node1_id in self._edges and node2_id in self._edges[node1_id]:
            self._edges[node1_id].remove(node2_id)
            # If undirected, remove reverse link too
            if not self._is_directed and node2_id in self._edges and node1_id in self._edges[node2_id]:
                self._edges[node2_id].remove(node1_id)
            return True
        return False

    def create_edge(self, id1: int, id2: int) -> None:
        self._add_edge(id1, id2)
        if not self._is_directed:
            self._add_edge(id2, id1)
        
class GraphVisualizer(ABC):
    #Returns a string representing an HTML DOM visualization of the provided graph
    def visualize_graph(self, g: Graph)->str:
        pass