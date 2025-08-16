from graph_api import Node

from . import Command as Command
from . import CommandLine as CLI

class DeleteCommand(Command.Command):
    def execute(self):
        parsed = self.parse_args(self.args)

        if parsed["type"] == "node":
            node_id = parsed["id"]
            if self.platform.delete_vertex(Node(node_id)):
                return f"Node {node_id} deleted successfully."
            else:
                return f"ERROR: Node {node_id} doesn't exist."
        elif parsed["type"] == "edge":
            node1_id, node2_id = parsed["extra"][:2]
            if self.platform.delete_edge(node1_id, node2_id):
                return f"Edge {node1_id} -> {node2_id} deleted successfully."
            else:
                return f"ERROR: Edge {node1_id} -> {node2_id} doesn't exist."
        else:
            return "ERROR: Invalid delete command."

    def parse_args(self, args):
        return CLI.CommandLine.parse_cli_args(None, args)