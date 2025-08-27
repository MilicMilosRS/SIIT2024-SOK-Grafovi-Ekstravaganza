import time
from django.shortcuts import render
from block_visualizer import BlockVisualizer
from data_source_json import JSONDataSource
from simple_visualizer import SimpleVisualizer
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
import json
from django.views.decorators.csrf import csrf_exempt

from graph_api import Graph, Node
from graph_platform import Platform
from workspace import WorkspaceManager
from plugin_registry import get_plugin_names, create_plugin
import os
import tempfile

from .management.commands.CommandLine import CommandLine
from .management.commands import CreateCommand, EditCommand, DeleteCommand, SaveGraphCommand


kwargs = {"file_path": "../large_graph.json"}
js = JSONDataSource(**kwargs)
graph_instance=js.load_graph()
platform = Platform(graph_instance, SimpleVisualizer(), kwargs["file_path"])
wm = WorkspaceManager()
wm.create_workspace(graph_instance)
cli_instance = CommandLine(platform, kwargs["file_path"])


def HomePage(request):
    global platform
    platform.attach_update_listener(notify_graph_update)

    style = request.GET.get("style", "simple")

    if style == "block":
        platform.set_visualizer(BlockVisualizer())
    else:
        platform.set_visualizer(SimpleVisualizer())

    context = {"main_view": platform.generate_main_view()}
    return render(request, 'index.html', context)


