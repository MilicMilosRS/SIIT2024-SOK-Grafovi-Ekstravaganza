import time
from django.shortcuts import render
from block_visualizer import BlockVisualizer
from data_source_json import JSONDataSource
from simple_visualizer import SimpleVisualizer
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .management.commands import cli
from graph_api import Graph, Node
from graph_platform import Platform, TreeNode, ForestView

# --- Initialize once at import time ---
filepath = "../mediun.json"
js = JSONDataSource(filepath)
js.parse_json()
graph_instance = js.convert_to_api_graph()

# cli_instance = cli.CommandLine(graph_instance, filepath)
# visualizer = BlockVisualizer()

platform = Platform(graph_instance, SimpleVisualizer())
cli_instance = cli.CommandLine(platform, filepath)

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
        
        html = cli_instance.process_command("search " + search_filter)
        context = {"main_view": html}
        print(context)
    return render(request, 'index.html', context)

@csrf_exempt
def filter_graph(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            filter_filter = data.get("value", "")
        except Exception:
            return JsonResponse({"output": "Invalid request"}, status=400)
    
        html = cli_instance.process_command("filter " + filter_filter)
    return JsonResponse({"main_view": html})

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
def deselect_node(request):
    if request.method == "POST":
        platform.deselect_node()
        return JsonResponse({}, status=200)

    return JsonResponse({"output": "Invalid method"}, status=405)