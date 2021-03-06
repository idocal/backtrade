from data import DB_URL

import datetime

import pandas as pd
from sqlalchemy import create_engine, MetaData
from loguru import logger


class MissingDataError(Exception):
    pass


def get_ohlcv(
    asset: str, start: datetime.date, end: datetime.date, interval: str
) -> pd.DataFrame:
    logger.info(f"Fetching local data for {asset}...")

    # create SQLite connection
    conn = create_engine(DB_URL)
    metadata = MetaData()
    metadata.reflect(bind=conn)

    # assert table exists
    table_name = f"{asset.upper()}{interval}"  # TODO: assumes the use of USDT
    db_table_names = [t.name for t in metadata.sorted_tables]
    logger.info(table_name)
    logger.info(db_table_names)
    if table_name not in db_table_names:
        raise MissingDataError(f"Couldn't find table for {asset} - {interval}")

    start_date = start.strftime("%Y-%m-%d")
    end_date = end.strftime("%Y-%m-%d")

    # TODO: fix query such that it checks all dates in between start and end
    # design query
    q = f"SELECT Timestamp, Open, High, Low, Close, Volume FROM {table_name} \
        WHERE Timestamp >= date('{start_date}') \
        AND Timestamp <= date('{end_date}')"

    result = pd.read_sql(q, conn, index_col="Timestamp")
    if len(result) == 0:
        raise MissingDataError(
            f"Couldn't find data for dates {start} to {end} for {asset} - {interval}"
        )
    logger.info("Done reading data!")

    return result
