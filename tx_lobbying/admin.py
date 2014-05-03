from django.contrib import admin

from . import models


class InterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name', 'address__city', 'address__state')
admin.site.register(models.Interest, InterestAdmin)


class LobbyingInline(admin.TabularInline):
    can_delete = False
    extra = 0

    def get_readonly_fields(self, request, obj=None):
        # fix the order is all wonk
        return list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many]
        ) - set(self.exclude))

    def has_add_permission(self, request):
        # Nobody is allowed to add
        return False


class RegistrationReportInline(LobbyingInline):
    exclude = ('raw', )
    model = models.RegistrationReport


class CoverSheetInline(LobbyingInline):
    exclude = ('raw', )
    model = models.Coversheet


class LobbyistAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated_at')
    search_fields = ('name', )
    inlines = (RegistrationReportInline, CoverSheetInline, )

admin.site.register(models.Lobbyist, LobbyistAdmin)
