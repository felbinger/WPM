from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Peer(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="peer_owner")
    name = models.CharField(max_length=32, unique=True)
    tunnel_ipv4 = models.GenericIPAddressField()
    tunnel_ipv6 = models.GenericIPAddressField()
    public_key = models.CharField(max_length=44)
    psk = models.CharField(max_length=44, default=None, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    valid = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.public_key

    def tunnel_ips(self) -> str:
        return f'{self.tunnel_ipv4}, {self.tunnel_ipv6}'
