import random

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render, redirect

from ipaddress import IPv4Network, IPv6Address, IPv6Network
from string import hexdigits

from manager.forms import NewPeerForm
from manager.models import Peer


@login_required(login_url='/oauth')
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "overview.html", context={"peers": Peer.objects.filter(owner=request.user).all()})


# TODO improve
def _get_random_ipv6_address(ipv6_prefix) -> str:
    net = IPv6Network(ipv6_prefix)
    used_ipv6_addresses = [p.tunnel_ipv6[:-19] for p in Peer.objects.all()]
    # vyos itself has the first address of the ipv6 network (...::1)
    used_ipv6_addresses.append(str(next(IPv6Network(ipv6_prefix).hosts())))
    # Which of the network.num_addresses we want to select?
    addr_no = random.randint(0, net.num_addresses)
    # Create the random address by converting to a 128-bit integer, adding addr_no and converting back
    network_int = int.from_bytes(net.network_address.packed, byteorder="big")
    addr_int = network_int + addr_no
    ipv6_addr = str(IPv6Address(addr_int.to_bytes(16, byteorder="big")))
    while ipv6_addr in used_ipv6_addresses:
        # Which of the network.num_addresses we want to select?
        addr_no = random.randint(0, net.num_addresses)
        # Create the random address by converting to a 128-bit integer, adding addr_no and converting back
        network_int = int.from_bytes(net.network_address.packed, byteorder="big")
        addr_int = network_int + addr_no
        ipv6_addr = str(IPv6Address(addr_int.to_bytes(16, byteorder="big")))
    return ipv6_addr


# TODO improve
def _get_next_ipv4_address() -> str:
    used_ipv4_addresses = [str(p.tunnel_ipv4) for p in Peer.objects.all()]
    # vyos itself has 10.2.248.1
    used_ipv4_addresses.append("10.2.248.1")
    for addr in IPv4Network('10.2.248.0/22').hosts():
        if str(addr) not in used_ipv4_addresses:
            # return first address which is not in use
            return str(addr)


@login_required(login_url='/oauth')
def add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = NewPeerForm(request.POST)
        if form.is_valid():
            peer = Peer(
                owner=request.user,
                name=request.POST['name'],
                public_key=request.POST['public_key'],
                tunnel_ipv4=_get_next_ipv4_address(),
                tunnel_ipv6=_get_random_ipv6_address(settings.WG_IPV6_PREFIX),
            )

            # TODO execute vyos commands
            name = f'{request.user.first_name.upper()}-{request.user.last_name.upper()}'
            print(f"""
set firewall group address-group VPN-{name} address {peer.tunnel_ipv4}
set firewall group ipv6-address-group VPN-{name}-6 address {peer.tunnel_ipv6}
set interfaces wireguard {settings.WG_INTERFACE} peer {name}-{peer.name} allowed-ips {peer.tunnel_ipv4}/32
set interfaces wireguard {settings.WG_INTERFACE} peer {name}-{peer.name} allowed-ips {peer.tunnel_ipv6}/128
set interfaces wireguard {settings.WG_INTERFACE} peer {name}-{peer.name} persistent-keepalive 30
set interfaces wireguard {settings.WG_INTERFACE} peer {name}-{peer.name} pubkey {peer.public_key}""")

            peer.save()
        return redirect('manager:index')
    else:
        return render(request, 'add_peer.html', context={
            'form': NewPeerForm(),
        })


@login_required(login_url='/oauth')
def delete(request: HttpRequest, peer_id) -> HttpResponse:
    if peer := Peer.objects.get(id=peer_id, owner=request.user):
        # TODO execute vyos commands
        name = f'{request.user.first_name.upper()}-{request.user.last_name.upper()}'
        print(f"""
del firewall group address-group VPN-{name} address {peer.tunnel_ipv4}
del firewall group ipv6-address-group VPN-{name}-6 address {peer.tunnel_ipv6}
del interfaces wireguard wg100 peer {name}-{peer.name}""")
        peer.delete()
    return redirect('manager:index')


@login_required(login_url='/oauth')
def show_peer(request: HttpRequest, peer_id) -> HttpResponse:
    peer = Peer.objects.filter(id=peer_id, owner=request.user).first()

    if not peer:
        return HttpResponse(404)

    return render(request, "show_peer.html", context={
        "peer": peer,
        "remote": {
            "description": settings.WG_DESCRIPTION,
            "publicKey": settings.WG_PUBKEY,
            "endpoint": settings.WG_ENDPOINT,
        }
    })
