from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.filters import SearchFilter

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
    serializer_class = FilmWorkSerializer
    filter_backends = (SearchFilter, filters.DjangoFilterBackend)
    search_fields = ('title', 'description')
    filterset_class = FilmWorkFilter

    def get_queryset(self) -> QuerySet:
        return (
            FilmWork.objects
            .prefetch_related('genres', 'persons')
            .annotate(
                genres_names=ArrayAgg(
                    'genrefilmwork__genre__name',
                    distinct=True
                ),
                actors=self._aggregate_person(FilmWorkPersonRole.ACTOR),
                directors=self._aggregate_person(FilmWorkPersonRole.DIRECTOR),
                writers=self._aggregate_person(FilmWorkPersonRole.WRITER),
            )
            .all()
        )

    @staticmethod
    def _aggregate_person(role: FilmWorkPersonRole) -> ArrayAgg:
        return ArrayAgg(
            'personfilmwork__person__full_name',
            filter=Q(personfilmwork__role=role),
            distinct=True
        )
