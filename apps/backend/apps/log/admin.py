from django.contrib import admin

from .models import CravingEvent, DailyEntry, Pulso, Slip


@admin.register(DailyEntry)
class DailyEntryAdmin(admin.ModelAdmin):
    list_display = ("data", "user", "humor", "energia", "craving_pico", "publicable")
    list_filter = ("user", "publicable")
    date_hierarchy = "data"


@admin.register(CravingEvent)
class CravingEventAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "substancia", "intensidade_pico", "gatilho")
    list_filter = ("user", "substancia", "gatilho", "publicable")
    search_fields = ("detalhes", "aprendizado")
    date_hierarchy = "timestamp"


@admin.register(Slip)
class SlipAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "substancia", "quantidade", "gatilho")
    list_filter = ("user", "substancia", "gatilho")
    date_hierarchy = "timestamp"


@admin.register(Pulso)
class PulsoAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "humor", "energia", "craving", "nota")
    list_filter = ("user", "humor", "energia")
    date_hierarchy = "timestamp"
