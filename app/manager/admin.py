from django.contrib import admin

from manager.models import Peer


class PeerListFilter(admin.SimpleListFilter):
    title = "Owner"
    parameter_name = 'owner'

    def lookups(self, request, model_admin):
        return [(peer.owner.username, peer.owner.get_full_name()) for peer in Peer.objects.all()]

    def queryset(self, request, queryset):
        qs = Peer.objects
        if self.value():
            qs = qs.filter(owner__username=self.value())
        return qs.all()


class PeerAdmin(admin.ModelAdmin):
    model = Peer
    list_display = ('owner', 'public_key', 'name', 'tunnel_ips', 'created',)
    list_filter = (PeerListFilter,)


admin.site.register(Peer, PeerAdmin)
