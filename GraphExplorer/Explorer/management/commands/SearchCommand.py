from graph_api import Node

from . import Command as Command
from . import CommandLine as CLI
from filters import SearchFilter

class SearchCommand(Command.Command):
    def execute(self):
        new_filter = SearchFilter(self.args[0])
        self.platform.add_filter(new_filter)
        return f"Successfully added search filter"

