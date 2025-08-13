from django.shortcuts import render
from block_visualizer import BlockVisualizer
from data_source_json import JSONDataSource
from simple_visualizer import SimpleVisualizer

# Create your views here.
def HomePage(request):
    style = request.GET.get("style", "simple")

    js = JSONDataSource("../large_graph.json")
    js.parse_json()
    g = js.convert_to_api_graph()

    if style == "block":
        visualizer = BlockVisualizer()
    else:
        visualizer = SimpleVisualizer()

    context = {"main_view": visualizer.visualize_graph(g)}
    return render(request, 'index.html', context)