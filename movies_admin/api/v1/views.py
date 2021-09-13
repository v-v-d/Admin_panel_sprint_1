from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q

from api.v1.serializers import FilmWorkSerializer
from movies.models import FilmWork, FilmWorkPersonRole
from rest_framework import viewsets


class FilmWorkViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        FilmWork.objects
        .prefetch_related('genres', 'persons')
        .annotate(
            genres_names=ArrayAgg(
                'genrefilmwork__genre__name',
                distinct=True
            ),
            actors=ArrayAgg(
                'personfilmwork__person__full_name',
                filter=Q(personfilmwork__role=FilmWorkPersonRole.ACTOR),
                distinct=True
            ),
            directors=ArrayAgg(
                'personfilmwork__person__full_name',
                filter=Q(personfilmwork__role=FilmWorkPersonRole.DIRECTOR),
                distinct=True
            ),
            writers=ArrayAgg(
                'personfilmwork__person__full_name',
                filter=Q(personfilmwork__role=FilmWorkPersonRole.WRITER),
                distinct=True
            ),
        )
        .all()
    )
    serializer_class = FilmWorkSerializer
