from django.shortcuts import render
from block_visualizer import BlockVisualizer
from data_source_json import JSONDataSource

# Create your views here.
def HomePage(request):
    js = JSONDataSource("../large_graph.json")
    js.parse_json()
    g = js.convert_to_api_graph()

    visaulizer = BlockVisualizer()
    context = {"main_view": visaulizer.visualize_graph(g)}
    return render(request, 'index.html', context)