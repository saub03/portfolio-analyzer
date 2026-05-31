import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import markdown

logger = logging.getLogger(__name__)

class EmailSender:
    def __init__(self):
        # .env에서 이메일 정보 로드
        self.sender_email = os.getenv("EMAIL_SENDER")
        self.sender_password = os.getenv("EMAIL_PASSWORD")
        self.receiver_email = os.getenv("EMAIL_RECEIVER")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))

    def send_report(self, report_path, date_str):
        """
        마크다운 리포트를 읽어와 HTML로 변환하고 Jinja2 템플릿을 거쳐 이메일로 전송합니다.
        """
        if not all([self.sender_email, self.sender_password, self.receiver_email]):
            logger.error("이메일 전송 실패: .env 파일에 EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER를 설정해주세요.")
            return False

        if not os.path.exists(report_path):
            logger.error(f"이메일 전송 실패: 리포트 파일을 찾을 수 없습니다. ({report_path})")
            return False

        try:
            # 1. 마크다운 파일 읽기
            with open(report_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # 2. 마크다운을 HTML로 변환 ('tables' 확장 추가)
            html_content = markdown.markdown(md_content, extensions=['tables'])

            # 3. Jinja2 템플릿 정의 및 렌더링
            template_str = """
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <title>AI 자산관리 리포트</title>
                <style>
                    body {
                        font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
                        line-height: 1.6;
                        color: #333333;
                        background-color: #f4f7f6;
                        padding: 20px;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        padding: 30px;
                        border-radius: 8px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    }
                    table {
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                    }
                    th, td {
                        border: 1px solid #dddddd;
                        padding: 10px;
                        text-align: left;
                    }
                    th { background-color: #f8f9fa; font-weight: bold; }
                </style>
            </head>
            <body>
                <div class="container">
                    {{ report_html | safe }}
                </div>
            </body>
            </html>
            """
            template = Template(template_str)
            final_html = template.render(report_html=html_content)

            # 4. 이메일 메시지 구성
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"일일 초개인화 AI 자산관리 리포트 ({date_str})"
            msg['From'] = self.sender_email
            msg['To'] = self.receiver_email
            
            msg.attach(MIMEText(final_html, 'html'))

            # 5. SMTP 서버 연결 및 이메일 전송
            logger.info(f"SMTP 서버({self.smtp_server}:{self.smtp_port}) 연결 및 이메일 전송 중...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()

            logger.info(f"이메일 전송 완료: {self.receiver_email}")
            return True

        except Exception as e:
            logger.error(f"이메일 전송 중 오류 발생: {e}")
            return False
