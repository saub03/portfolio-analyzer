import logging

from src.calendar_scraper import CalendarScraper
from src.news_scraper import NewsScraper

# 현재 모듈의 이름(src.web_scraper)으로 로거 생성
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, headless=False, chrome_version=146):
        self.calendar_scraper = CalendarScraper(headless=headless, chrome_version=chrome_version)
        self.news_scraper = NewsScraper()
        
    def execute_scrape(self):
        calendar_data = self.calendar_scraper.execute_scrape()
        # news_data = self.news_scraper.execute_scrape(asset_names=[...])
        
        return calendar_data
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("WebScraper 모듈 단독 실행 시작")
    scraper = WebScraper()
    result = scraper.execute_scrape()
    logger.info(f"최종 결과 데이터 수집 완료: {len(result) if result else 0}건")
    print(result)
    logger.info("WebScraper 모듈 단독 실행 종료")