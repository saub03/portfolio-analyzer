# src/email_sender.py
from jinja2 import Environment, FileSystemLoader

def render_email_html():
    # 1. 템플릿 파일이 있는 폴더 위치를 지정합니다.
    env = Environment(loader=FileSystemLoader('templates'))
    
    # 2. 사용할 템플릿 파일을 불러옵니다.
    template = env.get_template('email_template.html')

    # 3. HTML 빈칸에 채워넣을 데이터를 파이썬 딕셔너리나 리스트로 준비합니다.
    # (실제 프로젝트에서는 API나 크롤링으로 수집한 데이터가 들어갑니다.)
    mock_ai_summary = "FOMC 금리 인하 기대감으로 S&P 500과 나스닥이 상승 마감했습니다. 비트코인 및 솔라나(SOL) 등 가상화폐 시장도 동조화되며 강세를 보이고 있습니다."
    
    mock_portfolio = [
        {'name': 'S&P 500 ETF (SPY)', 'price': '$520.15', 'return': 1.2},
        {'name': '나스닥 100 ETF (QQQ)', 'price': '$445.30', 'return': 1.8},
        {'name': '미쓰비시상사', 'price': '¥3,500', 'return': -0.5},
        {'name': 'Solana (SOL)', 'price': '$150.20', 'return': 5.4}
    ]
    
    mock_news = [
        {'title': '美 연준, 연내 3회 금리 인하 전망 유지', 'link': 'https://finance.naver.com/...'},
        {'title': '워런 버핏이 픽한 일본 종합상사, 1분기 실적 발표', 'link': 'https://finance.naver.com/...'}
    ]

    # 4. 템플릿에 데이터를 전달하여 최종 HTML 문자열을 만듭니다. (렌더링)
    # 템플릿의 변수명 = 파이썬의 변수명
    final_html = template.render(
        ai_summary=mock_ai_summary,
        portfolio_list=mock_portfolio,
        news_list=mock_news
    )
    
    return final_html

# 테스트 출력 (이 문자열을 메일 본문에 그대로 넣어 보내면 됩니다!)
if __name__ == "__main__":
    result = render_email_html()
    print(result)
    
    
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_report_email(html_content):
    # 송수신자 정보 설정
    sender_email = "my_email@gmail.com" # 본인 구글 이메일
    receiver_email = "my_email@gmail.com" # 받을 이메일 (나에게 쓰기)
    app_password = "앱_비밀번호_16자리" # 구글 계정 보안에서 발급받은 앱 비밀번호

    # 메일 껍데기 만들기
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "[자동화 리포트] 오늘의 포트폴리오 분석 및 시황"
    msg['From'] = sender_email
    msg['To'] = receiver_email

    # Jinja2로 만든 HTML을 메일 본문에 부착
    part = MIMEText(html_content, 'html')
    msg.attach(part)

    # 이메일 서버 연결 및 발송
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("✅ 리포트 이메일 발송 성공!")
    except Exception as e:
        print(f"❌ 이메일 발송 실패: {e}")

# 실행
html_output = render_email_html()
send_report_email(html_output)