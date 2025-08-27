import itertools
import json
from graph_api import Graph, Node

class TreeNode:
    _id_counter = itertools.count(1)

    def __init__(self, node, graph, parent=None):
        self.node = node
        self.graph = graph
        self._children = None
        self.expanded = False
        self.tree_id = f"T{next(TreeNode._id_counter)}"
        self.parent = parent

    def expand(self):
        if self._children is None:
            self._children = []
            outgoing, incoming = self.graph.get_connected_nodes(self.node.get_id())
            neighbors = set()
            neighbors.update(outgoing)
            neighbors.update(incoming)
            for child_node in neighbors:
                child_tree_node = TreeNode(child_node, self.graph, parent=self)
                self._children.append(child_tree_node)
        self.expanded = True

    def collapse(self):
        self.expanded = False

    def is_expandable(self):
        outgoing, incoming = self.graph.get_connected_nodes(self.node.get_id())
        return len(outgoing) + len(incoming) > 0

    def get_children(self):
        return self._children if self._children else []


def print_tree(node: TreeNode, prefix=""):
    marker = "+" if node.is_expandable() and not node.expanded else "-" if node.expanded else " "
    print(f"{prefix}{marker} {node.tree_id} (Node {node.node.get_id()})")
    if node.expanded:
        for child in node.get_children():
            print_tree(child, prefix + "    ")


class ForestView:
    def __init__(self, graph):
        self.graph = graph
        self.roots = []
        #Array of arrays, each array contains the id's of nodes that were expanded, so we know what line of nodes to expand on refresh
        self._expanded_paths = set()
        self._build_forest()

    def _restore_expansions(self):
        unbroken_paths = self._expanded_paths.copy()

        for path_ids in self._expanded_paths:
            current_nodes = self.roots
            for node_id in path_ids:
                # Find a node with this ID in current level
                match = next((n for n in current_nodes if n.node.get_id() == node_id), None)
                if not match:
                    unbroken_paths.remove(path_ids)
                    break  # Path broken, stop here
                match.expand()  # Ensure it's expanded before going deeper
                current_nodes = match.get_children()

        self._expanded_paths = unbroken_paths.copy()

    def _build_forest(self):
        self.roots = []
        visited = set()

        for node_id, node in self.graph._vertices.items():
            if node_id in visited:
                continue

            # Pick this node as root of a new tree
            root_node = TreeNode(node, self.graph)
            self.roots.append(root_node)

            # Mark all nodes in this connected component as visited
            to_visit = [node_id]
            while to_visit:
                current_id = to_visit.pop()
                if current_id in visited:
                    continue
                visited.add(current_id)
                outgoing, incoming = self.graph.get_connected_nodes(current_id)
                neighbors = outgoing + incoming
                for neighbor in neighbors:
                    if neighbor.get_id() not in visited:
                        to_visit.append(neighbor.get_id())
        
        self._restore_expansions()

    def graph_updated(self):
        self._build_forest()

    def print_forest(self):
        for root in self.roots:
            print_tree(root)

    def expand_node_by_tree_id(self, tree_id: str) -> bool:
        node = self._find_tree_node_by_id(tree_id, self.roots)
        if node:
            node.expand()
            path = self._find_tree_node_path(tree_id)
            id_path = list(map(lambda tree_node: tree_node.node.get_id(), path))
            self._expanded_paths.add(tuple(id_path))
            return True
        return False
    
    def _delete_expanded_path(self, tree_id: str):
        path = self._find_tree_node_path(tree_id)
        if path:
            id_path = list(map(lambda tree_node: tree_node.node.get_id(), path))
            paths_to_remove = []
            for path_ids in self._expanded_paths:
                if path_ids[:len(id_path)] == tuple(id_path):
                    paths_to_remove.append(path_ids)
            print(self._expanded_paths)
            print(id_path)
            print(paths_to_remove)
            for p in paths_to_remove:
                if tuple(p) in self._expanded_paths:
                    self._expanded_paths.remove(p)

    def collapse_node_by_tree_id(self, tree_id: str) -> bool:
        node = self._find_tree_node_by_id(tree_id, self.roots)
        if node:
            node.collapse()
            self._delete_expanded_path(tree_id)
            return True
        return False

    def _find_tree_node_by_id(self, tree_id: str, nodes: list):
        for tree_node in nodes:
            if tree_node.tree_id == tree_id:
                return tree_node
            if tree_node._children:
                found = self._find_tree_node_by_id(tree_id, tree_node._children)
                if found:
                    return found
        return None
    
    def _find_tree_node_path(self, tree_id: str):
        stack = [(root, [root]) for root in self.roots]

        while stack:
            current, path = stack.pop()
            if current.tree_id == tree_id:
                return path

            if current._children:
                for child in current._children:
                    stack.append((child, path + [child]))

        return None
    
    def convert_to_json(self):
        roots = []

        def tree_to_json(node: TreeNode):
            data = {}
            data["tree_id"] = node.tree_id
            data["node_id"] = node.node.get_id()
            data["attributes"] = node.node.get_attributes()
            data["is_expanded"] = node.expanded
            data["children"] = []
            if node.expanded:
                data["children"] = [tree_to_json(child) for child in node.get_children()]
            return data

        for root in self.roots:
            roots.append(tree_to_json(root))

        return roots
    
    def expand_path_to_node(self, node_id: str) -> bool:
        path = self._find_tree_node_path_by_node_id(node_id)
        if not path:
            return False

        id_path = list(map(lambda tree_node: tree_node.node.get_id(), path))

        for i in range(1, len(id_path)):
            self._expanded_paths.add(tuple(id_path[:i]))

        return True

    def _find_tree_node_path_by_node_id(self, node_id: str):
        stack = [(root, [root]) for root in self.roots]

        visited = set()

        while stack:
            current, path = stack.pop()
            if current.node.get_id() in visited:
                continue
            visited.add(current.node.get_id())

            if current.node.get_id() == node_id:
                return path

            if current._children is None:
                current.expand()

            for child in current.get_children():
                stack.append((child, path + [child]))

        return None
