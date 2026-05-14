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
        
