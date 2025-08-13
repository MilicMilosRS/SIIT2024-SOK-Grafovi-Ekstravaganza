from django.shortcuts import render
from block_visualizer import BlockVisualizer
from data_source_json import JSONDataSource
from simple_visualizer import SimpleVisualizer
from django.http import JsonResponse
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .management.commands import cli
from graph_api import Graph, GraphVisualizer

graph_instance = Graph(False)
filepath = "../large_graph.json"
cli_instance = cli.CommandLine(graph_instance,filepath)
visualizer = BlockVisualizer()

def HomePage(request):
    global graph_instance

    style = request.GET.get("style","simple")
    js = JSONDataSource(filepath)
    js.parse_json()
    graph_instance = js.convert_to_api_graph()
    if style == "block":
        visualizer = BlockVisualizer()
    else:
        visualizer = SimpleVisualizer()

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
    return HttpResponse(html)