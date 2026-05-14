import time
import logging
from datetime import datetime

import feedparser
import urllib.parse

logger = logging.getLogger(__name__)

class NewsScraper:
    
    def __init__(self):
        pass
    def _get_google_news(self, keyword, max_items=3):
        """
        키워드의 구글 뉴스 제목 스크랩
        """
        try:
            logger.info(f"뉴스 정보 수집 시작: {keyword}")
            encoded_keyword = urllib.parse.quote(keyword)
            rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}&hl=ko&gl=KR&ceid=KR:ko"
            feed = feedparser.parse(rss_url)
            news_data = []
            for entry in feed.entries[:max_items]: # 최신 뉴스 max_items 개만 추출
                news_data.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published
                })
            logger.info(f"{keyword} 관련 뉴스 정보 수집 완료: {len(news_data)}건")
            return news_data
        except Exception as e:
            logger.warning(f"{keyword} 관련 뉴스 정보 수집 실패: {e}")
            return None
        
    def execute_scrape(self, asset_keywords):
        news_list = []
        for asset_keyword in asset_keywords:
            news_data = self._get_google_news(asset_keyword)
            if not news_data:
                logger.info(f"{asset_keyword}에 검색된 뉴스가 없습니다.")
            else:
                for news in news_data:
                    logger.info(f"{asset_keyword}에 검색된 뉴스: {news['title']}")
                    news_list.append(news['title'])
        return news_list

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("NewsScraper 모듈 단독 실행 시작")
    scraper = NewsScraper()
    news_list = scraper.execute_scrape(['나스닥100', '미국 기술주', '일본 종합상사', '미국 30년 국채', '미국 국채 금리', '금 현물', '국제 금 가격', '비트코인', '암호화폐', '솔라나', '알트코인'])
    logger.info(f"NewsScraper 모듈 단독 실행 종료. {len(news_list)}개 뉴스 추출 완료")