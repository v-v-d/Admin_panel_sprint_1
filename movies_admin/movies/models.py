from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class AbstractUUID(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        abstract = True


class AbstractTimeStamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Genre(AbstractTimeStamped, AbstractUUID):
    name = models.CharField(_('title'), max_length=255, blank=True)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        verbose_name = _('genre')
        verbose_name_plural = _('genres')
        db_table = '"content"."genre"'

    def __str__(self):
        return self.name


class Person(AbstractTimeStamped, AbstractUUID):
    full_name = models.CharField(_('full name'), max_length=255, blank=True)
    birth_date = models.DateField(_('birth date'), blank=True)

    class Meta:
        verbose_name = _('person')
        verbose_name_plural = _('persons')
        db_table = '"content"."person"'

    def __str__(self):
        return self.full_name


class FilmWorkType(models.TextChoices):
    MOVIE = 'movie', _('movie')
    TV_SHOW = 'tv_show', _('TV Show')


class FilmWork(AbstractTimeStamped, AbstractUUID):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    creation_date = models.DateField(_('creation date'), blank=True)
    certificate = models.CharField(_('certificate'), max_length=255, blank=True)
    file_path = models.FileField(_('file'), upload_to='film_works/', blank=True)
    rating = models.FloatField(_('rating'), validators=[MinValueValidator(0)], blank=True)
    type = models.CharField(_('type'), max_length=20, choices=FilmWorkType.choices, default=FilmWorkType.MOVIE)
    genres = models.ManyToManyField(Genre, through='GenreFilmWork')
    persons = models.ManyToManyField(Person, through='PersonFilmWork')

    class Meta:
        verbose_name = _('film work')
        verbose_name_plural = _('film works')
        db_table = '"content"."film_work"'

    def __str__(self):
        return self.title


class GenreFilmWork(AbstractUUID):
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '"content"."genre_film_work"'

    def __str__(self):
        return str(self.pk)


class FilmWorkPersonRole(models.TextChoices):
    ACTOR = 'actor', _('actor')
    WRITER = 'writer', _('writer')
    DIRECTOR = 'director', _('director')


class PersonFilmWork(AbstractUUID):
    film_work = models.ForeignKey(FilmWork, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.DO_NOTHING)
    role = models.CharField(_('role'), max_length=20, choices=FilmWorkPersonRole.choices, default=FilmWorkPersonRole.ACTOR)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = '"content"."person_film_work"'

    def __str__(self):
        return str(self.pk)
