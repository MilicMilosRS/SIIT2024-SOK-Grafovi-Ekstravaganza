from django.shortcuts import render
from block_visualizer import BlockVisualizer
from data_source_json import JSONDataSource
from simple_visualizer import SimpleVisualizer
from django.http import JsonResponse, HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt

from graph_api import Graph
from graph_platform import Platform

from .management.commands.CommandLine import CommandLine
from .management.commands import CreateCommand, EditCommand, DeleteCommand, SaveGraphCommand


filepath = "../large_graph.json"
js = JSONDataSource(filepath)
js.parse_json()
graph_instance = js.convert_to_api_graph()

platform = Platform(graph_instance, SimpleVisualizer())

cli_instance = CommandLine(platform, filepath)
# cli_instance.register_command("create", CreateCommand(platform))
# cli_instance.register_command("delete", DeleteCommand(platform))
# cli_instance.register_command("edit", EditCommand(platform))
# cli_instance.register_command("save", SaveGraphCommand(platform))


def HomePage(request):
    global platform

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

        # Send the text input into your CommandLine
        output = cli_instance.process_command(command)
        return JsonResponse({"output": output})

    return JsonResponse({"output": "Invalid method"}, status=405)


@csrf_exempt
def partial_graph_view(request):
    html = platform.generate_main_view()
    return HttpResponse(html)
