from django.shortcuts import render
from block_visualizer import BlockVisualizer
from data_source_json import JSONDataSource
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .management.commands import cli


js = JSONDataSource("../large_graph.json")
js.parse_json()
graph_instance = js.convert_to_api_graph()
cli_instance = cli.CommandLine(graph_instance)

def HomePage(request):
    global graph_instance, cli_instance

    js = JSONDataSource("../large_graph.json")
    js.parse_json()
    graph_instance = js.convert_to_api_graph()

    if cli_instance is None:
        cli_instance = cli.CommandLine(graph_instance)
    else:
        cli_instance.graph = graph_instance
    print("Nodes:", len(graph_instance._vertices))
    print("Edges:", sum(len(v) for v in graph_instance._edges.values()))
    visualizer = BlockVisualizer()
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
