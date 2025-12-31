import yfinance as yf
import pandas as pd
import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

class DividendDataLoader:
    def __init__(self, data_dir: str = 'us_market/dividend/data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Load universe seed
        seed_file = os.path.join(data_dir, 'universe_seed.json')
        if os.path.exists(seed_file):
            try:
                with open(seed_file, 'r', encoding='utf-8') as f:
                    seed_data = json.load(f)
                    if isinstance(seed_data, list):
                        self.tickers = [item.get('symbol') for item in seed_data if item.get('symbol')]
                    else:
                        self.tickers = list(seed_data.keys())
                logger.info(f"📋 Loaded {len(self.tickers)} tickers from {seed_file}")
            except Exception as e:
                logger.error(f"Failed to load universe_seed.json: {e}")
                self.tickers = []
        else:
            logger.warning("⚠️ universe_seed.json not found.")
            self.tickers = []
            
        self.universe_data = {}
        # Try to load existing data to resume
        self.output_file = os.path.join(self.data_dir, 'dividend_universe.json')
        if os.path.exists(self.output_file):
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    self.universe_data = {k: v for k, v in existing.items() if not k.startswith('_')}
                logger.info(f"🔄 Loaded {len(self.universe_data)} existing tickers for resume.")
            except:
                pass

    def _fetch_single_ticker(self, ticker: str) -> Optional[Dict]:
        """Fetches dividend data for a single ticker."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Get price
            price = info.get('currentPrice') or info.get('regularMarketPreviousClose') or 0
            if not price:
                # Try history if info fails
                hist_price = stock.history(period='1d')
                if not hist_price.empty:
                    price = float(hist_price['Close'].iloc[-1])
            
            if not price:
                logger.warning(f"⚠️ {ticker}: Could not get price")
                return None

            # Get dividend history
            hist = stock.dividends
            if hist.empty:
                logger.warning(f"⚠️ {ticker}: No dividend history")
                return None

            # Make timezone-naive
            if hist.index.tz:
                hist.index = hist.index.tz_localize(None)
            
            one_year_ago = pd.Timestamp.now() - pd.Timedelta(days=370)
            recent_divs = hist[hist.index > one_year_ago]

            # Calculate TTM yield
            ttm_div = float(recent_divs.sum()) if not recent_divs.empty else 0.0
            div_yield = (ttm_div / price) if price > 0 else 0.0
            
            if div_yield <= 0:
                logger.warning(f"⚠️ {ticker}: Yield is 0")
                # We skip 0 yield tickers for this dividend app
                return None

            # Frequency
            frequency = len(recent_divs)
            if frequency >= 10:
                freq_str = "Monthly"
            elif frequency >= 3:
                freq_str = "Quarterly"
            elif frequency >= 1:
                freq_str = "Semi-Annual/Annual"
            else:
                freq_str = "Unknown"

            # Payments
            payments = []
            for dt, amt in recent_divs.items():
                payments.append({
                    "date": dt.strftime("%Y-%m-%d"),
                    "amount": float(amt)
                })

            return {
                'name': info.get('shortName', ticker),
                'sector': info.get('sector', 'ETF'),
                'price': float(price),
                'yield': div_yield,
                'ttm_dividend': ttm_div,
                'frequency': freq_str,
                'last_div': float(recent_divs.iloc[-1]) if not recent_divs.empty else 0,
                'payments': payments,
                'currency': info.get('currency', 'USD')
            }

        except Exception as e:
            logger.error(f"❌ Error fetching {ticker}: {e}")
            return None

    def save_data(self):
        """Saves current universe_data to JSON."""
        data_to_save = self.universe_data.copy()
        data_to_save['_meta'] = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_tickers': len(self.universe_data),
        }
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 Saved {len(self.universe_data)} tickers to {self.output_file}")

    def fetch_data(self):
        """Fetches data for all tickers, saving every 10 tickers."""
        logger.info(f"💰 Starting dividend data fetch for {len(self.tickers)} tickers...")
        
        for i, ticker in enumerate(self.tickers):
            if ticker in self.universe_data:
                continue # Skip if already fetched
                
            stock_data = self._fetch_single_ticker(ticker)
            if stock_data:
                self.universe_data[ticker] = stock_data
                logger.info(f"✅ [{i+1}/{len(self.tickers)}] {ticker}: {stock_data['yield']*100:.2f}%")
            
            if (i + 1) % 10 == 0:
                self.save_data()
        
        self.save_data()
        return self.universe_data

if __name__ == "__main__":
    loader = DividendDataLoader()
    loader.fetch_data()
