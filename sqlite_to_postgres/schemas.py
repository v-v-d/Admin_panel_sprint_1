import typing as t
from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from pydantic.types import UUID4


class FilmWorkSchema(BaseModel):
    id: UUID4
    title: str
    description: t.Optional[str]
    creation_date: t.Optional[str]
    certificate: t.Optional[str]
    file_path: t.Optional[str]
    rating: t.Optional[float] = 0.0
    type: t.Optional[str]
    created_at: datetime
    updated_at: datetime
    subscription_required: bool


class GenreFilmWorkSchema(BaseModel):
    id: UUID4
    film_work_id: UUID4
    genre_id: UUID4
    created_at: datetime


class PersonFilmWorkSchema(BaseModel):
    id: UUID4
    film_work_id: UUID4
    person_id: UUID4
    role: str
    created_at: datetime


class GenreSchema(BaseModel):
    id: UUID4
    name: str
    description: t.Optional[str]
    created_at: datetime
    updated_at: datetime


class PersonSchema(BaseModel):
    id: UUID4
    full_name: str
    birth_date: t.Optional[datetime]
    created_at: datetime
    updated_at: datetime


class SchemaByTableEnum(Enum):
    film_work = FilmWorkSchema
    genre_film_work = GenreFilmWorkSchema
    person_film_work = PersonFilmWorkSchema
    genre = GenreSchema
    person = PersonSchema
