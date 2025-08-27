from graph_api import Node

from . import Command as Command
from . import CommandLine as CLI

class CreateCommand(Command.Command):
    def execute(self):
        parsed = self.parse_args(self.args)

        if parsed["type"] == "node":
            if parsed["id"] in self.platform.graph._vertices:
                return "ERROR: That node already exists."
            node = Node(parsed["id"])
            for k, v in parsed["properties"].items():
                node.set_attribute(k, v)
            self.platform.add_vertex(node)
            return f"Node created successfully: {node.get_attributes()}"
        elif parsed["type"] == "edge":
            node1_id, node2_id = parsed["extra"][:2]
            self.platform.create_edge(node1_id, node2_id)
            return f"Edge created successfully {node1_id} -> {node2_id}"
        else:
            return "ERROR: Invalid create command."

    def parse_args(self, args):
        return CLI.CommandLine.parse_cli_args(None, args)
