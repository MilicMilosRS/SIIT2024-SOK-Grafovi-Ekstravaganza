import json
from django.core.management.base import BaseCommand, CommandError
import shlex

from graph_platform import Platform
from graph_api import Node
 
class CommandLine():
    def __init__(self, platform: Platform, file_path: str = None):
        self.platform = platform
        self.file_path = file_path
        pass
    
    def process_command(self, command):
        tokens = shlex.split(command)
        if not tokens:
            return ""
        
        cmd = tokens[0].lower()

        if cmd == "create":
            return self.handle_create(tokens[1:])
        elif cmd == "edit":
            return self.handle_edit(tokens[1:])
        elif cmd == "delete":
            return self.handle_delete(tokens[1:])
        elif cmd == "filter":
            return self.handle_filter(tokens[1:])
        elif cmd == "search":
            return self.handle_search(tokens[1:])
        elif cmd == "clear":
            return self.handle_clear(tokens[1:])
        elif cmd == "save-graph":
            return self.handle_save(tokens[1:])
        else:
            return (f"WARNING: Unknown command: {cmd}")

    def handle_create(self, arg):
        parsed = self.parse_cli_args(arg)
        if parsed["type"] == "node":
            if parsed["id"] in self.platform.graph._vertices:
                return ("ERROR: That node already exists.")
            node = Node(parsed["id"])
            for k,v in parsed["properties"].items():
                node.set_attribute(k,v)
            self.platform.add_vertex(node)
            return f"Node created successfully: {node.get_attributes()}"
        elif parsed["type"] == "edge":
            node1_id,node2_id = parsed["extra"][:2]
            self.platform.create_edge(node1_id, node2_id)
            return f"Edge created successfully (id={parsed['id']}) {node1_id} -> {node2_id} with props {parsed['properties']}"
        else:
            return ("ERROR: Invalid create command.")

    def handle_edit(self,arg):
        parsed = self.parse_cli_args(arg)
        
        if parsed["type"] == "node":
            if parsed["id"] not in self.platform.graph._vertices:
                return ("ERROR: That node doesn't exist in the graph.")
            node = Node(parsed["id"])
            for k,v in parsed["properties"].items():
                node.set_attribute(k,v)
            self.platform.edit_vertex(node)
            return f"Node edited successfully: {node.get_attributes()}"
        elif parsed["type"] == "edge":
            node1_id, node2_id = parsed["extra"][:2]
            self.platform.edit_edge(node1_id, node2_id)
            return f"Edge edited successfully {node1_id} -> {node2_id} with props {parsed['properties']}"
        else:
            return ("ERROR: Invalid create command.")
        
    def handle_delete(self, arg):
        parsed = self.parse_cli_args(arg)

        if parsed["type"] == "node":
            node_id = parsed["id"]
            if self.platform.delete_vertex(Node(node_id)):
                return f"Node {node_id} deleted successfully."
            else:
                return f"ERROR: Node {node_id} doesn't exist."

        elif parsed["type"] == "edge":
            node1_id, node2_id = parsed["extra"][:2]
            deleted = self.platform.delete_edge(node1_id, node2_id)
            if deleted:
                return f"Edge {node1_id} -> {node2_id} deleted successfully."
            else:
                return f"ERROR: Edge {node1_id} -> {node2_id} doesn't exist."

        else:
            return "ERROR: Invalid delete command."

    def handle_filter(self,arg):
        command: str = arg[0] + " " + arg[1] + " " + arg[2]
        command = command.strip()
        new_filter = Filter(command)
        self.platform.add_filter(new_filter)
        return f"Successfully added range filter"
        
    
    def handle_search(self,arg):
        command = arg[0]
        new_filter = Filter(command)
        self.platform.add_filter(new_filter)
        return f"Successfully added search filter"

    def handle_clear(self,arg):
        index = arg[0]
        self.platform.remove_filter(index)
        return f"Successfully removed filter"

    def handle_save(self, args=None):
        try:
            with open(self.file_path, "w") as f:
                json.dump(self.platform.graph.to_json_dict_hierarchy(), f, indent=2)
            return f"Graph saved successfully to {self.file_path}."
        except Exception as e:
            return f"ERROR: Failed to save graph. {str(e)}"

    def parse_cli_args(self, args):
        """
        Parses CLI arguments for commands like:
        create node --id=2 --property Name=Tom --property Age=30 --property Gender=M --property Height=175
        create edge --id=1 --property Name=Siblings 1 2

        Returns:
            {
                "type": "edge" | "node",
                "id": "1",
                "properties": {"Name": "Siblings"},
                "extra": ["1", "2"]   # remaining positional args
            }
        """
        if isinstance(args, str):
            tokens = shlex.split(args)
        else:
            tokens = args

        if not tokens:
            return {}

        result = {
            "type": None,
            "id": None,
            "properties": {},
            "extra": []
        }
        result["type"] = tokens[0]
        
        i = 1
        while i < len(tokens):
            token = tokens[i]
            if token.startswith("--id="):
                result["id"] = token.split("=", 1)[1]
            elif token == "--id" and i + 1 < len(tokens):
                result["id"] = tokens[i+1]
                i += 1
            elif token == "--property" and i + 1 < len(tokens):
                key, value = tokens[i+1].split("=", 1)
                result["properties"][key] = value
                i += 1
            else:
                result["extra"].append(token)
            i += 1

        return result
    
class Filter():
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
            
            match tokens[1]:
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