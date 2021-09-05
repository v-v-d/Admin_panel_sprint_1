import io
import typing as t
from enum import Enum

import aiosqlite
import asyncpg
from sqlite3 import Row

from pydantic.main import BaseModel

from settings import settings


class DBError(Exception):
    pass


class BaseEnum(Enum):
    @classmethod
    def all_names(cls):
        return [i.name for i in cls]


class TableNameEnum(str, BaseEnum):
    film_work = "film_work"
    genre_film_work = "genre_film_work"
    person_film_work = "person_film_work"
    genre = "genre"
    person = "person"


class TableNameWithFKEnum(str, BaseEnum):
    genre_film_work = "genre_film_work"
    person_film_work = "person_film_work"


class TableFKFieldsEnum(str, Enum):
    id = "id"
    film_work_id = "film_work_id"
    genre_id = "genre_id"
    person_id = "person_id"

    @staticmethod
    def get_fk(target_filed: "TableFKFieldsEnum") -> str:
        return f"fk_{target_filed}"


class SQLiteDBClient:
    ROWS_LIMIT = settings.ETL.CHUNK_SIZE
    DB_NAME = settings.ETL.SOURCE_DB_DSN

    class Decorators:
        @classmethod
        def db_session(cls, decorated: t.Callable):
            """Decorator for db connection sharing between methods."""

            async def wrapper(self, *args, **kwargs):
                async with aiosqlite.connect(SQLiteDBClient.DB_NAME) as database:
                    database.row_factory = aiosqlite.Row
                    kwargs["database"] = database
                    return await decorated(self, *args, **kwargs)

            return wrapper

    @Decorators.db_session
    async def fetch_page(
        self,
        table_name: str,
        offset: int,
        fields: t.Tuple[str] = None,
        mapping_schema: BaseModel = None,
        database: aiosqlite.core.Connection = None,
    ) -> t.Union[t.Iterable[Row], t.List[BaseModel]]:
        """
        Fetch data from db with pagination. Pass a queryset row mapper
        if you need to convert queryset.
        """
        fields = ", ".join(fields) if fields else "*"
        query = (
            f"SELECT {fields} FROM {table_name} limit $1 offset $2",
            (self.ROWS_LIMIT, offset),
        )

        try:
            async with database.execute_fetchall(*query) as queryset:
                if mapping_schema:
                    return self.by_pydantic(queryset, mapping_schema)

                return queryset
        except Exception as err:
            raise DBError(err)

    @staticmethod
    def by_pydantic(queryset: t.Iterable[Row], schema: BaseModel) -> t.List[BaseModel]:
        """Convert all rows in queryset with pydantic schema."""
        return [schema(**dict(row)) for row in queryset]

    async def fetch(
        self,
        table_name: str,
        fields: t.Tuple[str] = None,
        mapping_schema: t.Callable = None,
    ) -> t.AsyncGenerator[t.List[t.Dict[str, t.Any]], None]:
        """Fetch data by chunks with settings.ETL.CHUNK_SIZE"""
        offset = 0

        while True:
            result = await self.fetch_page(table_name, offset, fields, mapping_schema)

            if not result:
                break

            yield result

            offset += self.ROWS_LIMIT


class PostgresDBClient:
    class Decorators:
        @classmethod
        def db_session(cls, decorated: t.Callable):
            """Decorator for db connection sharing between methods."""

            async def wrapper(self, *args, **kwargs):
                async with self.db_pool.acquire() as db_pool:
                    kwargs["db_pool"] = db_pool
                    return await decorated(self, *args, **kwargs)

            return wrapper

    def __init__(
        self, null_value: t.Optional[str] = None, delimiter: t.Optional[str] = None
    ):
        self.null_value = null_value or "None"
        self.delimiter = delimiter or "|"
        self.db_pool: t.Optional[asyncpg.pool.Pool] = None

    async def init_db(self):
        """Initialize db connection pool."""
        self.db_pool = await asyncpg.create_pool(
            dsn=settings.ETL.TARGET_DB.DSN,
            min_size=settings.ETL.TARGET_DB.MIN_POOL_SIZE,
            max_size=settings.ETL.TARGET_DB.MAX_POOL_SIZE,
        )

    @Decorators.db_session
    async def insert_by_copy(
        self,
        table_name: TableNameEnum,
        data: t.List[t.Dict[str, t.Any]],
        db_pool: asyncpg.pool.Pool = None,
    ) -> None:
        """Insert data to db with COPY statement."""
        if not data:
            return

        columns = data[0].keys()
        values = [i.values() for i in data]

        data_string = "\n".join(
            self.delimiter.join([str(i) for i in v]) for v in values
        )

        data = io.BytesIO()
        data.write(data_string.encode())
        data.seek(0)

        try:
            await db_pool.copy_to_table(
                table_name,
                source=data,
                schema_name=settings.ETL.TARGET_DB.SCHEMA,
                columns=columns,
                delimiter=self.delimiter,
                null=self.null_value,
            )
        except Exception as err:
            raise DBError(err)

    @Decorators.db_session
    async def add_foreign_key(
        self,
        target_table_name: TableNameEnum,
        reference_table_name: TableNameEnum,
        fk_name: str,
        fk_field: TableFKFieldsEnum,
        db_pool: asyncpg.pool.Pool = None,
    ) -> None:
        """Add foreign key to target table."""
        query = f"""
        ALTER TABLE {settings.ETL.TARGET_DB.SCHEMA}.{target_table_name}
        ADD CONSTRAINT {fk_name}
        FOREIGN KEY ({fk_field}) 
        REFERENCES {settings.ETL.TARGET_DB.SCHEMA}.{reference_table_name} 
        ({TableFKFieldsEnum.id.value})
        """

        try:
            await db_pool.execute(query)
        except Exception as err:
            raise DBError(err)
