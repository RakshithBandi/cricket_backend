from django.contrib import admin
from .models import Player, Team

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'village', 'role', 'team', 'bid_amount', 'phone', 'created_at')
    list_filter = ('role', 'team', 'village', 'created_at')
    search_fields = ('name', 'village', 'phone', 'team')
    ordering = ('-created_at',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'total_budget')
    search_fields = ('name',)
