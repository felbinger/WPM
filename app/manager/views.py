from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from ipaddress import IPv4Network, IPv6Address, IPv6Network
import random
from threading import Thread

from manager.forms import NewPeerForm
from manager.models import Peer
from manager.vyos import add_peer, delete_peer


@login_required
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "overview.html", context={
        "peers": Peer.objects.filter(owner=request.user).all()
    })


def _get_random_ipv6_address(ipv6_prefix) -> str:
    net = IPv6Network(ipv6_prefix)
    used_ipv6_addresses = [p.tunnel_ipv6 for p in Peer.objects.all()]
    # vyos itself has the first address
    used_ipv6_addresses.append(str(next(IPv6Network(ipv6_prefix).hosts())))
    def _get():
        # Which of the network.num_addresses we want to select?
        addr_no = random.randint(0, net.num_addresses)
        # Create the random address by converting to a 128-bit integer, adding addr_no and converting back
        network_int = int.from_bytes(net.network_address.packed, byteorder="big")
        addr_int = network_int + addr_no
        return str(IPv6Address(addr_int.to_bytes(16, byteorder="big")))
    while (ipv6_addr := _get()) in used_ipv6_addresses:
        pass
    return ipv6_addr


def _get_next_ipv4_address(ipv4_network: str) -> str:
    used_ipv4_addresses = [str(p.tunnel_ipv4) for p in Peer.objects.all()]
    # vyos itself has the first address
    used_ipv4_addresses.append(str(next(IPv4Network(ipv4_network).hosts())))
    for addr in IPv4Network(ipv4_network).hosts():
        if str(addr) not in used_ipv4_addresses:
            # return first address which is not in use
            return str(addr)


@login_required
def add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = NewPeerForm(request.POST)
        if form.is_valid():
            peer = Peer(
                owner=request.user,
                name=request.POST['name'],
                public_key=request.POST['public_key'],
                tunnel_ipv4=_get_next_ipv4_address(settings.WG_IPV4_NETWORK),
                tunnel_ipv6=_get_random_ipv6_address(settings.WG_IPV6_PREFIX),
            )

            name = f'{request.user.first_name.upper()}-{request.user.last_name.upper()}'
            t = Thread(target=add_peer, args=(name, peer))
            t.start()
            peer.save()
        return redirect('manager:index')
    else:
        return render(request, 'add_peer.html', context={
            'form': NewPeerForm(),
        })


@login_required
def delete(request: HttpRequest, peer_id) -> HttpResponse:
    if peer := Peer.objects.get(id=peer_id, owner=request.user):
        name = f'{request.user.first_name.upper()}-{request.user.last_name.upper()}'
        t = Thread(target=delete_peer, args=(name, peer))
        t.start()
        peer.delete()
    return redirect('manager:index')


@login_required
def show_peer(request: HttpRequest, peer_id) -> HttpResponse:
    if not (peer := Peer.objects.filter(id=peer_id, owner=request.user).first()):
        return HttpResponse(404)

    return render(request, "show_peer.html", context={
        "peer": peer,
        "remote": {
            "description": settings.WG_DESCRIPTION,
            "publicKey": settings.WG_PUBKEY,
            "endpoint": settings.WG_ENDPOINT,
        }
    })
