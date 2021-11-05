from rest_framework import serializers

from movies.models import FilmWork


class FilmWorkSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    actors = serializers.SerializerMethodField()
    directors = serializers.SerializerMethodField()
    writers = serializers.SerializerMethodField()

    class Meta:
        model = FilmWork
        fields = (
            'id',
            'title',
            'description',
            'creation_date',
            'rating',
            'type',
            'subscription_required',
            'genres',
            'actors',
            'directors',
            'writers',
        )

    def get_genres(self, obj):
        return obj.genres_names

    def get_actors(self, obj):
        return obj.actors

    def get_directors(self, obj):
        return obj.directors

    def get_writers(self, obj):
        return obj.writers
