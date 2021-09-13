from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import viewsets

from api.v1.serializers import FilmWorkSerializer
from movies.models import FilmWork, FilmWorkPersonRole


class FilmWorkFilter(filters.FilterSet):
    genres = filters.CharFilter(
        field_name="genrefilmwork__genre__name", lookup_expr='icontains'
    )

    class Meta:
        model = FilmWork
        fields = ('genres', )


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
    filter_backends = (filters.filters.SearchFilter, filters.DjangoFilterBackend)
    search_fields = ('title', 'description')
    filterset_class = FilmWorkFilter
