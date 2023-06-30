from django.contrib import admin
from django.contrib.sessions.models import Session
from .models import Client,Notification

class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']
admin.site.register(Session)
admin.site.register(Client)
admin.site.register(Notification)