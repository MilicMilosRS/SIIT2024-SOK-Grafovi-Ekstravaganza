from django.shortcuts import render
import block_visualizer
import api

# Create your views here.
def HomePage(request):
    g = api.Graph(False)

    A = api.Node("A")
    A.set_attribute("Ime", "Milos Milic")
    B = api.Node("B")
    B.set_attribute("Ime", "Mirko Djukic")

    g.add_vertex(A)
    g.add_vertex(B)

    g.create_edge("A", "B")

    visaulizer = block_visualizer.BlockVisualizer()
    context = {"main_view_script": visaulizer.visualize_graph(g)}
    return render(request, 'index.html', context)