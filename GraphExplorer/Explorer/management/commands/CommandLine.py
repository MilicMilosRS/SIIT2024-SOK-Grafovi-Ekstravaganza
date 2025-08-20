import shlex

from . import CreateCommand, EditCommand, DeleteCommand, SaveGraphCommand, FilterCommand

class CommandLine:
    def __init__(self, platform, file_path=None):
        self.platform = platform
        self.file_path = file_path
        self.command_map = {
            "create": CreateCommand.CreateCommand,
            "edit": EditCommand.EditCommand,
            "delete": DeleteCommand.DeleteCommand,
            "save-graph": SaveGraphCommand.SaveGraphCommand,
            "filter": FilterCommand.FilterCommand,
            # search
        }

    def process_command(self, command_str):
        tokens = shlex.split(command_str)
        if not tokens:
            return ""

        cmd_name = tokens[0].lower()
        args = tokens[1:]

        CommandClass = self.command_map.get(cmd_name)
        if not CommandClass:
            return f"WARNING: Unknown command: {cmd_name}"

        command_obj = CommandClass(self.platform, args)
        return command_obj.execute()
    
    @staticmethod
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
