from . import Command as Command

class HelpCommand(Command.Command):
    def execute(self):
        return [
            "1. create - Use to create a node\n"
            "2. edit - Use to edit an already existing node/edge\n"
            "3. delete - Use to delete node/edge\n"
            "4. save-graph - Use to save graph into database\n"
            "5. filter - Use to filter through nodes\n"
            "6. search - Use to search through graph\n"
            "7. clear - Use to clear entire graph\n"
            "8. clear-filter - Use to clear all filters from the graph\n"
            "9. help - Show this help message\n"
        ]