import os
import time
from datetime import datetime, timedelta
import pandas as pd
import requests
import pytz


API_KEY  = "<API KEY>" # Need paid plan to get 10yr dataset

 # Configure the time range to collect data
START_DATE = "2015-01-01"
END_DATE = "2025-08-15"

utc_tz = pytz.timezone('UTC')
nyc_tz = pytz.timezone('America/New_York')


def get_polygon_data(url=None, ticker="", multiplier=1, timespan="minute",
                       from_date=START_DATE, to_date=END_DATE, adjusted=False):

    if ticker == "":
        raise ValueError("Invalid ticker symbol")    

    """Retrieve intraday aggregate data from Polygon.io."""
    if url is None:
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
        params = {
            "adjusted": "true" if adjusted else "false",
            "sort": "asc",
            "limit": 50000,
            "apiKey": API_KEY
        }
        response = requests.get(url, params=params)
    else:
        if "apiKey" not in url:
            url = f"{url}&apiKey={API_KEY}" if "?" in url else f"{url}?apiKey={API_KEY}"
        response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None, None

    data = response.json()
    next_url = data.get("next_url")
    if next_url and "apiKey" not in next_url:
        next_url = f"{next_url}&apiKey={API_KEY}" if "?" in next_url else f"{next_url}?apiKey={API_KEY}"

    return data.get("results", []), next_url


def convert_to_backtesting_format(results):
    """Convert Polygon minute aggregate results to following columns

    Columns: Date, Open, High, Low, Close, Volume (ET, tz-naive), ascending.
    """
    if not results:
        return pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])

    df = pd.DataFrame(results)
    required = {"t", "o", "h", "l", "c", "v"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns from Polygon results: {sorted(missing)}")

    df["Date"] = (
        pd.to_datetime(df["t"], unit="ms")
        .dt.tz_localize(utc_tz)
        .dt.tz_convert(nyc_tz)
        .dt.tz_localize(None)
    )
    df = df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"})[
        ["Date", "Open", "High", "Low", "Close", "Volume"]
    ]
    # Round High and Close to two decimals as requested
    df["Open"] = df["Open"].round(2)
    df["High"] = df["High"].round(2)
    df["Low"] = df["Low"].round(2)
    df["Close"] = df["Close"].round(2)
    df = df.sort_values("Date").drop_duplicates(subset=["Date"], keep="first").reset_index(drop=True)
    return df


def save_minute_bars_adjusted(ticker="", adjusted: bool = True, output_dir: str = "data") -> str:
    
    if ticker == "":
        raise ValueError("Invalid ticker symbol")    

    print(f"Downloading minute bars for {ticker} ({'adjusted' if adjusted else 'unadjusted'})...")
    all_results = []
    next_url = None
    while True:
        results, next_url = get_polygon_data(ticker=ticker,url=next_url, adjusted=adjusted)
        if not results:
            break
        all_results.extend(results)
        if not next_url:
            break

    df = convert_to_backtesting_format(all_results)
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{ticker}_adjusted.csv" if adjusted else f"{ticker}.csv"
    path = os.path.join(output_dir, filename)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")
    return path


def read_tickers_file(tickers_file_path: str) -> list:
    tickers = []
    with open(tickers_file_path, "r") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            tickers.append(line)
    return tickers


if __name__ == "__main__":
    files_dir = "data/"
    sp500_tickers_file = "sp500_tickers.csv"
    adjusted = True

    tickers = read_tickers_file(sp500_tickers_file)    
    print(f"Found {len(tickers)} tickers in Sp500 Tickers File")

    os.makedirs(files_dir, exist_ok=True)

    for idx, ticker in enumerate(tickers, start=1):
        try:
            outfile = os.path.join(
                files_dir,
                f"{ticker}_adjusted.csv" if adjusted else f"{ticker}.csv",
            )
            if os.path.exists(outfile):
                print(f"[{idx}/{len(tickers)}] Skipping {ticker}: {outfile} already exists")
                continue
            print(f"[{idx}/{len(tickers)}] Processing {ticker}")
            save_minute_bars_adjusted(ticker=ticker, adjusted=adjusted, output_dir=files_dir)
        except Exception as exc:
            print(f"[{idx}/{len(tickers)}] Error for {ticker}: {exc}")
        # Gentle throttle to respect API limits; adjust as needed
        time.sleep(0.25)
