from abc import ABC, abstractmethod

class Command(ABC):
    def __init__(self, platform, args):
        self.platform = platform
        self.args = args

    @abstractmethod
    def execute(self):
        pass
