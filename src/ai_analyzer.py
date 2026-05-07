import json
import logging
import google.generativeai as genai

class AIAnalyzer:
    """
    calendar_data, news_data, portfolio_data, 
    """
    
    def __init__(self, api_key):
        
        genai.configure(api_key=api_key)
        # 로그 추가
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        # 로그 추가
        
    def generate_