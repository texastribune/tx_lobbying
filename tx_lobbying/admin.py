from django.contrib import admin

from . import models


admin.site.register(models.Interest)


class LobbyistAdmin(admin.ModelAdmin):
    list_display = ('name', 'updated_at')
    search_fields = ('name', )

admin.site.register(models.Lobbyist, LobbyistAdmin)
