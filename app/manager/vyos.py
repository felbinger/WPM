from typing import Union

from django.conf import settings
from pexpect.pxssh import ExceptionPxssh
from threading import Lock

from manager.models import Peer
from manager.router import Router

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
            if peer.psk:
                router.set(f"{wg_peer_path} preshared-key {peer.psk}")

            router.commit()
            router.save()
        except Exception as e:
            print(e)
        finally:
            router.exit()

            # set valid flag
            peer.valid = True
            peer.save()

    router.logout()


def delete_peer(name: str, peer: Peer):
    if not (router := _connect()):
        return

    # lock the configuration and delete the peer
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

            # delete peer from database
            peer.delete()

    router.logout()
