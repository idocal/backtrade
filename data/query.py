import pandas as pd
from sqlalchemy import create_engine, MetaData
from loguru import logger


class MissingData(Exception):
    pass


def get_ohlcv(asset: str, start: str, end: str, interval: str) -> pd.DataFrame:
    logger.info(f"Fetching data for {asset}...")
    intervals = ["1m", "5m", "15m", "1h", "4h", "1d"]
    if interval not in intervals:
        raise AttributeError(f"interval {interval} not in {intervals}")

    # create SQLite connection
    conn = create_engine("sqlite:///ohlcv.db")
    metadata = MetaData()
    metadata.reflect(bind=conn)

    # assert table exists
    table_name = f"{asset.upper()}{interval}"
    db_table_names = [t.name for t in metadata.sorted_tables]
    if table_name not in db_table_names:
        raise MissingData(f"Couldn't find table for {asset} and {interval}")

    # design query
    q = f"SELECT Timestamp, Open, High, Low, Close, Volume FROM {table_name} \
        WHERE Timestamp >= date('{start}') \
        AND Timestamp <= date('{end}')"

    logger.info("Done reading data!")
    return pd.read_sql(q, conn, index_col="Timestamp")
