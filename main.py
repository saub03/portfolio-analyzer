import logging
import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from datetime import datetime# TODO: 프로그램 시작에 시간 추가하고, 공백 주기

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
    
    
    BASE_DIR = Path(__file__).resolve().parent
    LOG_DIR = BASE_DIR / "logs" / "execute_logs"
    LOG_FILE = LOG_DIR / "execute_logs.log"

    # 최상단 루트 로거(Root Logger) 생성 및 레벨 설정
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY를 등록해주세요")
    

    # 핸들러가 중복해서 추가되는 것을 방지
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - [%(name)s] %(levelname)s - %(message)s')
        
        # 1. 파일에 저장하는 핸들러
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 2. 콘솔에 출력하는 핸들러
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

if __name__ == "__main__":
    setup_global_logger()
    logger = logging.getLogger(__name__)
    
    logger.info(f"\n\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
    logger.info("========== 자동화 프로그램 시작 ==========")
    logger.info("포트폴리오 파일(portfolio.json) 읽기 및 자산 이름 추출 시작...")
    userInfoReader = PortfolioReader()
    asset_names = userInfoReader.NameForNews()
    logger.info(f"포트폴리오 자산 이름 추출 완료: {len(asset_names)}건 {asset_names}")
        
    
    scraper = WebScraper()
    calendar_data = scraper.execute_scrape()
    with open(f'logs/data_logs/calendar_data_{datetime.now().strftime("%Y%m%d")}.json', 'w', encoding='utf-8') as f:
        json.dump(calendar_data, f, ensure_ascii=False, indent=4) # ensure_ascii로 유니코드 한글 변환
    logger.info(f"calendar_data 수집 완료: {len(calendar_data) if calendar_data else 0}건")
    
    
    logger.info("========== 자동화 프로그램 종료 ==========")