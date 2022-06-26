from django.urls import path

from manager.views import index, add, delete, show_peer, show_peer_api

urlpatterns = [
    path('', index, name='index'),
    path('add', add, name='add'),
    path('delete/<int:peer_id>', delete, name='delete'),
    path('show/<int:peer_id>', show_peer, name='show_peer'),
    path('api/show/<int:peer_id>', show_peer_api, name='show_peer_api'),
]
