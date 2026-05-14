import json
import logging
import google.generativeai as genai

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """
    calendar_data, news_data, portfolio_data, 
    """
    
    def __init__(self, api_key):
        
        logger.info("GenerativeAI API 키 설정 중...")
        # transport='rest' 옵션을 추가하여 gRPC 차단으로 인한 무한 대기 버그 해결
        genai.configure(api_key=api_key, transport='rest')
        
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        logger.info("GenerativeModel(gemini-2.5-flash) 초기화 완료")
        
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
                # timeout을 15초로 설정하여 무한 대기 현상 방지
                response = self.model.generate_content(prompt, request_options={"timeout": 15})
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