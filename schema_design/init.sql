-- DROP SCHEMA IF EXISTS content CASCADE;
-- DROP DATABASE IF EXISTS movies;

-- Создание БД movies;
CREATE DATABASE movies;

-- Подключение к созданной БД movies;
\connect movies;

-- Создание отдельной схемы для контента:
CREATE SCHEMA IF NOT EXISTS content;

-- Кинопроизведения:
CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    creation_date DATE,
    certificate VARCHAR(255),
    file_path VARCHAR(255),
    rating FLOAT,
    type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ON content.film_work(creation_date, rating);

-- Жанры кинопроизведений:
CREATE TABLE IF NOT EXISTS content.genre (
    id uuid PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- m:m Жанры - Кинопроизведения:
CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid,
    genre_id uuid,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX film_work_genre ON content.genre_film_work (film_work_id, genre_id);

-- Персоны (актёр/режисёр/сценарист):
CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name VARCHAR(255),
    birth_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- m:m Персоны - Кинопроизведения:
CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid,
    person_id uuid,
    role VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX film_work_person_role ON content.person_film_work (film_work_id, person_id, role);
