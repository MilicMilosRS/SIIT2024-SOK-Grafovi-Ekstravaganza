import asyncio
import os
import threading
import websockets
import json
from graph_api import Graph, Node, GraphVisualizer

class BlockVisualizer(GraphVisualizer):
    def __init__(self):
        self.clients = set()
        self.loop = None
        self.server = None

    def on_switched_to(self):
        self.thread = threading.Thread(target=self._start_background_server, daemon=True)
        self.thread.start()

    def _start_background_server(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = loop

        async def start():
            self.server = await websockets.serve(self._handler, "localhost", 8765)

        loop.run_until_complete(start())  # start the server
        loop.run_forever()  
        print("Server running")

    def on_switched_from(self):
        print("Switched from")
        if self.loop and self.server:
            asyncio.run_coroutine_threadsafe(self._shutdown_server(), self.loop).result()

    async def _shutdown_server(self):
        print("Shutting down server...")
        self.server.close()
        await self.server.wait_closed()
        self.loop.call_soon_threadsafe(self.loop.stop)


    async def _handler(self, websocket):
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)

    def _send_update(self, update: dict):
        """Send update to all connected clients from sync code."""
        if self.loop:
            asyncio.run_coroutine_threadsafe(self._send_update_async(update), self.loop)

    async def _send_update_async(self, update: dict):
        if self.clients:
            msg = json.dumps(update)
            await asyncio.gather(*(client.send(msg) for client in self.clients))

    def visualize_graph(self, g: Graph) -> str:
        parsedNodes = []
        for node in g._vertices.values():
            parsedNodes.append(node._attributes)

        parsedLinks = []
        for source, targets in g._edges.items():
            for target in targets:
                parsedLinks.append({"source": source, "target": target, "attrs": g._edges[source][target]})

        template_path = os.path.join(os.path.dirname(__file__))
        with open(template_path + "/templates/layout.html") as file:
            html = file.read()

        return html.replace("NODES", json.dumps(parsedNodes)).replace("LINKS", json.dumps(parsedLinks)).replace("IS_DIRECTED", "true" if g._is_directed else "false")

    def add_node(self, node: Node):
        print("adding node")
        self._send_update({
            "action": "addNode",
            "node": {"id": node.get_id(), **node._attributes}
        })

    def edit_node(self, node: Node):
        self._send_update({
            "action": "editNode",
            "node": {"id": node.get_id(), **node._attributes}
        })

    def remove_node(self, node: Node):
        self._send_update({
            "action": "removeNode",
            "id": node.get_id()
        })

    def add_link(self, id_source: str, id_target: str, **attrs):
        self._send_update({
            "action": "addLink",
            "source": id_source,
            "target": id_target,
            "attrs": attrs
        })

    def edit_link(self, id_source: str, id_target: str, **attrs):
        self._send_update({
            "action": "editLink",
            "source": id_source,
            "target": id_target,
            "attrs": attrs
        })

    def remove_link(self, id_source: str, id_target: str):
        self._send_update({
            "action": "removeLink",
            "source": id_source,
            "target": id_target
        })