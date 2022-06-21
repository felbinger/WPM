from typing import Union

from django.conf import settings
from pexpect.pxssh import ExceptionPxssh
from threading import Lock

from vymgmt import Router

from manager.models import Peer

firewall_locked = Lock()


def _connect() -> Union[Router, None]:
    router = settings.VYOS_ROUTER

    # establish connection to the router
    try:
        router.login()
    except ExceptionPxssh:
        print("Unable to establish connection to router!")
        return

    return router


def add_peer(name: str, peer: Peer):
    if not (router := _connect()):
        # delete peer because it can't create on the firewall
        peer.delete()
        return

    # lock the configuration and add the peer
    with firewall_locked:
        try:
            router.configure()

            router.set(f"firewall group address-group VPN-{name} address {peer.tunnel_ipv4}")
            router.set(f"firewall group ipv6-address-group VPN-{name}-6 address {peer.tunnel_ipv6}")
            wg_peer_path = f"interfaces wireguard {settings.WG_INTERFACE} peer {name}-{peer.name}"
            router.set(f"{wg_peer_path} allowed-ips {peer.tunnel_ipv4}/32")
            router.set(f"{wg_peer_path} allowed-ips {peer.tunnel_ipv6}/128")
            router.set(f"{wg_peer_path} persistent-keepalive 30")
            router.set(f"{wg_peer_path} pubkey {peer.public_key}")

            router.commit()
            router.save()
        except Exception as e:
            print(e)
            peer.delete()
        finally:
            router.exit()

    router.logout()


def delete_peer(name: str, peer: Peer):
    if not (router := _connect()):
        return

    # lock the configuration and add the peer
    with firewall_locked:
        try:
            router.configure()

            router.delete(f"firewall group address-group VPN-{name} address {peer.tunnel_ipv4}")
            router.delete(f"firewall group ipv6-address-group VPN-{name}-6 address {peer.tunnel_ipv6}")
            router.delete(f"interfaces wireguard {settings.WG_INTERFACE} peer {name}-{peer.name}")

            router.commit()
            router.save()
        except Exception as e:
            print(e)
        finally:
            router.exit()

    router.logout()
