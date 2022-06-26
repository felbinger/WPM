from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render, redirect

from threading import Thread

from manager.forms import NewPeerForm
from manager.models import Peer
from manager.utils import _is_base_64, _get_next_ipv4_address, _get_random_ipv6_address
from manager.vyos import add_peer, delete_peer


@login_required
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "overview.html", context={
        "peers": Peer.objects.filter(owner=request.user).all()
    })


@login_required
def add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = NewPeerForm(request.POST)
        if form.is_valid():
            if not _is_base_64(request.POST['public_key']):
                return HttpResponseBadRequest("Invalid wireguard public key!")

            peer = Peer(
                owner=request.user,
                name=request.POST['name'],
                public_key=request.POST['public_key'],
                tunnel_ipv4=_get_next_ipv4_address(settings.WG_IPV4_NETWORK),
                tunnel_ipv6=_get_random_ipv6_address(settings.WG_IPV6_PREFIX),
            )
            peer.save()

            name = f'{request.user.first_name.upper()}-{request.user.last_name.upper()}'
            t = Thread(target=add_peer, args=(name, peer))
            t.start()
        return redirect('manager:index')
    else:
        return render(request, 'add_peer.html', context={
            'form': NewPeerForm(),
        })


@login_required
def delete(request: HttpRequest, peer_id: int) -> HttpResponse:
    if peer := Peer.objects.get(id=peer_id, owner=request.user):
        peer.valid = False
        peer.save()
        name = f'{request.user.first_name.upper()}-{request.user.last_name.upper()}'
        t = Thread(target=delete_peer, args=(name, peer))
        t.start()
    return redirect('manager:index')


@login_required
def show_peer(request: HttpRequest, peer_id: int) -> HttpResponse:
    if not (peer := Peer.objects.filter(id=peer_id, owner=request.user).first()):
        return HttpResponseNotFound("Peer does not exist, or access denied!")

    return render(request, "show_peer.html", context={
        "peer": peer,
        "remote": {
            "description": settings.WG_DESCRIPTION,
            "publicKey": settings.WG_PUBKEY,
            "endpoint": settings.WG_ENDPOINT,
        }
    })
