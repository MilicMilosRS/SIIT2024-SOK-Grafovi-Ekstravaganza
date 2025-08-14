from django.shortcuts import render
from block_visualizer import BlockVisualizer
from data_source_json import JSONDataSource
from simple_visualizer import SimpleVisualizer
from django.http import JsonResponse, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .management.commands import cli
from graph_api import Node, Graph, GraphVisualizer

graph_instance = Graph(True)
graph_instance.add_vertex(Node("gas1"))
graph_instance.add_vertex(Node("gas2"))
graph_instance.create_edge("gas1", "gas2", **{"attr1": "gas", "attr2": 13})
graph_instance.create_edge("gas2", "gas1", **{"attr1": "drugi gas", "attr2": 13})

cli_instance = cli.CommandLine(graph_instance)
visualizer = BlockVisualizer()

def HomePage(request):
    global graph_instance

    style = request.GET.get("style", "simple")

    if style == "block":
        visualizer = BlockVisualizer()
    else:
        visualizer = SimpleVisualizer()

    context = {"main_view": visualizer.visualize_graph(graph_instance)}
    context = {"main_view": visualizer.visualize_graph(graph_instance)}
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
    html = visualizer.visualize_graph(graph_instance)
    print(html)
    return HttpResponse(html)
