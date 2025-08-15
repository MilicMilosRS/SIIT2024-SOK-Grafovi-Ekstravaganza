from django.urls import path
from . import views
from .views import HomePage

urlpatterns = [
    path('', HomePage, name='HomePage'),
    path('run-command/', views.run_command, name='run_command'),
    path('partial-graph', views.partial_graph_view, name='partial_graph'),
    path('treeview/updates', views.sse_treeview_updates, name='treeview_updates'),
    path('treeview/expand', views.expand_treeview_node, name='expand_treeview'),
]