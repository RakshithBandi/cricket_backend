from rest_framework import serializers
from .models import Player, Team

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            'id',
            'name',
            'village',
            'role',
            'phone',
            'team',
            'bid_amount',
            'first_name',
            'last_name',
            'email',
            'city',
            'state',
            'jersey_number',
            'matches_played',
            'total_runs',
            'wickets_taken',
            'highest_score',
            'best_bowling',
            'bio',
            'created_at',
            'updated_at',
        ]

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'total_budget']
