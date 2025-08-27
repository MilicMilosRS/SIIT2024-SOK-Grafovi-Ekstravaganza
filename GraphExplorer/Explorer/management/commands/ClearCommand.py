from graph_api import Graph
from . import Command as Command

class ClearCommand(Command.Command):
    def execute(self):
        if not self.args:
            directed = self.platform.graph._is_directed
            self.platform.graph = Graph(directed)
            self.platform.update_graph_view()
            return "Graph cleared successfully."

        elif self.args[0] == "filter":
            self.platform.graph._filters.clear()
            self.platform.update_graph_view()
            return "All filters cleared successfully."

        else:
            return "ERROR: Invalid clear command. Use 'clear' or 'clear filter'."
