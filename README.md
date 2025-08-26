# S&P 500 RSI Backtest

An experimental backtesting framework for analyzing RSI (Relative Strength Index) trading strategies across all S&P 500 stocks using 10 years of historical minute-level data.

## 🎯 Overview


### Strategy Details

**RSI Oscillator Strategy:**
- **Buy Signal**: When RSI crosses above 30 (oversold condition)
- **Sell Signal**: When RSI crosses above 70 (overbought condition)
- **RSI Period**: 14 periods (configurable)
- **Initial Capital**: $50,000 per backtest

## 📊 Features

- **Complete S&P 500 Coverage**: Automated backtesting across all 500+ stocks
- **High-Resolution Data**: Minute-level price data for precise entry/exit timing
- **Comprehensive Metrics**: 25+ performance indicators including:
  - Return percentages and annualized returns
  - Risk metrics (Sharpe, Sortino, Calmar ratios)
  - Drawdown analysis
  - Trade statistics and win rates
  - Market exposure and volatility measures

- **Parallel Processing**: Multi-threaded execution for faster backtesting
- **Flexible Timeframes**: Configurable analysis periods (1, 5, 10 years)
- **Export Results**: CSV output for further analysis

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Polygon.io API key with paid subscription (required for 10-year historical data)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sp500-rsi-backtest.git
   cd sp500-rsi-backtest
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Set up Polygon.io API key**
   ```bash
   # Edit fetch_polygon_data.py and replace with your API key
   API_KEY = "your_polygon_api_key_here"
   ```

2. **Configure data collection period** (optional)
   ```python
   # In fetch_polygon_data.py
   START_DATE = "2015-01-01"
   END_DATE = "2025-08-15"
   ```

### Usage

1. **Fetch historical data** (⚠️ Requires Polygon.io paid subscription)
   ```bash
   python fetch_polygon_data.py
   ```
   *Note: This will download minute-level data for all S&P 500 stocks. The process may take several hours depending on your API rate limits.*

2. **Run backtests**
   ```bash
   python rsi_backtest.py
   ```

3. **View results**
   - Results are saved to `backtest_results.csv`
   - Each row contains comprehensive metrics for one stock's performance

### Using Sample Data

If you don't have a Polygon.io subscription, you can explore the framework using the included sample data:

```bash
# Sample data for GEN is included in data/GEN_adjusted.csv
# Modify rsi_backtest.py to process only the sample file
python rsi_backtest.py
```


## 📈 Output Metrics

The backtesting framework generates comprehensive performance metrics:

| Metric Category | Examples |
|-----------------|----------|
| **Returns** | Total Return %, Annualized Return %, CAGR % |
| **Risk Measures** | Volatility, Max Drawdown, Sharpe Ratio, Sortino Ratio |
| **Trade Analytics** | Win Rate, # of Trades, Best/Worst Trade, Profit Factor |
| **Market Exposure** | Exposure Time %, Alpha, Beta |
| **Duration Analysis** | Max/Avg Trade Duration, Drawdown Duration |

## ⚙️ Customization

### Modify RSI Parameters

```python
# In rsi_backtest.py, adjust the RsiOscillator class:
class RsiOscillator(Strategy):
    upper_bound = 70    # Overbought threshold
    lower_bound = 30    # Oversold threshold  
    rsi_window = 14     # RSI calculation period
```

### Change Analysis Period

```python
# In rsi_backtest.py, modify the years parameter:
tasks.append((ticker, RsiOscillator, all_data, 5))  # 5-year backtest
```

### Adjust Threading

```python
# Modify max_workers for your system:
with ThreadPoolExecutor(max_workers=6) as executor:
```

## 🔧 Dependencies

- **backtesting**: Core backtesting framework
- **TA-Lib**: Technical analysis indicators (RSI calculation)
- **pandas**: Data manipulation and analysis
- **requests**: HTTP client for Polygon.io API
- **pytz**: Timezone handling for market data

## 📊 Sample Results

The framework has been tested on the complete S&P 500 universe. Here's an example output for a single stock:

- **Ticker**: GEN
- **10-Year Return**: 590,752%
- **Sharpe Ratio**: 0.0 (high volatility strategy)
- **Win Rate**: 60.62%
- **Total Trades**: 2,156


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for educational and research purposes only. Past performance does not guarantee future results. Always consult with a qualified financial advisor before making investment decisions. The authors are not responsible for any financial losses incurred through the use of this software.
