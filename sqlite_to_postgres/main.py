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

    async def run(self) -> None:
        """Run etl concurrently."""
        # Спасибо за комменты и особенно за коммент про асинхронность)
        # Я как-то действительно упустил этот момент
        tasks: t.List[asyncio.Task] = []

        for table_name in TableNameEnum.all_names():
            tasks.append(asyncio.create_task(self.run_etl_by_table_name(table_name)))

        await asyncio.gather(*tasks, return_exceptions=True)

        await self.after_load()

    async def run_etl_by_table_name(self, table_name: TableNameEnum):
        """Run etl by table name."""
        try:
            async for chunk in self.extract(table_name):
                transformed_data = await self.transform(chunk)
                await self.load(table_name, transformed_data)
        except Exception as err:
            raise ETLError from err

    async def extract(
        self, table_name: TableNameEnum
    ) -> t.AsyncIterator[t.List[BaseModel]]:
        """Extract data from source."""
        schema = getattr(SchemaByTableEnum, table_name)

        async for chunk in self.source_db_client.fetch(
            table_name, mapping_schema=schema.value
        ):
            logger.debug(
                "Success extraction data from %s table, chunk len %s",
                table_name,
                len(chunk),
            )

            yield chunk

    async def transform(
        self, raw_data: t.List[BaseModel]
    ) -> t.List[t.Dict[str, t.Any]]:
        """Transform extracted data."""
        # В комменте был вопрос, поэтому я отвечаю. Не очень хочется связывать
        # пидантик схемы с клиентом к бд, т.к. в схемах может быть дополнительная
        # логика по трансформации данных. Либо в этом методе может быть такая
        # логика. Кажется, что логичней будет в клиент к бд передавать уже обработанные
        # примитивные данные. В клиенте к sqlite я использовал конвертацию словарей в
        # пидантик, но сделал это как необязательное дополнение.
        return [data.dict() for data in raw_data]

    async def load(
        self, table_name: TableNameEnum, transformed_data: t.List[t.Dict[str, t.Any]]
    ) -> None:
        """Load transformed data to target."""
        if not transformed_data:
            return

        try:
            await self.target_db_client.insert_by_copy(table_name, transformed_data)
            logger.debug(
                "Success load data to %s table, chunk len %s",
                table_name,
                len(transformed_data),
            )
        except DBError as err:
            logger.exception("Failed to load data to db! Error: %s", err)
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
            logger.exception("Failed to set foreign keys. Error: %s", err)


async def run_movie_etl():
    etl = MovieETL()
    await etl.source_db_client.init_db()
    await etl.target_db_client.init_db()

    try:
        await etl.run()
    except ETLError as err:
        logger.exception("ETL failed! Error: %s", err)
        return
    finally:
        await etl.source_db_client.close_db()

    logger.info("All data has been processed.")


if __name__ == "__main__":
    asyncio.run(run_movie_etl())
