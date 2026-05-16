import pandas as pd
import FinanceDataReader as fdr
import numpy as np
from datetime import datetime, timedelta
import logging
import os
import json

logger = logging.getLogger(__name__)

class StatisticalAnalyzer:
    def __init__(self, user_portfolio, target_ratio_df, stocks_info,
                bonds_info, golds_info, crypto_info, cash_info):
        self.portfolio_df = user_portfolio
        self.target_ratio_df = target_ratio_df
        self.stocks_info = stocks_info
        self.bonds_info = bonds_info
        self.golds_info = golds_info
        self.crypto_info = crypto_info
        self.cash_info = cash_info
        
        # 자산군별 현재 가치 계산
        self.current_values = self._calculate_current_values()
        
    def _calculate_current_values(self):
        """각 자산군별 총 평가금액을 계산합니다."""
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        values = {}
        asset_mapping = {
            "stocks": self.stocks_info,
            "bonds": self.bonds_info,
            "gold": self.golds_info,
            "crypto": self.crypto_info
        }
        
        for asset_name, asset_list in asset_mapping.items():
            asset_amount = 0
            for item in asset_list:
                df = fdr.DataReader(item['code'], week_ago)
                if not df.empty:
                    close = df.tail(1)['Close'].iloc[0]
                    asset_amount += close * item['quantity']
            values[asset_name] = int(asset_amount)
            
        cash_amount = 0
        cash_amount += self.cash_info['KRW']
        
        usd_df = fdr.DataReader("USD/KRW", week_ago)
        if not usd_df.empty:
            cash_amount += self.cash_info['USD'] * usd_df.tail(1)['Close'].iloc[0]
        cash_amount = int(cash_amount)
        values['cash'] = cash_amount
        
        return values

    def get_weight_differences(self):
        """목표 비중과 현재 비중의 차이 계산"""
        logger.info("목표 비중과 현재 비중 차이 계산 중...")
        current_values_dict = self.current_values.copy()
        index = current_values_dict.keys()
        data = current_values_dict.values()
        current_ratio = pd.DataFrame(data=data, index=index, columns=['current_ratio'], dtype=float)
        current_ratio['current_ratio'] = current_ratio['current_ratio'] / sum(current_ratio['current_ratio'])

        target_ratio = self.target_ratio_df.copy()
        
        weight_differences = current_ratio.copy()
        weight_differences['target_ratio'] = target_ratio['target_ratio']
        weight_differences['diff_ratio'] = weight_differences['current_ratio'] - weight_differences['target_ratio']
        logger.info("목표 비중과 현재 비중 차이 계산 완료")
        return weight_differences
        
    def _get_all_tickers(self):
        """포트폴리오에 포함된 모든 자산의 코드(티커) 목록 추출"""
        tickers = []
        for asset_list in [self.stocks_info, self.bonds_info, self.golds_info, self.crypto_info]:
            for item in asset_list:
                if 'code' in item:
                    tickers.append(item['code'])
        return list(set(tickers))

    def get_historical_prices(self, start_date=None):
        """FinanceDataReader를 활용하여 최근 1년치 가격 데이터를 수집"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        tickers = self._get_all_tickers()
        price_df = pd.DataFrame()
        for ticker in tickers:
            try:
                df = fdr.DataReader(ticker, start_date)
                if not df.empty and 'Close' in df.columns:
                    price_df[ticker] = df['Close']
            except Exception as e:
                logger.warning(f"티커 {ticker}의 가격 정보를 불러오지 못했습니다: {e}")
        return price_df

    def calculate_mdd(self):
        """각 자산의 MDD(Maximum Drawdown) 계산"""
        logger.info("포트폴리오 자산 MDD 계산 중...")
        price_df = self.get_historical_prices()
        if price_df.empty:
            logger.warning("가져온 가격 데이터가 없어 MDD를 계산할 수 없습니다.")
            return pd.Series(dtype=float)
        
        roll_max = price_df.cummax()
        drawdown = price_df / roll_max - 1.0
        mdd = drawdown.min()
        return mdd

    def calculate_correlation(self):
        """자산 간 상관계수 (Correlation) 분석"""
        logger.info("포트폴리오 자산 상관계수 분석 중...")
        price_df = self.get_historical_prices()
        if price_df.empty:
            logger.warning("가져온 가격 데이터가 없어 상관계수를 계산할 수 없습니다.")
            return pd.DataFrame()
            
        daily_returns = price_df.pct_change().dropna()
        corr_matrix = daily_returns.corr()
        
        ticker_to_name = {}
        for asset_list in [self.stocks_info, self.bonds_info, self.golds_info, self.crypto_info]:
            for item in asset_list:
                if 'code' in item and 'name' in item:
                    ticker_to_name[item['code']] = item['name']
                    
        corr_matrix.rename(columns=ticker_to_name, index=ticker_to_name, inplace=True)
        return corr_matrix
