import binascii
from base64 import b64decode, b64encode
from ipaddress import IPv6Network, IPv6Address, IPv4Network
import random
from string import printable, ascii_uppercase, digits

from django.contrib.auth.models import User

from manager.models import Peer


def _is_base_64(s: str) -> bool:
    try:
        return b64encode(b64decode(s)).decode() == s
    except binascii.Error:
        return False


def _get_next_ipv4_address(ipv4_network: str) -> str:
    used_ipv4_addresses = [str(p.tunnel_ipv4) for p in Peer.objects.all()]

    # vyos itself has the first address
    used_ipv4_addresses.append(str(next(IPv4Network(ipv4_network).hosts())))

    for addr in IPv4Network(ipv4_network).hosts():
        if str(addr) not in used_ipv4_addresses:
            # return first address which is not in use
            return str(addr)


def _get_random_ipv6_address(ipv6_prefix: str) -> str:
    used_ipv6_addresses = [str(p.tunnel_ipv6) for p in Peer.objects.all()]

    # vyos itself has the first address
    used_ipv6_addresses.append(str(next(IPv6Network(ipv6_prefix).hosts())))

    def _get_random():
        # Which of the network.num_addresses we want to select?
        addr_no = random.randint(0, IPv6Network(ipv6_prefix).num_addresses)
        # Create the random address by converting to a 128-bit integer, adding addr_no and converting back
        network_int = int.from_bytes(IPv6Network(ipv6_prefix).network_address.packed, byteorder="big")
        addr_int = network_int + addr_no
        return str(IPv6Address(addr_int.to_bytes(16, byteorder="big")))

    while (ipv6_addr := _get_random()) in used_ipv6_addresses:
        pass
    return ipv6_addr


# replace the invalid characters in the name
def _check_and_replace_name(name: str) -> str:
    for k, v in {
        'Ä': 'AE',
        'Ö': 'OE',
        'Ü': 'UE',
        'ß': 'SS',
    }.items():
        name = name.replace(k, v)

    for c in printable.replace(ascii_uppercase + digits, ""):
        if c not in name:
            continue
        print(f"WARNING: name string contains character {c}")
        name.replace(c, '')

    return name


def _get_name(user: User) -> str:
    return f'{_check_and_replace_name(user.first_name.upper())}-{_check_and_replace_name(user.last_name.upper())}'
