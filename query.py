from constants import *
import pandas as pd
from sqlalchemy import create_engine, MetaData


def get_ohlcv(asset: str, start: str, end: str, interval: str):
    if interval not in INTERVALS:
        raise AttributeError(f"interval {interval} not in {INTERVALS}")

    # create SQLite connection
    conn = create_engine('sqlite:///ohlcv.db')
    metadata = MetaData()
    metadata.reflect(bind=conn)

    # assert table exists
    table_name = f"{asset.upper()}{interval}"
    db_table_names = [t.name for t in metadata.sorted_tables]
    if table_name not in db_table_names:
        raise AttributeError(f"Couldn't find table for {asset} and {interval}")

    # design query
    q = f"SELECT Timestamp, Open, High, Low, Close, Volume FROM {table_name} \
        WHERE Timestamp >= date('{start}') \
        AND Timestamp <= date('{end}')"

    return pd.read_sql(q, conn, index_col='Timestamp')
