import json
from graph_api import Node

from . import Command as Command
from . import CommandLine as CLI

class SaveGraphCommand(Command.Command):
    def execute(self):
        try:
            with open(self.platform.file_path, "w") as f:
                json.dump(self.platform.graph.to_json_dict_hierarchy(), f, indent=2)
            return f"Graph saved successfully to {self.platform.file_path}."
        except Exception as e:
                return f"ERROR: Failed to save graph. {str(e)}"

    def parse_args(self, args):
        return CLI.CommandLine.parse_cli_args(args)