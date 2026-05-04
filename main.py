import logging
import sys
from pathlib import Path

from src.web_scraper import WebScraper

def setup_global_logger():
    BASE_DIR = Path(__file__).resolve().parent
    LOG_DIR = BASE_DIR / "logs" / "execute_logs"
    LOG_FILE = LOG_DIR / "execute_logs.log"

    # 최상단 루트 로거(Root Logger) 생성 및 레벨 설정
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

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
    
    logger.info("========== 자동화 프로그램 시작 ==========")
    scraper = WebScraper()
    result = scraper.execute_scrape()
    logger.info(f"크롤링 데이터 수집 완료: {len(result) if result else 0}건")
    logger.info("========== 자동화 프로그램 종료 ==========")