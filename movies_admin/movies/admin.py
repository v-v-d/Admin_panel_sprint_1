from django.contrib import admin
from .models import FilmWork, Person, Genre


class PageLimit:
    list_per_page = 20


class NonExtra:
    extra = 0


class PersonFilmWorkInline(NonExtra, admin.TabularInline):
    model = FilmWork.persons.through
    raw_id_fields = ('person', 'film_work')


class GenreFilmWorkInline(NonExtra, admin.TabularInline):
    model = FilmWork.genres.through
    raw_id_fields = ('genre', 'film_work')


@admin.register(FilmWork)
class FilmWorkAdmin(PageLimit, admin.ModelAdmin):
    list_display = ('title', 'type', 'creation_date', 'rating', 'subscription_required')
    list_filter = ('type', 'subscription_required')
    search_fields = ('title', 'description', 'type')
    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating', 'subscription_required'
    )
    inlines = (GenreFilmWorkInline, PersonFilmWorkInline)


@admin.register(Person)
class PersonAdmin(PageLimit, admin.ModelAdmin):
    search_fields = ('full_name', )
    inlines = (PersonFilmWorkInline, )


@admin.register(Genre)
class GenreAdmin(PageLimit, admin.ModelAdmin):
    search_fields = ('name', 'description')
    inlines = (GenreFilmWorkInline, )
