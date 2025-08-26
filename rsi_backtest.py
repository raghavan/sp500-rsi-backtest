from datetime import datetime
import pandas as pd
from  backtesting import Backtest, Strategy
from backtesting.lib import crossover
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

import talib 

import warnings

# Suppress only that specific warning
warnings.filterwarnings(
    "ignore",
    message=".*Broker canceled the relative-sized order due to insufficient margin.*",
    category=UserWarning
)

warnings.filterwarnings(
    "ignore",
    message=".*Some trades remain open at the end of backtest.*",
    category=UserWarning
)

warnings.filterwarnings("ignore", category=UserWarning, module="backtesting")

class RsiOscillator(Strategy):

    upper_bound = 70
    lower_bound = 30
    rsi_window = 14
    
    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_window) #function, data
    
    def next(self):
        if crossover(self.rsi, self.upper_bound):
            self.position.close()
        if crossover(self.lower_bound, self.rsi):
            self.buy()


def backtesting_task(args):
    ticker, strategy, all_data, years = args
    try:
        print(f"Backtesting {ticker}")
        
        data = get_data(all_data,years)
        bt = Backtest(data, strategy, cash=50_000)
        stats = bt.run()

        return {
            'Ticker': ticker,
            'Return [%]': round(stats['Return [%]'], 2),
            'Buy & Hold Return [%]': round(stats['Buy & Hold Return [%]'], 2),
            'Return (Ann.) [%]': round(stats['Return (Ann.) [%]'], 2),
            'Volatility (Ann.) [%]': round(stats['Volatility (Ann.) [%]'], 2),
            'CAGR [%]': round(stats['CAGR [%]'], 2),
            'Sharpe Ratio': round(stats['Sharpe Ratio'], 2),
            'Sortino Ratio': round(stats['Sortino Ratio'], 2),
            'Calmar Ratio': round(stats['Calmar Ratio'], 2),
            'Alpha [%]': round(stats['Alpha [%]'], 2),
            'Beta': round(stats['Beta'], 4),
            'Max Drawdown [%]': round(stats['Max. Drawdown [%]'], 2),
            'Avg Drawdown [%]': round(stats['Avg. Drawdown [%]'], 2),
            'Max Drawdown Duration (days)': stats['Max. Drawdown Duration'],
            'Avg Drawdown Duration (days)': stats['Avg. Drawdown Duration'],
            'Exposure Time [%]': round(stats['Exposure Time [%]'], 2),
            'Equity Final [$]': round(stats['Equity Final [$]'], 2),
            'Equity Peak [$]': round(stats['Equity Peak [$]'], 2),
            'Win Rate [%]': round(stats['Win Rate [%]'], 2),
            '# Trades': stats['# Trades'],  # Keep as integer
            'Best Trade [%]': round(stats['Best Trade [%]'], 2),
            'Worst Trade [%]': round(stats['Worst Trade [%]'], 2),
            'Avg Trade [%]': round(stats['Avg. Trade [%]'], 2),
            'Max Trade Duration (days)': stats['Max. Trade Duration'],
            'Avg Trade Duration (days)': stats['Avg. Trade Duration'],
            'Profit Factor': round(stats['Profit Factor'], 2),
            'Expectancy [%]': round(stats['Expectancy [%]'], 2),
            'SQN': round(stats['SQN'], 2),
            'Kelly Criterion': round(stats['Kelly Criterion'], 4),
            'Start Date' : stats['Start'],
            'End Date' : stats['End'],
            'Duration (Years of data)': round((stats['End'] - stats['Start']).days / 365)      
        }
    except Exception as e:
        print(f"Failed to fetch {ticker}")
        print(e)

def get_data(all_data, years):
    #filter results only that fall under the years from now
    max_date = all_data.index.max()    
    cutoff_date = max_date - pd.DateOffset(years=years)
    return all_data[all_data.index >= cutoff_date]

def start():
    started_at = datetime.now()

    #read all file names from data dir
    directory_path = "data"
    all_sp500_data_files = os.listdir(directory_path);

    # restrict few for testing
    all_sp500_data_files = all_sp500_data_files

    tasks = []
    for sp500_data_file in all_sp500_data_files:
        try:
            ticker=sp500_data_file.split("_")[0]
            csv_path = f"{directory_path}/{sp500_data_file}"
            
            all_data = pd.read_csv(csv_path, parse_dates=["Date"])
            all_data.set_index("Date", inplace=True)

            tasks.append((ticker, RsiOscillator, all_data, 10))
            #tasks.append((ticker, RsiOscillator, all_data, 5))
            #tasks.append((ticker, RsiOscillator, all_data, 1))
        except Exception as e:
            print(e)

    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        to_complete_tickers = []
        for task in tasks:
            to_complete_ticker = executor.submit(backtesting_task, task)
            to_complete_tickers.append(to_complete_ticker)

        for to_complete_ticker in as_completed(to_complete_tickers):
            result = to_complete_ticker.result();
            #print(result)
            results.append(result);

    #Write all results to CSV
    results_df = pd.DataFrame(results)
    output_file = f"backtest_results.csv"
    results_df.to_csv(output_file, index=False)

    finished_at = datetime.now()
    print(f"Time Taken: {(finished_at - started_at).total_seconds():.2f} s")

start()