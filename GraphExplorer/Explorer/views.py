from django.shortcuts import render
from block_visualizer import BlockVisualizer
from data_source_json import JSONDataSource
from django.http import JsonResponse
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .management.commands import cli
from graph_api import Graph, GraphVisualizer

graph_instance = Graph(False)
cli_instance = cli.CommandLine(graph_instance)
visualizer = BlockVisualizer()

def HomePage(request):
    global graph_instance, cli_instance

    if cli_instance is None:
        cli_instance = cli.CommandLine(graph_instance)
    else:
        cli_instance.graph = graph_instance
    print("Nodes:", len(graph_instance._vertices))
    print("Edges:", sum(len(v) for v in graph_instance._edges.values()))
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
    global visualizer, graph_instance
    html = visualizer.visualize_graph(graph_instance)
    print(html)
    return HttpResponse(html)