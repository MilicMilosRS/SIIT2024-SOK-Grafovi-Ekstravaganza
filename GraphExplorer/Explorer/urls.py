from django.urls import path
from . import views
from .views import HomePage

urlpatterns = [
    path('', HomePage, name='HomePage'),
    path('run-command/', views.run_command, name='run_command'),
    path('partial-graph', views.partial_graph_view, name='partial_graph'),
    path('treeview/updates', views.sse_treeview_updates, name='treeview_updates'),
    path('treeview/expand', views.expand_treeview_node, name='expand_treeview'),
    path('treeview/collapse', views.collapse_treeview_node, name='expand_treeview'),
    path('select/<str:item_id>/', views.select_node, name='select_node'),
    path('select/', views.get_selected_node, name='get_selection'),
    path('deselect/', views.deselect_node, name='deselect_node'),

    path('api/vertex/create/', views.create_vertex, name="create_vertex"),
    path('api/vertex/edit/', views.edit_vertex, name="edit_vertex"),
    path('api/vertex/delete/', views.delete_vertex, name="delete_vertex"),
]