from django.shortcuts import render
from block_visualizer import BlockVisualizer
from data_source_json import JSONDataSource
from simple_visualizer import SimpleVisualizer
from django.http import JsonResponse, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .management.commands import cli
from graph_api import Graph
from graph_platform import Platform

# --- Initialize once at import time ---
filepath = "../large_graph.json"
# js = JSONDataSource(filepath)
# js.parse_json()
# graph_instance = js.convert_to_api_graph()

# cli_instance = cli.CommandLine(graph_instance, filepath)
# visualizer = BlockVisualizer()

platform = Platform(Graph(False), SimpleVisualizer())
cli_instance = cli.CommandLine(platform, filepath)

def HomePage(request):
    global platform

    style = request.GET.get("style", "simple")

    if style == "block":
        platform.set_visualizer(BlockVisualizer())
    else:
        platform.set_visualizer(SimpleVisualizer())

    for node in platform.graph._vertices.keys():
            print(node)

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
def partial_graph_view(request):
    html = platform.generate_main_view()
    return HttpResponse(html)
