import asyncio
import random
from threading import Lock, Thread

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from ipaddress import IPv4Network, IPv6Address, IPv6Network
from vymgmt import Router

from manager.forms import NewPeerForm
from manager.models import Peer

firewall_locked = Lock()


@login_required(login_url='/oauth')
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


def add_peer(name: str, peer: Peer):
    vyos = Router(address=settings.VYOS_HOSTNAME, user=settings.VYOS_USERNAME)
    vyos.login()

    with firewall_locked:
        try:
            vyos.configure()

            vyos.set(f"firewall group address-group VPN-{name} address {peer.tunnel_ipv4}")
            vyos.set(f"firewall group ipv6-address-group VPN-{name}-6 address {peer.tunnel_ipv6}")
            wg_peer_path = f"interfaces wireguard {settings.WG_INTERFACE} peer {name}-{peer.name}"
            vyos.set(f"{wg_peer_path} allowed-ips {peer.tunnel_ipv4}/32")
            vyos.set(f"{wg_peer_path} allowed-ips {peer.tunnel_ipv6}/128")
            vyos.set(f"{wg_peer_path} persistent-keepalive 30")
            vyos.set(f"{wg_peer_path} pubkey {peer.public_key}")

            vyos.commit()
            vyos.save()
        finally:
            vyos.exit()

    vyos.logout()


@login_required(login_url='/oauth')
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


def delete_peer(name: str, peer: Peer):
    vyos = Router(address=settings.VYOS_HOSTNAME, user=settings.VYOS_USERNAME)
    vyos.login()

    with firewall_locked:
        try:
            vyos.configure()

            vyos.delete(f"firewall group address-group VPN-{name} address {peer.tunnel_ipv4}")
            vyos.delete(f"firewall group ipv6-address-group VPN-{name}-6 address {peer.tunnel_ipv6}")
            vyos.delete(f"interfaces wireguard {settings.WG_INTERFACE} peer {name}-{peer.name}")

            vyos.commit()
            vyos.save()
        finally:
            vyos.exit()

    vyos.logout()


@login_required(login_url='/oauth')
def delete(request: HttpRequest, peer_id) -> HttpResponse:
    if peer := Peer.objects.get(id=peer_id, owner=request.user):
        name = f'{request.user.first_name.upper()}-{request.user.last_name.upper()}'
        t = Thread(target=delete_peer, args=(name, peer))
        t.start()
        peer.delete()
    return redirect('manager:index')


@login_required(login_url='/oauth')
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
