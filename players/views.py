import csv
from django.http import HttpResponse
from django.db.models import Q, Count, Max, Sum
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Player, Team
from .serializers import PlayerSerializer, TeamSerializer
from .pdf_generator import generate_team_pdf

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def list(self, request, *args, **kwargs):
        official_teams = [
            'Krishi Knight Riders',
            'Vegetable Titans',
            'Red Chilli Blasters',
            'Silk Rising Heros',
            'Mango Icons',
            'Groundnuts Super Kings'
        ]
        if Team.objects.count() < 6:
            for name in official_teams:
                Team.objects.get_or_create(name=name, defaults={'total_budget': 100000})
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        team = self.get_object()
        players = Player.objects.filter(team=team.name)
        pdf_bytes = generate_team_pdf(team, players)

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f"{team.name.replace(' ', '_')}_Players_List.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    @action(detail=False, methods=['get'])
    def export_team_pdf(self, request):
        team_name = request.query_params.get('team', '').strip()
        team_id = request.query_params.get('id', '').strip()

        team = None
        if team_id:
            team = Team.objects.filter(id=team_id).first()
        elif team_name:
            team = Team.objects.filter(name__iexact=team_name).first()

        if not team:
            return Response({'error': 'Team not found'}, status=status.HTTP_404_NOT_FOUND)

        players = Player.objects.filter(team=team.name)
        pdf_bytes = generate_team_pdf(team, players)

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = f"{team.name.replace(' ', '_')}_Players_List.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def get_queryset(self):
        qs = Player.objects.all()
        search = self.request.query_params.get('search', '').strip()
        role = self.request.query_params.get('role', '').strip()
        batting_style = self.request.query_params.get('batting_style', '').strip()
        bowling_style = self.request.query_params.get('bowling_style', '').strip()
        experience = self.request.query_params.get('experience', '').strip()
        status_filter = self.request.query_params.get('status', '').strip()
        sort_by = self.request.query_params.get('sort_by', '-created_at').strip()

        if search:
            qs = qs.filter(
                Q(name__icontains=search) |
                Q(village__icontains=search) |
                Q(role__icontains=search) |
                Q(phone__icontains=search)
            )

        if role:
            qs = qs.filter(role__iexact=role)
        if batting_style:
            qs = qs.filter(batting_style__iexact=batting_style)
        if bowling_style:
            qs = qs.filter(bowling_style__iexact=bowling_style)
        if experience:
            qs = qs.filter(experience_level__iexact=experience)
        if status_filter:
            qs = qs.filter(status__iexact=status_filter)

        valid_sorts = [
            'created_at', '-created_at',
            'jersey_number', '-jersey_number',
            'total_runs', '-total_runs',
            'wickets_taken', '-wickets_taken',
            'matches_played', '-matches_played',
            'first_name', '-first_name'
        ]
        if sort_by in valid_sorts:
            qs = qs.order_by(sort_by)
        else:
            qs = qs.order_by('-created_at')

        return qs

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_players = Player.objects.count()
        role_counts = dict(Player.objects.values('primary_role').annotate(count=Count('id')).values_list('primary_role', 'count'))
        exp_counts = dict(Player.objects.values('experience_level').annotate(count=Count('id')).values_list('experience_level', 'count'))
        
        top_runs = Player.objects.order_by('-total_runs')[:5]
        top_wickets = Player.objects.order_by('-wickets_taken')[:5]

        total_runs_scored = Player.objects.aggregate(Sum('total_runs'))['total_runs__sum'] or 0
        total_wickets_taken = Player.objects.aggregate(Sum('wickets_taken'))['wickets_taken__sum'] or 0
        total_matches = Player.objects.aggregate(Sum('matches_played'))['matches_played__sum'] or 0

        return Response({
            'total_players': total_players,
            'role_distribution': role_counts,
            'experience_distribution': exp_counts,
            'total_runs_scored': total_runs_scored,
            'total_wickets_taken': total_wickets_taken,
            'total_matches': total_matches,
            'top_run_scorers': PlayerSerializer(top_runs, many=True, context={'request': request}).data,
            'top_wicket_takers': PlayerSerializer(top_wickets, many=True, context={'request': request}).data,
        })

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cricket_players_roster.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'First Name', 'Last Name', 'Email', 'Phone', 'City', 'State',
            'Jersey #', 'Primary Role', 'Batting Style', 'Bowling Style',
            'Experience Level', 'Preferred Position', 'Matches', 'Runs', 'Highest Score',
            'Wickets', 'Best Bowling', 'Strike Rate', 'Economy', 'Status'
        ])

        for p in self.get_queryset():
            writer.writerow([
                p.id, p.first_name, p.last_name, p.email, p.phone, p.city, p.state,
                p.jersey_number or '', p.primary_role, p.batting_style, p.bowling_style,
                p.experience_level, p.preferred_batting_pos, p.matches_played, p.total_runs,
                p.highest_score, p.wickets_taken, p.best_bowling, p.strike_rate,
                p.economy_rate, p.status
            ])

        return response

    @action(detail=False, methods=['post'])
    def seed_data(self, request):
        return Response({
            "message": "Real database records active.",
            "total_players": Player.objects.count()
        })
