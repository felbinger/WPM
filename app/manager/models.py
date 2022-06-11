from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Peer(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="peer_owner")
    name = models.CharField(max_length=32)
    tunnel_ipv4 = models.GenericIPAddressField()
    tunnel_ipv6 = models.GenericIPAddressField()
    public_key = models.CharField(max_length=44)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.public_key

    def tunnel_ips(self):
        return f'{self.tunnel_ipv4}, {self.tunnel_ipv6}'
