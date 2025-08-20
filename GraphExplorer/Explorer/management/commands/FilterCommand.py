from graph_api import Node

from . import Command as Command
from . import CommandLine as CLI

class FilterCommand(Command.Command):
    def execute(self):
        command: str = self.args[0] + " " + self.args[1] + " " + self.args[2]
        command = command.strip()
        new_filter = Filter(command)
        self.platform.add_filter(new_filter)
        return f"Successfully added range filter"



class Filter:
    def __init__(self, command: str):
        tokens = command.split(" ")
        if len(tokens) != 3 and len(tokens) != 1:
            self.valid = False
        else:
            self.valid = True

        if self.valid and len(tokens) == 1:
            self.attribute = tokens[0]
            self.type = "search"
            self.value = ""
        elif self.valid and len(tokens) == 3:
            self.attribute = tokens[0]
            op = tokens[1]
            match op:
                case ">":
                    self.type = 'gt'
                case "<":
                    self.type = 'lt'
                case ">=":
                    self.type = 'ge'
                case "<=":
                    self.type = 'le'
                case "==":
                    self.type = 'eq'
                case "!=":
                    self.type = 'ne'
                case _:
                    self.valid = False
                    self.type = 'invalid'
            self.value = tokens[2]

    def __str__(self):
        return f"value: {self.value}, type: {self.type}, attribute: {self.attribute}"

    def __getitem__(self, key):
        return getattr(self, key)

    def serialize(self):
        return {"value": self.value, "type": self.type, "attribute": self.attribute}