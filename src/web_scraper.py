import logging

from src.calendar_scraper import CalendarScraper
from src.news_scraper import NewsScraper

# 현재 모듈 이름으로 로거 생성
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, headless=False, chrome_version=146, test_window=True):
        self.calendar_scraper = CalendarScraper(headless=headless, chrome_version=chrome_version, test_window=test_window)
        self.news_scraper = NewsScraper()
        
    def execute_scrape_calendar(self):
        calendar_data = self.calendar_scraper.execute_scrape()
        return calendar_data
    
    def execute_scrape_news(self, asset_names):
        news_data = self.news_scraper.execute_scrape(asset_names)
        return news_data
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("WebScraper 모듈 단독 실행 시작")
    scraper = WebScraper()


