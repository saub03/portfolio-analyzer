import pandas as pd
from pathlib import Path
import json
import logging
"""
1. 보유 자산 관련 뉴스 스크랩 -> asset 이름 추출
2. 변동 비율 계산, 목표 비중과 차이 계산 -> 자산군별 가격 추출
3. 고급 분석 -> 총자산 및 평가손익 계산, 자산군 및 통화별 비중 계산, 위험 지표 및 집중도 분석
, AI에게 넘겨줄 '요약본' 작성

"""
logger = logging.getLogger(__name__)


# 1. 현재 파일의 절대 경로를 기준으로 부모의 부모
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. BASE_DIR 하위의 data/portfolio.json
PORTFOLIO_PATH = BASE_DIR / "data" / "portfolio.json"

def read_portfolio():
    """
    portfolio.json 읽기
    """
    if PORTFOLIO_PATH.exists():
        df = pd.read_json(PORTFOLIO_PATH)
        return df
    else:
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {PORTFOLIO_PATH}")

class PortfolioReader:
    def __init__(self):
        with open(PORTFOLIO_PATH, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
            
        self.df = pd.DataFrame({
            "assets": self.raw_data.get("assets", {}),
            "target_ratio": self.raw_data.get("target_ratio", {})
        })
        
    def names_for_news(self) -> list:
        """
        내가 가진 자산의 키워드들만 가져옵니다.
        """
        logger.info("포트폴리오 파일(portfolio.json) 읽기 및 자산 키워드 추출 시작...")
        asset_names = []
        assets_dict = self.raw_data.get("assets", {})
        for asset_type, asset_list in assets_dict.items():
            if isinstance(asset_list, list):
                for asset in asset_list:
                    if "name" in asset:
                        asset_names.append(asset["name"])
        return asset_names
    
    def get_target_ratio(self) -> pd.DataFrame:
        df_temp = self.df.copy()
        if 'assets' in df_temp.columns:
            df_temp = df_temp.drop(['assets'], axis=1)
        df_temp['target_ratio'] = df_temp['target_ratio'].apply(lambda x:x/100)
        return df_temp
    
    def get_stocks_info(self):
        return self.raw_data.get("assets", {}).get("stocks", [])
    
    def get_bonds_info(self):
        return self.raw_data.get("assets", {}).get("bonds", [])
    
    def get_golds_info(self):
        return self.raw_data.get("assets", {}).get("gold", [])
    
    def get_crypto_info(self):
        return self.raw_data.get("assets", {}).get("crypto", [])
    
    def get_cash_info(self):
        return self.raw_data.get("assets", {}).get("cash", {})

    def get_user_profile(self):
        return self.raw_data.get("user_profile", {})

    def get_financial_status(self):
        return self.raw_data.get("financial_status", {})

    def get_tax_info(self):
        return self.raw_data.get("tax_info", {})
    
    def get_alts_info(self):
        return self.raw_data.get("assets", {}).get("alternative", [])


if __name__ == "__main__":
    userInfoReader = PortfolioReader()
    ratio = userInfoReader.get_target_ratio()
    keys = ratio.index.tolist()
    values = ratio['target_ratio'].tolist()
    print(dict(zip(keys, values)))
    print(ratio)
    print(userInfoReader.get_stocks_info())