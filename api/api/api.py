from datetime import datetime
from abc import ABC, abstractmethod

class Node(object):
    def __init__(self, id: int) -> None:
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
    
    def get_id(self) -> int:
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

    def create_vertex(self) -> Node:
        i = 1
        while i in self._vertices:
            i += 1
        new_vertex = Node(i)
        self.add_vertex(new_vertex)
        return new_vertex
    
    def _add_edge(self, id1: int, id2: int) -> None:
        if id1 not in self._edges:
            self._edges[id1] = []
        if id2 not in self._edges[id1]:
            self._edges[id1].append(id2)


    def create_edge(self, id1: int, id2: int) -> None:
        self._add_edge(id1, id2)
        if not self._is_directed:
            self._add_edge(id2, id1)
        
class GraphVisualizer(ABC):
    #Returns a string representing an HTML DOM visualization of the provided graph
    def visualize_graph(self, g: Graph)->str:
        pass