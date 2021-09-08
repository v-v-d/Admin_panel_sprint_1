import asyncio
import typing as t
from abc import ABC, abstractmethod
from logging import getLogger

from pydantic.main import BaseModel

from db_clients import (
    TableNameEnum,
    SQLiteDBClient,
    PostgresDBClient,
    TableNameWithFKEnum,
    TableFKFieldsEnum,
    DBError,
)
from schemas import SchemaByTableEnum
from settings import settings


logger = getLogger(__name__)


class ETLError(Exception):
    pass


class ETL(ABC):
    @abstractmethod
    def extract(self, *args, **kwargs) -> t.AsyncIterator[None]:
        pass

    @abstractmethod
    def transform(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def load(self, *args, **kwargs) -> None:
        pass


class MovieETL(ETL):
    def __init__(self):
        self.source_db_client: SQLiteDBClient = SQLiteDBClient()
        self.target_db_client: PostgresDBClient = PostgresDBClient()

        self.raw_data: t.Optional[t.List[BaseModel]] = []
        self.transformed_data: t.Optional[t.List[t.Dict[str, t.Any]]] = []

    async def run(self):
        """Run etl by chunks with settings.ETL.CHUNK_SIZE."""
        try:
            async for table_name in self.extract():
                await self.transform()
                await self.load(table_name)

            await self.after_load()
        except Exception as err:
            raise ETLError(err)

    async def extract(self) -> t.AsyncIterator[TableNameEnum]:
        """
        Extract data from source to in-memory storage named self.raw_data.
        """
        for table_name in TableNameEnum.all_names():
            schema = getattr(SchemaByTableEnum, table_name)

            async for chunk in self.source_db_client.fetch(
                table_name, mapping_schema=schema.value
            ):
                logger.debug(
                    "Success extraction data from %s table, chunk len %s",
                    table_name,
                    len(chunk),
                )

                for item in chunk:
                    if len(self.raw_data) == settings.ETL.CHUNK_SIZE:
                        yield table_name
                        self.raw_data = []

                    self.raw_data.append(item)

            yield table_name
            self.raw_data = []

    async def transform(self) -> None:
        """
        Transform extracted data and save it to in-memory storage named
        self.transformed_data.
        """
        self.transformed_data = [data.dict() for data in self.raw_data]

    async def load(self, table_name: TableNameEnum) -> None:
        """Load transformed data to target."""
        if not self.transformed_data:
            return

        try:
            await self.target_db_client.insert_by_copy(
                table_name, self.transformed_data
            )
        except DBError as err:
            logger.error("Failed to load data to db! Error: %s", err, exc_info=True)
            # skip this chunk
            return

    async def after_load(self):
        """Call it when the etl is done."""
        try:
            for table_name in TableNameWithFKEnum.all_names():
                await self.target_db_client.add_foreign_key(
                    target_table_name=table_name,
                    reference_table_name=TableNameEnum.film_work.value,
                    fk_name=TableFKFieldsEnum.get_fk(
                        TableFKFieldsEnum.film_work_id.value
                    ),
                    fk_field=TableFKFieldsEnum.film_work_id.value,
                    on_delete_cascade=True,
                )

                if table_name == TableNameEnum.genre_film_work:
                    await self.target_db_client.add_foreign_key(
                        target_table_name=table_name,
                        reference_table_name=TableNameEnum.genre.value,
                        fk_name=TableFKFieldsEnum.get_fk(
                            TableFKFieldsEnum.genre_id.value
                        ),
                        fk_field=TableFKFieldsEnum.genre_id.value,
                    )
                    continue

                await self.target_db_client.add_foreign_key(
                    target_table_name=table_name,
                    reference_table_name=TableNameEnum.person.value,
                    fk_name=TableFKFieldsEnum.get_fk(TableFKFieldsEnum.person_id.value),
                    fk_field=TableFKFieldsEnum.person_id.value,
                )
        except DBError as err:
            logger.error("Failed to set foreign keys. Error: %s", err, exc_info=True)


async def run_movie_etl():
    etl = MovieETL()
    await etl.target_db_client.init_db()

    try:
        await etl.run()
    except ETLError as err:
        logger.error("ETL failed! Error: %s", err, exc_info=True)
        return

    logger.info("All data has been processed.")


if __name__ == "__main__":
    asyncio.run(run_movie_etl())
