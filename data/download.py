import time
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import pandas as pd
from sqlalchemy import create_engine
from loguru import logger
from datetime import datetime
import argparse
from typing import List

BASE_URL = "https://data.binance.vision/data/spot/monthly/klines"


def timestamp_from_str(date: str) -> datetime:
    try:
        date = time.strptime(date, "%m-%Y")
    except ValueError:
        date = time.strptime(date, "%Y-%m-%d")

    date = time.struct_time(date)
    date = time.mktime(date)
    return datetime.fromtimestamp(date)


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


def download(symbols, intervals, start_time, end_time):
    start_time = timestamp_from_str(start_time)
    end_time = timestamp_from_str(end_time)
    data_months = months_from_range(start_time, end_time)

    # years = [i for i in range(start_time.year, end_time.year + 1)]
    # months = [i for i in range(1, 13)]

    db_name = "ohlcv"
    symbols_usdt = [s + "USDT" for s in symbols]

    # download and index data in loop
    logger.info(f"Importing data of coins: {symbols}")
    for i in range(len(symbols)):
        logger.info(f"Coin {i + 1}/{len(symbols)}")
        s = symbols_usdt[i]
        for interval in intervals:
            for data_month in data_months:
                month, year = data_month.split("-")

                # define binance url
                filename = f"{s}-{interval}-{year}-{month}"
                url = f"{BASE_URL}/{s}/{interval}/{filename}.zip"
                csv_filename = f"{filename}.csv"
                table_name = f"{symbols[i]}{interval}"
                logger.info(f"Reading from url: {url}")

                # retrieve zip file from binance
                resp = urlopen(url)
                zf = ZipFile(BytesIO(resp.read()))

                # read csv file in zip
                df = pd.read_csv(zf.open(csv_filename), header=None)
                df.drop(df.columns[6:], axis=1, inplace=True)
                df.columns = ["Timestamp", "Open", "High", "Low", "Close", "Volume"]

                # convert unix timestamp to datetime
                df["Timestamp"] = df["Timestamp"].apply(
                    lambda t: datetime.utcfromtimestamp(t / 1000)
                )

                # index in sqlite
                engine = create_engine(f"sqlite:///{db_name}.db")
                logger.info(f"Writing to database: {db_name} table: {table_name}")
                df.to_sql(table_name, con=engine, if_exists="append")


if __name__ == "__main__":
    # parse user arguments
    parser = argparse.ArgumentParser(description="Download Binance data")
    parser.add_argument(
        "-c", "--coins", type=str, nargs="+", help="List of coins to download"
    )
    parser.add_argument("-i", "--interval", type=str, help="Interval between each tick")
    parser.add_argument(
        "-s", "--start", type=str, help="Start day of trade, format is MM-YYYY"
    )
    parser.add_argument(
        "-e", "--end", type=str, help="End day of trade, format is MM-YYYY"
    )
    args = parser.parse_args()

    # define basic parameters to download
    all_symbols = ["BTC", "ETH", "ETC", "BNB", "XRP", "LTC"]
    all_intervals = ["1m", "5m", "15m", "1h", "4h", "1d"]

    intervals = [args.interval] if args.interval else all_intervals
    symbols = args.coins if args.coins else all_symbols
    start_time = args.start
    end_time = args.end

    download(symbols, intervals, start_time, end_time)