@csrf_exempt
def run_command(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            command = data.get("command", "")
        except Exception:
            return JsonResponse({"output": "Invalid request"}, status=400)

        output = cli_instance.process_command(command)
        return JsonResponse({"output": output})

    return JsonResponse({"output": "Invalid method"}, status=405)


@csrf_exempt
def search_graph(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            search_filter = data.get("value", "")
        except Exception:
            return JsonResponse({"output": "Invalid request"}, status=400)
        
        cli_instance.process_command(search_filter)
    return JsonResponse({"success": True})

@csrf_exempt
def filter_graph(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            filter_filter = data.get("value", "")
        except Exception:
            return JsonResponse({"output": "Invalid request"}, status=400)
    
        html = cli_instance.process_command(filter_filter)
    return JsonResponse({"main_view": html})

@csrf_exempt
def get_filters(request):
    if request.method == "POST":
        filters = platform.get_filters()
        serialized_filters = []
        for filter in filters:
            serialized_filters.append(filter.serialize())
        if len(serialized_filters) != 0:
            platform.update_graph_view()
    return JsonResponse({"filters": serialized_filters})

@csrf_exempt
def remove_filter(request):
    if request.method == "POST":
        data = json.loads(request.body)
        index = data.get("index", "")
        platform.remove_filter(index)
    return JsonResponse({"success": True})

@csrf_exempt
def partial_graph_view(request):
    html = platform.generate_main_view()
    return HttpResponse(html)

#TreeView stuff

#list of callbacks for SSE
_graph_update_listeners = []

def notify_graph_update():
    data = json.dumps(platform.get_tree_view())
    for callback in _graph_update_listeners:
        callback(data)

#reloads the treeview when the graph is updated
def sse_treeview_updates(request):
    def event_stream():
        last_data = None

        # Define a callback to push updates
        data_queue = []

        def listener(new_data):
            data_queue.append(new_data)

        _graph_update_listeners.append(listener)

        try:
            initial_data = json.dumps(platform.get_tree_view())
            yield f"data: {initial_data}\n\n"
            
            while True:
                if data_queue:
                    # pop the latest update
                    data = data_queue.pop(0)
                    yield f"data: {data}\n\n"
                else:
                    time.sleep(0.1)  # small sleep to avoid busy loop
        finally:
            _graph_update_listeners.remove(listener)

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

@csrf_exempt
def expand_treeview_node(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            id = data.get("tree_id", "")
        except Exception:
            return JsonResponse({"output": "Invalid request"}, status=400)

        platform.expand_tree_view(id)
        return JsonResponse({}, status=200)

    return JsonResponse({"output": "Invalid method"}, status=405)

@csrf_exempt
def collapse_treeview_node(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            id = data.get("tree_id", "")
        except Exception:
            return JsonResponse({"output": "Invalid request"}, status=400)

        platform.collapse_tree_view(id)
        return JsonResponse({}, status=200)

    return JsonResponse({"output": "Invalid method"}, status=405)


#Selection stuff
@csrf_exempt
def select_node(request, item_id):
    if request.method == "POST":
        if platform.select_node(item_id) is None:
            return JsonResponse({}, status=404)
        return JsonResponse({}, status=200)

    return JsonResponse({"output": "Invalid method"}, status=405)

@csrf_exempt
def get_selected_node(request):
    if request.method == "GET":
        if platform.selected_node is None:
            return JsonResponse({}, status=404)
        return JsonResponse({"node": platform.selected_node._attributes}, status=200)

    return JsonResponse({"output": "Invalid method"}, status=405)

@csrf_exempt
def deselect_node(request):
    if request.method == "POST":
        platform.deselect_node()
        return JsonResponse({}, status=200)

    return JsonResponse({"output": "Invalid method"}, status=405)

#CRUD STUFF
@csrf_exempt
def create_vertex(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            id = data.get("id")
            if id is None:
                raise Exception("No id")

            attrs = data.get("attributes")
            n = Node(id)
            if attrs is not None:
                for attr_name, attr_value in attrs.items():
                    n.set_attribute(attr_name, attr_value)
            if platform.add_vertex(n):
                return JsonResponse({}, status=200)
            return JsonResponse({}, status=409)

        except Exception:
            return JsonResponse({"output": "Invalid request"}, status=400)

    return JsonResponse({"output": "Invalid method"}, status=405)

@csrf_exempt
def edit_vertex(request):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            id = data.get("id")
            if id is None:
                raise Exception("No id")

            attrs = data.get("attributes")
            n = Node(id)
            if attrs is not None:
                for attr_name, attr_value in attrs.items():
                    n.set_attribute(attr_name, attr_value)
            if platform.edit_vertex(n):
                return JsonResponse({}, status=200)

            return JsonResponse({}, status=409)

        except Exception:
            return JsonResponse({"output": "Invalid request"}, status=400)

    return JsonResponse({"output": "Invalid method"}, status=405)

@csrf_exempt
def delete_vertex(request):
    if request.method == "DELETE":
        try:
            data = json.loads(request.body)
            id = data.get("id")
            print(id)
            if id is None:
                return JsonResponse({"output": "No ID provided"}, status=400)
            
            node = platform.graph._vertices.get(id)
            if node is None:
                return JsonResponse({"output": "Node with that id doesn't exist"}, status=404)
            
            platform.delete_vertex(node)
            return JsonResponse({}, status=200)

        except Exception:
            return JsonResponse({"output": "Invalid request"}, status=400)

    return JsonResponse({"output": "Invalid method"}, status=405)

@csrf_exempt
def get_graph_data(request):
    if request.method == "GET":
        data = platform.get_graph_data()
        return JsonResponse(data, status=200)
    return JsonResponse({"output": "Invalid method"}, status=405)




#getting all installed data source plugins so we can give user options from which he can choose
def get_plugins(request):
    plugins = get_plugin_names()
    return JsonResponse({"plugins": plugins})

#getting all fileds that need to be filled for chosen data source so UI can be generated dynamically
def plugin_fields(request):
    plugin_name = request.GET.get("plugin")
    if not plugin_name:
        return JsonResponse({"fields": []})
    
    try:
        plugin_instance = create_plugin(plugin_name)
        fields = plugin_instance.get_input_fields()
        return JsonResponse({"fields": fields})
    except KeyError:
        return JsonResponse({"fields": []})



#getting all data necessary to load graph and making new workspace with newly loaded graph
@csrf_exempt
def load_graph(request):
    if request.method != "POST":
        return JsonResponse({"output": "Invalid method"}, status=405)

    #getting plugin name from form data
    plugin_name = request.POST.get("plugin")
    if not plugin_name:
        return JsonResponse({"output": "Plugin not specified"}, status=400)

    try:
        #collecting kwargs for plugin dynamically
        kwargs = {}
        for key in request.POST:
            if key != "plugin":
                kwargs[key] = request.POST.get(key)

        #handling uploaded files
        for key in request.FILES:
            uploaded_file = request.FILES[key]
            #saving temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                for chunk in uploaded_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            kwargs[key] = tmp_path

        #instantiating plugin dynamically
        plugin_instance = create_plugin(plugin_name, **kwargs)

        #loading graph
        new_graph = plugin_instance.load_graph(**kwargs)

        #creating a new workspace using WorkspaceManager
        manager = WorkspaceManager()
        wid, workspace = manager.create_workspace(graph=new_graph)

        #cleaning up temp files if any
        for key in request.FILES:
            os.remove(kwargs[key])

        return JsonResponse({
            "success": True,
            "workspace_id": wid,
            "active_wid": manager.active_id
        })
    
    except Exception as e:
        return JsonResponse({"output": str(e)}, status=500)
    





def get_workspaces(request):
    """
    Returns all workspaces and the active workspace.
    """
    workspace_manager = WorkspaceManager()
    all_ws = workspace_manager.get_all_workspaces()
    ws_list = [{"id": wid, "name": f"Workspace {i+1}"} for i, wid in enumerate(all_ws.keys())]
    return JsonResponse({"workspaces": ws_list, "active_wid": workspace_manager.active_id})


@csrf_exempt
def switch_workspace(request):
    """
    Switches the active workspace.
    """
    workspace_manager = WorkspaceManager()
    if request.method != "POST":
        return JsonResponse({"output": "Invalid method"}, status=405)

    import json
    try:
        data = json.loads(request.body)
        wid = data.get("wid")
        if not wid or wid not in workspace_manager.workspaces:
            return JsonResponse({"output": "Workspace not found"}, status=404)

        workspace_manager.switch_workspace(wid)
        return JsonResponse({"active_wid": wid})
    except Exception as e:
        return JsonResponse({"output": str(e)}, status=500)

@csrf_exempt
def close_workspace(request):
    """
    Closes a workspace.
    """
    workspace_manager = WorkspaceManager()
    if request.method != "POST":
        return JsonResponse({"output": "Invalid method"}, status=405)

    import json
    try:
        data = json.loads(request.body)
        wid = data.get("wid")
        if not wid or wid not in workspace_manager.workspaces:
            return JsonResponse({"output": "Workspace not found"}, status=404)

        workspace_manager.close_workspace(wid)
        return JsonResponse({"active_wid": workspace_manager.active_id})
    except Exception as e:
        return JsonResponse({"output": str(e)}, status=500)