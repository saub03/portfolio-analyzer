import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """
    calendar_data, news_data, portfolio_data, 
    """
    
    def __init__(self, api_key):
        
        logger.info("GenerativeAI API 키 설정 중...")
        # 새로운 공식 SDK(google.genai)의 Client 객체 초기화
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=60000) # 타임아웃 설정
        )
        self.model_name = 'gemini-2.5-flash'
        logger.info("genai.Client 초기화 완료 (모델: gemini-2.5-flash)")
        
    def generate_keywords(self, asset_names):
        '''
        자산들의 이름 리스트를 받아서 키워드 리스트로 반환(뉴스 검색용)
        '''
        logger.info(f"뉴스 검색용 키워드 생성 요청: {asset_names}")
        
        prompt = f"""
        자산 이름 목록: {asset_names}
        이 자산들과 관련된 최신 경제 뉴스를 검색하기 위해 가장 적합한 핵심 키워드를 자산별로 1~2개씩 추출.
        결과는 반드시 아래와 같은 JSON 배열 형식으로만 반환해주세요. 부가적인 텍스트는 절대 금지.
        예시: ["애플", "아이폰", "테슬라", "일론머스크"]
        """
        for i in range(3):
            try:
                logger.info(f"키워드 생성 시도 중... {i+1}/3")
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                text_response = response.text.strip()

                # 마크다운 형식 예외처리
                if text_response.startswith("```json"):
                    text_response = text_response[7:-3].strip()
                elif text_response.startswith("```"):
                    text_response = text_response[3:-3].strip()

                keywords = json.loads(text_response)
                logger.info(f"키워드 생성 완료: {keywords}")
                return keywords
            except Exception as e:
                logger.error(f"시도 {i+1}/3 실패: {e}")
        logger.error("keyword요청 실패. 원본 자산 리스트를 반환합니다.")
        return asset_names

    def generate_ai_report(self, calendar_data, news_data, user_data):
        """
        수집된 캘린더, 뉴스, 포트폴리오 데이터를 바탕으로 종합 AI 리포트를 작성합니다.
        """
        logger.info("AI 종합 리포트 생성 요청 중...")
        
        prompt = f"""
        아래에 제공된 사용자의 포트폴리오 통계 데이터, 경제 캘린더 데이터, 관련 뉴스 데이터를 바탕으로 
        오늘의 포트폴리오 분석 및 시황 요약 리포트를 작성해주세요.

        [데이터]
        1. 포트폴리오 통계 (user_data): {json.dumps(user_data, ensure_ascii=False) if user_data else '데이터 없음'}
        2. 경제 캘린더 (calendar_data): {json.dumps(calendar_data, ensure_ascii=False) if calendar_data else '데이터 없음'}
        3. 관련 뉴스 (news_data): {json.dumps(news_data, ensure_ascii=False) if news_data else '데이터 없음'}

        [요구사항]
        - 시장 시황 요약 (주요 뉴스 및 경제 지표 일정 기반)
        - 포트폴리오 현재 상태 및 위험도 평가 (MDD, 상관계수, 목표 비중 괴리율 등 데이터 활용)
        - 향후 대응 전략 및 조언
        - 이메일 본문으로 들어갈 수 있도록 HTML이 아닌 마크다운(Markdown) 형식을 사용하여 가독성 있게 작성
        - 본문만 작성하고 누구에게, 누구드림은 작성 금지
        """
        
        test_prompt = f"""
        [데이터]
        1. 포트폴리오 통계 (user_data): {json.dumps(user_data, ensure_ascii=False) if user_data else '데이터 없음'}
        2. 경제 캘린더 (calendar_data): {json.dumps(calendar_data, ensure_ascii=False) if calendar_data else '데이터 없음'}
        3. 관련 뉴스 (news_data): {json.dumps(news_data, ensure_ascii=False) if news_data else '데이터 없음'}
        AI가 사용자 포트폴리오를 분석하는데 이 세 가지 정보 말고 필요한 정보 더 있어?
        """
        
        for attempt in range(2):
            try:
                logger.info(f"AI 리포트 생성 시도 중... {attempt+1}/2")
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=test_prompt
                )
                logger.info("AI 종합 리포트 생성 완료")
                return response.text.strip()
            except Exception as e:
                logger.error(f"시도 {attempt+1}/2 실패: {e}")
                
        logger.error("AI 리포트 최종 생성 실패.")
        return "AI 리포트를 생성하는 데 실패했습니다."
        
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(name)s] %(levelname)s - %(message)s')
    
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY", "dummy_key")
    aiAnalyzer = AIAnalyzer(api_key=api_key)
    
    # 테스트용 더미 데이터
    mock_calendar_data = [{"date": "2026-05-16", "time": "21:30", "country": "US", "event_type": "Indicator", "event_name": "소비자물가지수 (CPI)", "actual": None, "consensus": "3.1%", "previous": "3.2%"}]
    mock_news_data = ["美 연준, 연내 3회 금리 인하 전망 유지", "S&P 500 사상 최고치 경신"]
    mock_user_data = {"returns": {"assets_return": {"S&P 500 ETF": 0.05}, "total_return": 0.06}, "mdd": {"SPY": -0.02}}
    
    report = aiAnalyzer.generate_ai_report(mock_calendar_data, mock_news_data, mock_user_data)
    print("\n[테스트 AI 리포트 결과]\n", report)
    