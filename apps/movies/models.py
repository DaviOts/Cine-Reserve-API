from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField()
    genre = models.CharField(max_length=100)
    poster_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    #use for indexing in BD to improve performance(CREATE INDEX)
    class Meta:
        indexes = [models.Index(fields=['title'])]


class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='sessions')
    room = models.CharField(max_length=50)
    starts_at = models.DateTimeField()
    total_seats = models.PositiveIntegerField()

    class Meta:
        indexes = [models.Index(fields=['movie', 'starts_at'])]
