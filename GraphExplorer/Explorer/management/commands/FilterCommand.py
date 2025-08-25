from graph_api import Node

from . import Command as Command
from . import CommandLine as CLI
from filters import Filter, FilterFilter

class FilterCommand(Command.Command):
    def execute(self):
        new_filter = FilterFilter(self.args[0],self.args[1],self.args[2])
        self.platform.add_filter(new_filter)
        return f"Successfully added range filter"

