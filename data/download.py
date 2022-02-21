from .providers import get_provider
from data import DB_NAME

import time
from sqlalchemy import create_engine
from loguru import logger
import datetime
from typing import List, Union


def timestamp_from_str(date: datetime.date) -> datetime.datetime:
    date = time.mktime(date.timetuple())
    return datetime.datetime.fromtimestamp(date)


def months_from_range(start_time, end_time) -> List[str]:
    curr_year = start_time.year
    curr_start_month = start_time.month
    months = []
    is_last_year = False
    while not is_last_year:
        is_last_year = curr_year == end_time.year
        last_month = end_time.month if is_last_year else 12
        for i in range(curr_start_month, last_month + 1):
            month = "0" + str(i) if i < 10 else i
            months.append(f"{month}-{curr_year}")
        curr_year += 1
        curr_start_month = 1

    return months


def download(
    provider_name: str,
    symbol: Union[list[str], str],
    intervals: Union[list[str], str],
    start: datetime.date,
    end: datetime.date,
):
    if type(symbol) == str:
        symbol = [symbol]

    if type(intervals) == str:
        intervals = [intervals]

    start = timestamp_from_str(start)
    end = timestamp_from_str(end)
    data_months = months_from_range(start, end)

    db_name = DB_NAME

    # TODO: note that the code assume the use of USDT
    symbol_usdt = [s + "USDT" for s in symbol]

    # download and index data in loop
    logger.info(f"Importing data of coins: {symbol}")
    for i in range(len(symbol)):
        logger.info(f"Coin {i + 1}/{len(symbol)}")
        curr_symbol = symbol_usdt[i]  # TODO: USDT
        for interval in intervals:
            for data_month in data_months:
                month, year = data_month.split("-")

                # retrieve data file from curr_provider
                # NOTE: retrieve monthly data
                curr_provider = get_provider(provider_name, logger)
                df = curr_provider.retrieve_data(curr_symbol, interval, year, month)
                # index in sqlite
                table_name = f"{symbol[i]}{interval}"  # TODO: symbol[i] instead of curr_symbol assumes use of USDT
                engine = create_engine(f"sqlite:///{db_name}.db")
                logger.info(f"Writing to database: {db_name} table: {table_name}")
                df.to_sql(table_name, con=engine, if_exists="append")
