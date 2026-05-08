import logging
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import json
from datetime import datetime

from src.web_scraper import WebScraper
from src.read_userinfo import PortfolioReader


load_dotenv()

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
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY를 등록해주세요")
    
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
    1. 유저 포트폴리오 portfolio.json 읽어오기 
        1) asset_keywords에 종목명 리스트 저장
        2) TODO: AI에게 넘길 정보 저장 
    '''
    
    logger.info("포트폴리오 파일(portfolio.json) 읽기 및 자산 키워드 추출 시작...")
    userInfoReader = PortfolioReader()
    asset_keywords = userInfoReader.keywordForNews()
    logger.info(f"포트폴리오 자산 키워드 추출 완료: {len(asset_keywords)}건 {asset_keywords}")
    
    '''
    2. WebScraper모듈 시작
        1) investing.com 경제 캘린더 불러오기
        2) asset_names를 기반으로 뉴스 검색해서 불러오기
    '''
    
    # 캘린더 정보 불러오기
    scraper = WebScraper(test_window=False)
    calendar_data = scraper.execute_scrape_calendar()
    if calendar_data is None:
        logger.info("calendar_data가 비었습니다.")
    else:
        with open(f'logs/data_logs/calendar_data_{datetime.now().strftime("%Y%m%d")}.json', 'w', encoding='utf-8') as f:
            json.dump(calendar_data, f, ensure_ascii=False, indent=4) # ensure_ascii로 유니코드 한글 변환
        logger.info(f"calendar_data 수집 완료: {len(calendar_data) if calendar_data else 0}건")

    # 뉴스 정보 불러오기
    # news_data = scraper.execute_scrape_news(asset_names=asset_names)
    # 

    logger.info("========== 자동화 프로그램 종료 ==========")