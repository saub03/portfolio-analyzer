import logging
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import json
from datetime import datetime

from src.web_scraper import WebScraper
from src.read_userinfo import PortfolioReader
from src.ai_analyzer import AIAnalyzer


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
        2) TODO: AI에게 넘길 정보 저장 
    '''
    logger.info("포트폴리오 파일(portfolio.json) 읽기 및 자산 키워드 추출 시작...")
    asset_names = userInfoReader.NamesForNews()
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
        with open(f'logs/data_logs/calendar_data_{datetime.now().strftime("%Y%m%d")}.json', 'w', encoding='utf-8') as f:
            json.dump(calendar_data, f, ensure_ascii=False, indent=4) # ensure_ascii로 유니코드 한글 변환
        logger.info(f"calendar_data 수집 완료: {len(calendar_data) if calendar_data else 0}건")

    '''
    4. 키워드로 뉴스 스크랩 후 json으로 저장
    '''
    news_data = scraper.execute_scrape_news(asset_keywords=asset_keywords)
    if len(news_data) == 0:
        logger.info("news_data가 비었습니다.")
    else:
        logger.info(f"news_data 수집 완료: {len(news_data) if news_data else 0}건")

    logger.info("========== 자동화 프로그램 종료 ==========")