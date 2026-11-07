from django.db import models

class Player(models.Model):
    ROLE_CHOICES = [
        ('Batsman', 'Batsman'),
        ('Bowler', 'Bowler'),
        ('All-Rounder', 'All-Rounder'),
    ]

    # Required fields requested by user
    name = models.CharField(max_length=150, default='')
    village = models.CharField(max_length=100, default='Mallinamadugu')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='All-Rounder')
    phone = models.CharField(max_length=25, default='')
    team = models.CharField(max_length=50, blank=True, null=True, default='')
    bid_amount = models.IntegerField(default=0) # Amount spent when buying player in action

    # Optional extended fields
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    jersey_number = models.IntegerField(null=True, blank=True)
    primary_role = models.CharField(max_length=50, blank=True, null=True)

    matches_played = models.IntegerField(default=0)
    total_runs = models.IntegerField(default=0)
    wickets_taken = models.IntegerField(default=0)
    highest_score = models.CharField(max_length=20, default='0', blank=True)
    best_bowling = models.CharField(max_length=20, default='0/0', blank=True)

    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.name and not self.first_name:
            parts = self.name.split(' ', 1)
            self.first_name = parts[0]
            self.last_name = parts[1] if len(parts) > 1 else ''
        if not self.name and self.first_name:
            self.name = f"{self.first_name} {self.last_name or ''}".strip()
        if not self.village and self.city:
            self.village = self.city
        if not self.primary_role and self.role:
            self.primary_role = self.role
        if not self.role and self.primary_role:
            self.role = self.primary_role
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.village}) - {self.role} [{self.team or 'Unsold'}]"

class Team(models.Model):
    name = models.CharField(max_length=50, unique=True)
    total_budget = models.IntegerField(default=100000)

    def __str__(self):
        return f"{self.name} (Budget: {self.total_budget})"
