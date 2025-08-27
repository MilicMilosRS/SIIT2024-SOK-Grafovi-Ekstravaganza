from graph_api import Graph
from graph_platform import Platform

class Workspace:
    def __init__(self, graph=None):
        self.graph = graph

class WorkspaceManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.workspaces: dict[str, Workspace] = {}
        self.active_id: str | None = None
        self.counter = 1
        self._initialized = True

    def create_workspace(self, graph=None):
        wid = f"workspace{self.counter}"
        self.counter += 1
        ws = Workspace(graph=graph or Graph(False))
        self.workspaces[wid] = ws
        self.active_id = wid
        self._apply_to_platform(ws)
        return wid, ws

    def close_workspace(self, wid: str):
        if wid in self.workspaces and len(self.workspaces) > 1:
            del self.workspaces[wid]
            if self.active_id == wid:
                self.active_id = next(iter(self.workspaces.keys()))
                self._apply_to_platform(self.workspaces[self.active_id])

    def switch_workspace(self, wid: str):
        if wid in self.workspaces:
            if self.active_id:
                self._save_from_platform(self.workspaces[self.active_id])
            self.active_id = wid
            self._apply_to_platform(self.workspaces[wid])

    def get_active_workspace(self) -> Workspace:
        return self.workspaces.get(self.active_id)

    def get_all_workspaces(self):
        return self.workspaces

    def _apply_to_platform(self, ws: Workspace):
        platform = Platform()  # singleton
        platform.set_graph(ws.graph)
        platform.update_graph_view()
        return

    def _save_from_platform(self, ws: Workspace):
        platform = Platform()
        ws.graph = platform.graph