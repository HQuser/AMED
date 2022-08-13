from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.homepage, name='home'),
    path('get_doc', views.get_document_preview, name='get_doc'),
    path('get_clust_data', views.get_cluster_data, name='get_clust_data'),
    path('get_clusters', views.get_clusters, name='get_clusters'),
    path('viz', views.viz, name='viz')
]