from django.urls import path

from manager.views import index, add, delete, show_peer, source_groups, source_groups6

urlpatterns = [
    path('', index, name='index'),
    path('add', add, name='add'),
    path('delete/<int:peer_id>', delete, name='delete'),
    path('show/<int:peer_id>', show_peer, name='show_peer'),
    path('vyoscli/vpn-source-groups', source_groups, name='source_groups'),
    path('vyoscli/vpn-source-groups6', source_groups6, name='source_groups6'),
]
