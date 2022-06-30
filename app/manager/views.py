import json
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpRequest, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render

from threading import Thread

from manager.models import Peer
from manager.utils import _is_base_64, _get_next_ipv4_address, _get_random_ipv6_address, _get_name
from manager.vyos import add_peer, delete_peer


@login_required
def index(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        return HttpResponse(json.dumps({
            'peers': [
                {
                    'id': peer.id,
                    'name': peer.name,
                    'tunnelIpAddresses': [
                        f'{peer.tunnel_ipv4}/32',
                        f'{peer.tunnel_ipv6}/128',
                    ],
                    'valid': peer.valid,
                    'publicKey': peer.public_key,
                } for peer in Peer.objects.filter(owner=request.user).all()
            ]
        }))
    else:
        return render(request, "wpm.html")


@login_required
def add(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest()

        if 'name' in data and 'publicKey' in data:
            # check if public key is valid
            if not re.match(r'^[A-Za-z0-9+/]{43}=$', data['publicKey']) or not _is_base_64(str(data['publicKey'])):
                return HttpResponseNotFound(json.dumps({
                   "error": "invalid_wireguard_public_key",
                }))

            # check if name matches format
            if not re.match(r'^[A-Za-z0-9]{1,32}$', data['name']):
                return HttpResponseNotFound(json.dumps({
                   "error": "invalid_peer_name_format",
                }))

            # check if name is already in use
            if str(data['name']).upper() in {p.name.upper() for p in Peer.objects.all()}:
                return HttpResponseNotFound(json.dumps({
                   "error": "peer_name_already_in_use",
                }))

            peer = Peer(
                owner=request.user,
                name=data['name'],
                public_key=data['publicKey'],
                tunnel_ipv4=_get_next_ipv4_address(settings.WG_IPV4_NETWORK),
                tunnel_ipv6=_get_random_ipv6_address(settings.WG_IPV6_PREFIX),
            )
            peer.save()
            t = Thread(target=add_peer, args=(_get_name(request.user), peer))
            t.start()
            return HttpResponse()
    return HttpResponseBadRequest(json.dumps({
       "error": "invalid_payload",
    }))


@login_required
def delete(request: HttpRequest, peer_id: int) -> HttpResponse:
    if request.method != "DELETE":
        return HttpResponseBadRequest(json.dumps({
           "error": "invalid_http_method_use_delete",
        }))
    if peer := Peer.objects.get(id=peer_id, owner=request.user):
        peer.valid = False
        peer.save()
        t = Thread(target=delete_peer, args=(_get_name(request.user), peer))
        t.start()
    return HttpResponse(status=201)


@login_required
def show_peer(request: HttpRequest, peer_id: int) -> HttpResponse:
    if not (peer := Peer.objects.filter(id=peer_id, owner=request.user).first()):
        return HttpResponseNotFound(json.dumps({
           "error": "not_found_or_forbidden",
        }))

    return HttpResponse(json.dumps({
        "peer": {
            "publicKey": peer.public_key,
            "tunnelIpAddresses": [
                f'{peer.tunnel_ipv4}/32',
                f'{peer.tunnel_ipv6}/128',
            ],
        },
        "remote": {
            "description": settings.WG_DESCRIPTION,
            "publicKey": settings.WG_PUBKEY,
            "endpoint": settings.WG_ENDPOINT,
        },
    }))
