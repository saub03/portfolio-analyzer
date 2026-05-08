import time
import logging
from datetime import datetime

from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)

class CalendarScraper:
    def __init__(self, headless=False, chrome_version=146, test_window=True):
        self.investing_url = "https://www.investing.com/economic-calendar/"
        self.options = uc.ChromeOptions()
        self.chrome_version = chrome_version
        self.headless = headless
        self.test_window = test_window
        
        
    def _scrape_investing(self):
        """
        Economic Calendar 데이터 수집
        중요도 3, This Week인 데이터만
        """
        if not self.test_window:
            options = uc.ChromeOptions()
            options.add_argument("--window-position=-2000,0") # 화면 밖으로 이동해서 화면에 안보이게 하기!!!
            driver = uc.Chrome(options=options, version_main=self.chrome_version, headless=False)
        else:
            driver = uc.Chrome(version_main=self.chrome_version,headless=self.headless, use_subprocess=False)
        
        try:
            for i in range(5):
                try:
                    driver.get(self.investing_url)
                    logger.info(f"{self.investing_url} 접근 성공... {i+1}/5")
                    break
                except Exception as e:
                    if i < 4:
                        logger.warning(f"{self.investing_url} 접근 실패... 다시 시도합니다 {i+1}/5 (사유: {e})")
                    else:
                        logger.error(f"{self.investing_url} 접근 실패... 경제 캘린더 정보 수집 스킵 {i+1}/5 (사유: {e})")
                        return None
            time.sleep(1)
            
            # 웹페이지 최상단으로 스크롤
            driver.execute_script("window.scrollTo(0, 0);")
            logger.info("웹페이지 최상단으로 스크롤 완료")
            time.sleep(1)

            # Show Filters 버튼 클릭
            category_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Show Filters')]")
            driver.execute_script("arguments[0].click();", category_btn)
            logger.info("'Show Filters' 버튼 클릭 성공")
            time.sleep(1)
            # 중요도 선택 드롭다운 클릭
            dropdown_btns = driver.find_elements(By.XPATH, "//div[contains(@class, 'no-contextual-alternatives')]")
            target_dropdown = dropdown_btns[2]
            driver.execute_script("arguments[0].click();", target_dropdown)
            logger.info("'dropdown' 클릭 성공")
            time.sleep(1)
            # 'High' 항목 선택 (중요도3)
            high_option = driver.find_element(By.CSS_SELECTOR, "div > ul > li:nth-child(3) > span")
            driver.execute_script("arguments[0].click();", high_option)
            logger.info("'High' 선택 성공")
            time.sleep(1)
            # 이번 주 카테고리 클릭
            this_week_btn =  driver.find_element(By.CSS_SELECTOR, "#__next > div.md\:relative.md\:bg-white > div.relative.flex > div.grid.flex-1.grid-cols-1.px-4.pt-6.font-sans-v2.text-\[\#232526\].antialiased.transition-all.xl\:container.sm\:px-6.sm\:pt-8.md\:gap-6.md\:px-7.md\:pt-10.md2\:gap-8.md2\:px-8.xl\:mx-auto.xl\:gap-10.xl\:px-10.md\:grid-cols-\[1fr_72px\].md2\:grid-cols-\[1fr_420px\] > div.min-w-0 > div.space-y-5.sm\:space-y-8 > div.mt-5.flex.items-center.justify-between.gap-4.md\:my-6.md\:mb-4 > div > div > button:nth-child(4) > span")
            driver.execute_script("arguments[0].click();", this_week_btn)
            logger.info("'This Week' 선택 성공")
            time.sleep(1)
            
            # 테이블에 접근해서 정보 수집
            calendar_list = []
            ele = driver.find_element(By.CLASS_NAME, "datatable-v2_body__8TXQk.relative")
            logger.info("테이블 접근 성공")
            for i in ele.find_elements(By.TAG_NAME, "tr"):
                calendar_list.append(i.text.strip())
            logger.info("테이블 정보 딕셔너리로 저장 완료")
        except Exception as e:
            logger.error(f"경제 캘린더 정보 접근 실패, 캘린더 정보 수집을 스킵합니다. (사유: {e})")
            return None
        finally:
            driver.quit()

        return calendar_list
    
    def _preprocessing_calendar(self, calendar_list):
        if calendar_list is None:
            return None
        
        week_days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
        cal_regulized = []

        def holiday_detector(item):
            """
            문자열에 Holiday가 있으면 True 리턴
            """
            for part in item.split("\n"):
                if part == "Holiday":
                    return True
            else:
                return False

        def act_for_pre(item):
            """
            파싱 길이 6개, 5개, 4개
            """
            actual, forecast, previous = (None, None, None)
            part = item.split("\n")
            if len(part)==6:
                actual = part[-3]
                forecast = part[-2]
                previous = part[-1]
            elif len(part)==5:
                actual = None
                forecast = part[-2]
                previous = part[-1]
            elif len(part)==4:
                actual = None
                forecast = None
                previous = part[-1]

            return part, actual, forecast, previous

        for item in calendar_list:
            if item.startswith(week_days):
                dt = datetime.strptime(item, "%A, %B %d, %Y")
                str_dt = dt.strftime("%Y-%m-%d")
                temp_date = str_dt
            elif holiday_detector(item):
                part = item.split("\n")
                cal_regulized.append({
                    "date":temp_date,
                    "time":part[0],
                    "country":part[1],
                    "event_type":"Holiday",
                    "event_name":part[2].split("-")[-1].strip(),
                    "actual": None,
                    "consensus": None,
                    "previous": None
                })
            else:
                part, actual, forecast, previous = act_for_pre(item)
                cal_regulized.append({
                    "date":temp_date,
                    "time":part[0],
                    "country":part[1],
                    "event_type":"Indicator",
                    "event_name":part[2],
                    "actual": actual,
                    "consensus": forecast,
                    "previous": previous
                })
        logger.info(f"경제 캘린더 데이터 전처리 완료 (정제된 데이터: {len(cal_regulized)}건)")
        return cal_regulized
    
    def execute_scrape(self):
        for attempt in range(2):
            calendar_list = self._scrape_investing()
            try:
                cal_regulized = self._preprocessing_calendar(calendar_list)
                if cal_regulized is not None:
                    return cal_regulized
            except Exception as e:
                logger.warning(f"캘린더 데이터 전처리 실패  {attempt+1}/2 다시 사이트에 접근합니다. 사유: {e}")
        logger.error("캘린더 데이터 전처리 최종 실패. None을 반환합니다.")
        return None