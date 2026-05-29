import logging
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import glob

from src.web_scraper import WebScraper
from src.read_userinfo import PortfolioReader
from src.ai_analyzer import AIAnalyzer
from src.statistical_analysis import StatisticalAnalyzer
from src.graphs import get_graph

import pandas as pd

def setup_global_logger():
    if not os.path.exists('logs'):
        os.mkdir('logs')
    if not os.path.exists('logs/execute_logs'):
        os.mkdir('logs/execute_logs')
    if not os.path.exists('logs/data_logs'):
        os.mkdir('logs/data_logs')
    if not os.path.exists('data'):
        os.mkdir('data')
    

# ============================ logger 설정 ===============================
    BASE_DIR = Path(__file__).resolve().parent
    LOG_DIR = BASE_DIR / "logs" / "execute_logs"
    LOG_FILE = LOG_DIR / "execute_logs.log"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - [%(name)s] %(levelname)s - %(message)s')
        
        #  파일에 저장하는 핸들러
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        #  콘솔에 출력하는 핸들러
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
# ==========================================================================


if __name__ == "__main__":
    setup_global_logger()
    logger = logging.getLogger(__name__)
    
    logger.info("\n\n========== 자동화 프로그램 시작 ==========")
    
    '''
    0. 객체 초기화
    '''
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY 등록 실패. 프로그램 종료")
        raise ValueError("GEMINI_API_KEY를 등록해주세요")
    logger.info("GEMINI_API_KEY 등록 완료")
    
    aiAnalyzer = AIAnalyzer(api_key=GEMINI_API_KEY)
    logger.info("aiAnalyzer 객체 초기화 완료")
    

    userInfoReader = PortfolioReader()
    logger.info("userInfoReader 객체 초기화 완료")

    scraper = WebScraper(chrome_version=148 ,test_window=False)
    logger.info("scraper 객체 초기화 완료")
    
    
    '''
    1. 유저 포트폴리오 portfolio.json 읽어오기 
        1) asset_names에 종목명 리스트 저장
        2) AI에게 넘길 정보 저장 
    '''
    logger.info("포트폴리오 파일(portfolio.json) 읽기 및 자산 키워드 추출 시작...")
    asset_names = userInfoReader.names_for_news()
    logger.info(f"포트폴리오 자산 이름 추출 완료: {len(asset_names)}건 {asset_names}")
    
    '''
    2. 추출한 자산 이름에서 제미나이 api로 키워드 추출.
    '''
    asset_keywords = aiAnalyzer.generate_keywords(asset_names)
    
    '''
    3. investing.com 경제 캘린더 불러오기
    '''
    # 캘린더 정보 불러오기
    for i in range(3):
        try:
            calendar_data = scraper.execute_scrape_calendar()
            break
        except Exception as e:
            logger.warning(f"calendat_data 수집 실패. 다시시도 {i+1}/3")
            
    if calendar_data is None:
        logger.info("calendar_data가 비었습니다.")
    else:
        try:
            file_path = f'logs/data_logs/calendar_data_{datetime.now().strftime("%Y%m%d")}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(calendar_data, f, ensure_ascii=False, indent=4) # ensure_ascii로 유니코드 한글 변환
            logger.info(f"calendar_data 파일 저장 완료: {file_path}, 총 {len(calendar_data)}건")
        except Exception as e:
            logger.error(f"calendar_data 파일 저장 중 오류 발생: {e}")
    

    '''
    4. 키워드로 뉴스 스크랩 후 json으로 저장
    '''
    news_data = scraper.execute_scrape_news(asset_keywords=asset_keywords)
    if len(news_data) == 0:
        logger.info("news_data가 비었습니다.")
    else:
        try:
            file_path = f'logs/data_logs/news_data_{datetime.now().strftime("%Y%m%d")}.json'
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(news_data, f, ensure_ascii=False, indent=4)
            logger.info(f"news_data 파일 저장 완료: {file_path}, 총 {len(news_data)}건")
        except Exception as e:
            logger.error(f"news_data 파일 저장 중 오류 발생: {e}")

    '''
    5. 고급 통계분석
    '''
    logger.info("고급 통계분석 시작...")
    target_ratio = userInfoReader.get_target_ratio()
    user_portfolio = userInfoReader.df
    stocks_info = userInfoReader.get_stocks_info()
    bonds_info = userInfoReader.get_bonds_info()
    golds_info = userInfoReader.get_golds_info()
    crypto_info = userInfoReader.get_crypto_info()
    cash_info = userInfoReader.get_cash_info()
    alts_info = userInfoReader.get_alts_info()

    staticAnalyzer = StatisticalAnalyzer(user_portfolio=user_portfolio, 
                                        target_ratio_df=target_ratio,
                                        stocks_info=stocks_info,
                                        bonds_info=bonds_info,
                                        golds_info=golds_info,
                                        crypto_info=crypto_info,
                                        cash_info=cash_info,
                                        alts_info=alts_info)
    val = staticAnalyzer.current_values
    logger.info(f"val: {val}")
    
    profit_loss = staticAnalyzer.calculate_profit_loss()
    logger.info(f"\nprofit_loss: \n{profit_loss}")

    diff = staticAnalyzer.get_weight_differences()
    logger.info(f"\ndiff: \n{diff}")
    
    mdd = staticAnalyzer.calculate_mdd()
    logger.info(f"\nmdd: \n{mdd}")
    
    corr = staticAnalyzer.calculate_correlation()
    logger.info(f"\ncorrelation: \n{corr}")
    
    returns_info = staticAnalyzer.calculate_returns()
    logger.info(f"\nreturns_info: \n{returns_info}")
    
    volatility = staticAnalyzer.calculate_volatility()
    logger.info(f"\nvolatility: \n{volatility}")
    
    sharpe = staticAnalyzer.calculate_sharpe_ratio()
    logger.info(f"\nsharpe_ratio: \n{sharpe}")
    
    beta = staticAnalyzer.calculate_beta()
    logger.info(f"\nbeta: \n{beta}")
    
    '''
    6. 분석 결과 JSON 저장
    '''
    user_data = {
        "investor_profile": {
            "user_profile": userInfoReader.get_user_profile(),
            "financial_status": userInfoReader.get_financial_status(),
            "tax_info": userInfoReader.get_tax_info()
        },
        "portfolio_holdings": userInfoReader.raw_data.get("assets", {}),
        "risk_and_performance": {
            "current_values": val,
            "profit_loss_summary": profit_loss,
            "weight_differences": diff.to_dict(),
            "mdd": mdd.to_dict(),
            "correlation": corr.to_dict(),
            "returns": returns_info,
            "volatility": volatility.to_dict(),
            "sharpe_ratio": sharpe.to_dict(),
            "beta": beta.to_dict()
        }
    }
    
    try:
        file_path = f'logs/data_logs/user_data_{datetime.now().strftime("%Y%m%d")}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, ensure_ascii=False, indent=4)
        logger.info(f"user_data 파일 저장 완료: {file_path}")
    except Exception as e:
        logger.error(f"user_data 파일 저장 중 오류 발생: {e}")
    
    '''
    7. calendar_data, news_data, user_data 결합, AI분석
    '''
    logger.info("데이터 취합 및 AI 분석 시작...")
    today_str = datetime.now().strftime("%Y%m%d")
    
    # glob을 활용하여 오늘 날짜의 데이터 파일 찾기
    calendar_files = glob.glob(f"logs/data_logs/calendar_data_{today_str}.json")
    news_files = glob.glob(f"logs/data_logs/news_data_{today_str}.json")
    user_files = glob.glob(f"logs/data_logs/user_data_{today_str}.json")
    
    def load_json_from_file(file_list):
        if file_list and os.path.exists(file_list[0]):
            with open(file_list[0], 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    loaded_calendar_data = load_json_from_file(calendar_files)
    loaded_news_data = load_json_from_file(news_files)
    loaded_user_data = load_json_from_file(user_files)
    
    ai_report = aiAnalyzer.generate_ai_report(
        calendar_data=loaded_calendar_data,
        news_data=loaded_news_data,
        user_data=loaded_user_data
    )
    
    # 로그 및 마크다운 파일로 저장
    logger.info(f"\n[AI 분석 리포트]\n{ai_report}")
    with open(f"logs/data_logs/ai_report_{today_str}.md", "w", encoding="utf-8") as f:
        f.write(ai_report)
    
    '''
    8. 그래프 만들기
    '''
    logger.info("시계열 자산 그래프 생성 시작...")
    graph_generator = get_graph()
    graph_generator.create_stacked_bar_chart_from_logs()
    logger.info("시계열 자산 그래프 생성 완료.")
    
    logger.info("========== 자동화 프로그램 종료 ==========")   