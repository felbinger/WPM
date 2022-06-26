import json

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

            # check if public key is valid
            if not _is_base_64(request.POST['public_key']):
                return HttpResponseBadRequest("Invalid wireguard public key!")

            # check if name is already in use
            if request.POST['name'].lower() in {p.name.lower() for p in Peer.objects.all()}:
                return HttpResponseBadRequest("Peer name already in use!")

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
    return render(request, "show_peer.html")


@login_required
def show_peer_api(request: HttpRequest, peer_id: int) -> HttpResponse:
    if not (peer := Peer.objects.filter(id=peer_id, owner=request.user).first()):
        return HttpResponseNotFound(json.dumps({
           "error": "not_found_or_forbidden",
        }))

    return HttpResponse(json.dumps({
        "peer": {
            "publicKey": peer.public_key,
            "tunnelIpv4": peer.tunnel_ipv4,
            "tunnelIpv6": peer.tunnel_ipv6,
        },
        "remote": {
            "description": settings.WG_DESCRIPTION,
            "publicKey": settings.WG_PUBKEY,
            "endpoint": settings.WG_ENDPOINT,
        },
    }))
