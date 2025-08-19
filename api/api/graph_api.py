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
        #Dict of dicts
        #Example: node1_id: {node2_id: {EDGE ATTRIBUTES}, node3_id: {EDGE ATTRIBUTES}}
        self._edges = {}
        self._is_directed = directed
        self._filters = []
        self._filtered_vertices = {}
        self._filtered_edges = {}

    def add_vertex(self, vertex: Node) -> bool:
        if vertex.get_id() in self._vertices:
            return False
        
        self._vertices[vertex.get_id()] = vertex
        return True

    def edit_vertex(self, vertex: Node) -> bool:
        vid = vertex.get_id()
        if vid not in self._vertices:
            return False
    
        existing_node = self._vertices[vid]
        existing_node._attributes.clear()
        existing_node._attributes["id"] = vid
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
                del targets[vid]
        # And then remove edge itself
        del self._vertices[vid]
        return True

    def _add_edge(self, id1: str, id2: str, **attrs) -> None:
        if id1 not in self._vertices or id2 not in self._vertices:
            return

        if id1 not in self._edges:
            self._edges[id1] = {}
        if id2 not in self._edges[id1]:
            self._edges[id1][id2] = attrs
    
    def _edit_edge(self, id1: str, id2: str, **attrs) -> None:
        if id1 not in self._edges:
            return
        if id2 not in self._edges[id1]:
            return
        self._edges[id1][id2] = attrs

    def delete_edge(self, node1_id: str, node2_id: str) -> bool:
       #If nodes ids are located in edges, we remove the edge from 1 node to another
        if node1_id in self._edges and node2_id in self._edges[node1_id]:
            self._edges[node1_id].pop(node2_id,None)
            # If undirected, remove reverse link too
            if not self._is_directed and node2_id in self._edges and node1_id in self._edges[node2_id]:
              self._edges[node2_id].pop(node1_id, None)
            return True
        return False

    def create_edge(self, id1: str, id2: str, **attrs) -> None:
        self._add_edge(id1, id2, **attrs)
        if not self._is_directed:
            self._add_edge(id2, id1, **attrs)

    def edit_edge(self, old_source: str, new_target: str, **attrs) -> None:
        for target in list(self._edges.get(old_source, {})):
            old_attrs = self._edges[old_source].pop(target)
            self._edges[old_source][new_target] = {**old_attrs, **attrs}
            break

    
    def to_json_dict_hierarchy(self):
        data = {"community": {"members": []}}
        for node_id, node in self._vertices.items():
            attrs = node.get_attributes()
            if attrs.get("type") == "member":
                member_dict = {k: v for k, v in attrs.items() if k != "id"}
                # find friends
                friends = []
                for target_id in self._edges.get(node_id, []):
                    friend_node = self._vertices[target_id]
                    friend_attrs = friend_node.get_attributes()
                    friends.append({k: v for k, v in friend_attrs.items() if k != "id"})
                member_dict["friends"] = friends
                data["community"]["members"].append(member_dict)
        return data
    
    #Returns a tuple.
    #First element is outgoing connections.
    #Second element is incoming connections.
    def get_connected_nodes(self, node_id: str):
        outgoing = []
        incoming = []

        #Loop through outgoing connections and take the nodes
        if node_id in self._edges:
            for outgoing_node_id in self._edges[node_id].keys():
                outgoing.append(self._vertices[outgoing_node_id])

        #Loop through all connections and take the incoming nodes
        for src_id in self._edges.keys():
            for trgt_id in self._edges[src_id].keys():
                if trgt_id == node_id:
                    incoming.append(self._vertices[src_id])
        
        return (outgoing, incoming)
    
    def add_filter(self, filter):
        self._filters.append(filter)

    def remove_filter(self, index: int):
        index = int(index)
        if (index < 0 or index >= len(self._filters)):
            return False
        self._filters.pop(index)
        return True

    def get_filters(self):
        return self._filters
        

class GraphVisualizer(ABC):
    #Returns a string representing an HTML DOM visualization of the provided graph
    @abstractmethod
    def visualize_graph(self, g: Graph, selected_node: Node)->str:
        pass

    @abstractmethod
    def add_node(self, node: Node):
        pass

    @abstractmethod
    def edit_node(self, node: Node):
        pass

    @abstractmethod
    def remove_node(self, node: Node):
        pass

    @abstractmethod
    def add_link(self, id_source: str, id_target: str, **attrs):
        pass

    @abstractmethod
    def edit_link(self, id_source: str, id_target: str, **attrs):
        pass

    @abstractmethod
    def remove_link(self, id_source: str, id_target: str):
        pass

    #When the visualizer being used is switched from this to something else
    @abstractmethod
    def on_switched_from(self):
        pass

    @abstractmethod
    def on_switched_to(self):
        pass

    @abstractmethod
    def on_selection_changed(self, node: Node):
        pass

    @abstractmethod
    def revisualize_graph(self, graph: Graph):
        pass