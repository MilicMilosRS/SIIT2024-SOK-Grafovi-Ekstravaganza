from django.shortcuts import render
import block_visualizer
import api
import data_source_json

# Create your views here.
def HomePage(request):
    js = data_source_json.JSONDataSource("../large_graph.json")
    js.parse_json()
    g = js.convert_to_api_graph()

    visaulizer = block_visualizer.BlockVisualizer()
    context = {"main_view_script": visaulizer.visualize_graph(g)}
    return render(request, 'index.html', context)