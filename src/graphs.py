import os
import glob
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import FuncFormatter
import seaborn as sns
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class get_graph:
    def __init__(self):
        self.log_dir = "logs/data_logs"
        self.img_dir = "logs/img_logs"
        
        # 이미지 저장 폴더 생성
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)
            logger.info(f"이미지 로그 폴더 생성: {self.img_dir}")
            
        sns.set_style("whitegrid")
        self._set_korean_font()

    def _set_korean_font(self):
        """운영체제에 맞는 한글 폰트 설정"""
        try:
            if os.name == 'nt': # Windows
                font_name = fm.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
                plt.rc('font', family=font_name)
            elif 'darwin' in os.sys.platform: # Mac
                plt.rc('font', family='AppleGothic')
            else: # Linux
                if fm.findfont('NanumGothic', fallback_to_default=False):
                    plt.rc('font', family='NanumGothic')
                else:
                    logger.warning("한글 폰트(NanumGothic)를 찾을 수 없습니다. 그래프의 한글이 깨질 수 있습니다.")
            
            # 마이너스 부호 깨짐 방지
            plt.rcParams['axes.unicode_minus'] = False
            logger.info("한글 폰트 설정 완료")
        except Exception as e:
            logger.error(f"한글 폰트 설정 중 오류 발생: {e}")

    def create_stacked_bar_chart_from_logs(self):
        """
        logs/data_logs 폴더의 모든 user_data_*.json 파일을 읽어
        자산군별 시계열 누적 막대 그래프를 생성하고 저장합니다.
        """
        logger.info("자산 추이 누적 막대 그래프 생성 시작...")
        
        json_files = glob.glob(os.path.join(self.log_dir, "user_data_*.json"))
        if not json_files:
            logger.warning("분석할 user_data 로그 파일이 없습니다. 그래프 생성을 건너뜁니다.")
            return None
            
        data_list = []
        for file_path in json_files:
            try:
                date_str = os.path.basename(file_path).replace("user_data_", "").replace(".json", "")
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                current_values = data.get("risk_and_performance", {}).get("current_values", {})
                if current_values:
                    current_values['date'] = date_obj
                    data_list.append(current_values)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.error(f"파일 처리 중 오류 발생 ({file_path}): {e}")
                continue
        
        if not data_list:
            logger.error("로그 파일에서 유효한 데이터를 찾을 수 없습니다.")
            return None

        df = pd.DataFrame(data_list).set_index('date').sort_index()

        df.index = df.index.strftime('%Y-%m-%d')

        fig, ax = plt.subplots(figsize=(15, 8))

        df.plot(kind='bar', stacked=True, ax=ax, colormap='viridis')
        
        # 각 막대에 비중(%) 텍스트 추가
        df_pct = df.div(df.sum(axis=1), axis=0) * 100
        for i, container in enumerate(ax.containers):
            labels = []
            for j, rect in enumerate(container):
                height = rect.get_height()
                if height > 0:
                    pct = df_pct.iloc[j, i]
                    # 비중이 2% 이상인 경우에만 텍스트 표시 (글자 겹침 방지)
                    if pct >= 2.0:
                        labels.append(f'{pct:.1f}%')
                    else:
                        labels.append('')
                else:
                    labels.append('')
            ax.bar_label(container, labels=labels, label_type='center', fontsize=9, color='white', weight='bold')

        ax.set_title('일자별 자산 추이 (누적 막대 그래프)', fontsize=20, pad=20)
        ax.set_xlabel('날짜', fontsize=12)
        ax.set_ylabel('평가금액 (원)', fontsize=12)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{int(x):,}'))
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        ax.legend(title='자산군', bbox_to_anchor=(1.02, 1), loc='upper left')
        plt.tight_layout(rect=[0, 0, 0.9, 1])
        
        today_str = datetime.now().strftime("%Y%m%d")
        file_name = f"asset_timeseries_stacked_bar_{today_str}.png"
        save_path = os.path.join(self.img_dir, file_name)
        
        fig.savefig(save_path, dpi=300)
        logger.info(f"그래프 저장 완료: {save_path}")
        plt.close(fig)
        return save_path

if __name__ == "__main__":
    # 단독 실행 시 로그를 콘솔에서 볼 수 있도록 설정
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(name)s] %(levelname)s - %(message)s')
    
    logger.info("graphs.py 단독 실행 테스트 시작...")
    graph_maker = get_graph()
    
    result_path = graph_maker.create_stacked_bar_chart_from_logs()
    if result_path:
        logger.info(f"✅ 그래프 생성 테스트 성공! 확인 경로: {result_path}")
    else:
        logger.error("❌ 그래프 생성 테스트 실패. data_logs 폴더 내에 user_data_*.json 파일이 있는지 확인하세요.")