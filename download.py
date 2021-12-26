from constants import *
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import pandas as pd
from sqlalchemy import create_engine
from loguru import logger
from datetime import datetime
import argparse


if __name__ == '__main__':
    # parse user arguments
    parser = argparse.ArgumentParser(description='Download Binance data')
    parser.add_argument('-c', '--coins', type=str, nargs='+',
                        help='List of coins to download')
    args = parser.parse_args()

    # define basic parameters to download
    BASE_URL = 'https://data.binance.vision/data/spot/monthly/klines'
    symbols = args.coins if args.coins else SYMBOLS
    today = datetime.today()
    years = [i for i in range(2021, today.year + 1)]
    months = [i for i in range(1, 13)]
    db_name = 'ohlcv'
    symbols_usdt = [s + 'USDT' for s in symbols]

    # download and index data in loop
    logger.info(f"Importing data of coins: {symbols}")
    for i in range(len(symbols)):
        logger.info(f"Coin {i+1}/{len(symbols)}")
        s = symbols_usdt[i]
        for interval in INTERVALS:
            for year in years:
                for month in months:
                    # skip future months
                    if month >= today.month and year >= today.year:
                        continue
                    month = '0' + str(month) if month < 10 else month

                    # define binance url
                    filename = f'{s}-{interval}-{year}-{month}'
                    url = f'{BASE_URL}/{s}/{interval}/{filename}.zip'
                    csv_filename = f'{filename}.csv'
                    table_name = f'{symbols[i]}{interval}'
                    logger.info(f"Reading from url: {url}")

                    # retrieve zip file from binance
                    resp = urlopen(url)
                    zf = ZipFile(BytesIO(resp.read()))

                    # read csv file in zip
                    df = pd.read_csv(zf.open(csv_filename))
                    # df = pd.read_csv(zf.open(csv_filename, header=None))
                    df.drop(df.columns[6:], axis=1, inplace=True)
                    df.columns = ['Timestamp',
                                  'Open',
                                  'High',
                                  'Low',
                                  'Close',
                                  'Volume']

                    # convert unix timestamp to datetime
                    df['Timestamp'] = df['Timestamp'].apply(
                        lambda t: datetime.utcfromtimestamp(t / 1000))

                    # index in sqlite
                    engine = create_engine(f'sqlite:///{db_name}.db')
                    logger.info(f"Writing to database: {db_name} table: {table_name}")
                    df.to_sql(table_name, con=engine, if_exists='append')
