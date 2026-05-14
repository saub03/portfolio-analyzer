import pandas as pd
import FinanceDataReader as fdr
import numpy as np
from datetime import datetime, timedelta
import logging
import os
import json

logger = logging.getLogger(__name__)

class PortfolioAnalyzer:
    def __init__(self, user_portfolio, target_ratio_df):
        """
        user_portfolio: PortfolioReader.df (index: 자산군, columns: [target_ratio, assets])
        target_ratio_df: PortfolioReader.get_target_ratio()
        """
        self.portfolio_df = user_portfolio
        self.target_ratio_df = target_ratio_df
        
        # 자산군별 현재 가치 계산
        self.current_values = self._calculate_current_values()
        self.total_value = sum(self.current_values.values())
        
    def _calculate_current_values(self):
        """각 자산군별 총 평가금액을 계산합니다."""
        values = {}
        for asset_class, row in self.portfolio_df.iterrows():
            class_total = 0
            assets = row.get('assets', [])
            if isinstance(assets, list):
                for asset in assets:
                    # 'value'(평가금액)가 명시되어 있거나, 'amount'(수량) * 'price'(단가)로 계산 가능하다고 가정
                    val = asset.get('value', asset.get('amount', 0) * asset.get('price', 0))
                    class_total += val
            values[asset_class] = class_total
        return values

    def get_weight_differences(self):
        """목표 비중과 현재 비중의 차이 계산"""
        logger.info("목표 비중과 현재 비중 차이 계산 중...")
        df = self.target_ratio_df.copy()
        
        if self.total_value == 0:
            df['current_ratio'] = 0.0
        else:
            df['current_ratio'] = [self.current_values.get(idx, 0) / self.total_value for idx in df.index]
            
        df['diff_ratio'] = df['current_ratio'] - df['target_ratio']
        
        logger.info(f"\n비중 분석 결과:\n{df[['target_ratio', 'current_ratio', 'diff_ratio']]}")
        return df

    def save_daily_portfolio(self, save_dir="data"):
        """현재 날짜로 유저 자산 정보(총액 및 비중) 저장 -> 추이 확인용"""
        logger.info("오늘의 포트폴리오 자산 정보 저장 중...")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        file_path = os.path.join(save_dir, "historical_portfolio.json")
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        new_data = {
            "date": today_str,
            "total_value": self.total_value,
            "values": self.current_values
        }
        
        historical_data = []
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    historical_data = json.load(f)
            except Exception as e:
                logger.error(f"기존 포트폴리오 이력 파일 읽기 실패: {e}")
        
        # 당일 데이터 덮어쓰기 또는 추가
        updated = False
        for idx, data in enumerate(historical_data):
            if data['date'] == today_str:
                historical_data[idx] = new_data
                updated = True
                break
        
        if not updated:
            historical_data.append(new_data)
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(historical_data, f, ensure_ascii=False, indent=4)
            logger.info(f"포트폴리오 자산 정보 이력 저장 완료: {file_path}")
        except Exception as e:
            logger.error(f"포트폴리오 자산 정보 저장 중 오류 발생: {e}")

    def get_historical_prices(self, tickers, start_date=None):
        """FinanceDataReader를 활용하여 최근 1년치 가격 데이터를 수집"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        price_df = pd.DataFrame()
        for ticker in tickers:
            try:
                df = fdr.DataReader(ticker, start_date)
                if not df.empty and 'Close' in df.columns:
                    price_df[ticker] = df['Close']
            except Exception as e:
                logger.warning(f"티커 {ticker}의 가격 정보를 불러오지 못했습니다: {e}")
        return price_df

    def calculate_mdd(self, tickers):
        """각 자산의 MDD(Maximum Drawdown) 계산"""
        logger.info("포트폴리오 자산 MDD 계산 중...")
        price_df = self.get_historical_prices(tickers)
        if price_df.empty:
            logger.warning("가져온 가격 데이터가 없어 MDD를 계산할 수 없습니다.")
            return pd.Series(dtype=float)
        
        roll_max = price_df.cummax()
        drawdown = price_df / roll_max - 1.0
        mdd = drawdown.min()
        
        logger.info(f"MDD 계산 완료:\n{mdd}")
        return mdd

    def calculate_correlation(self, tickers):
        """자산 간 상관계수 (Correlation) 분석"""
        logger.info("포트폴리오 자산 상관계수 분석 중...")
        price_df = self.get_historical_prices(tickers)
        if price_df.empty:
            logger.warning("가져온 가격 데이터가 없어 상관계수를 계산할 수 없습니다.")
            return pd.DataFrame()
            
        daily_returns = price_df.pct_change().dropna()
        corr_matrix = daily_returns.corr()
        
        logger.info(f"상관계수 매트릭스 계산 완료:\n{corr_matrix}")
        return corr_matrix
        
    def extract_all_tickers(self):
        """portfolio.json에서 fdr 검색을 위한 'ticker' 속성 모두 추출"""
        tickers = []
        for _, row in self.portfolio_df.iterrows():
            assets = row.get('assets', [])
            if isinstance(assets, list):
                for asset in assets:
                    if 'ticker' in asset:
                        tickers.append(asset['ticker'])
        return list(set(tickers)) # 중복 제거 후 반환
