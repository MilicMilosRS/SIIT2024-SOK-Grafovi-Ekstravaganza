from abc import ABC, abstractmethod
from graph_api import Graph

class DataSourcePlugin(ABC):
    @abstractmethod
    def load_graph(self, **kwargs) -> Graph:
        """
        Parses data and returns Graph object.
        kwargs is used for parameters(file_path, api_url, api_key)
        """
        pass

    @abstractmethod
    def get_input_fields(self) -> list[str]:
        """Return a list of field names the user must provide to run this plugin."""
        pass

        