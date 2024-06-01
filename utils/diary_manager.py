import pandas as pd
import os

def load_diary():
    """
    CSV 파일에서 일기 데이터를 불러옵니다. 파일이 존재하지 않으면 빈 DataFrame을 생성합니다.
    
    반환값:
        diary (pd.DataFrame): ['datetime', 'texts', 'sentiment', 'pic'] 컬럼을 가진 DataFrame
    """
    try:
        # 일기 CSV 파일 경로를 생성
        diary_path = os.path.join(os.path.dirname(__file__), '../datasets/diary_data.csv')
        # 'datetime' 컬럼을 datetime 객체로 파싱하면서 CSV 파일을 DataFrame으로 읽어들임
        diary = pd.read_csv(diary_path, parse_dates=['datetime'])
    except FileNotFoundError:  # 파일이 없을 경우 예외 처리
        # 파일이 없을 경우 지정된 컬럼을 가진 빈 DataFrame을 생성
        diary = pd.DataFrame(columns=['datetime', 'texts', 'sentiment', 'pic'])
    return diary

def save_diary(diary):
    """
    일기 DataFrame을 CSV 파일로 저장합니다.
    
    매개변수:
        diary (pd.DataFrame): 저장할 일기 항목을 가진 DataFrame
    """
    try:
        # 일기 CSV 파일 경로를 생성
        diary_path = os.path.join(os.path.dirname(__file__), '../datasets/diary_data.csv')
        # DataFrame을 CSV 파일로 저장, 인덱스 없이 저장하고 UTF-8 인코딩 사용
        diary.to_csv(diary_path, index=False, encoding='utf-8')
    except Exception as e:  # 파일 저장 중 발생하는 모든 예외를 처리
        # 예외가 발생하면 예외 세부 정보를 포함한 에러 메시지 출력
        print(f"Failed to save the file: {e}")

def sort_diary(diary):
    """
    일기 DataFrame을 'datetime' 컬럼을 기준으로 내림차순 정렬합니다 (가장 최근 항목이 먼저 오도록).
    
    매개변수:
        diary (pd.DataFrame): 정렬할 일기 항목을 가진 DataFrame
    
    반환값:
        sorted_diary (pd.DataFrame): 가장 최근 항목이 먼저 오는 정렬된 DataFrame
    """
    # 'datetime' 컬럼을 datetime 형식으로 변환
    diary['datetime'] = pd.to_datetime(diary['datetime'], format="%Y-%m-%d")
    # 'datetime' 컬럼을 기준으로 DataFrame을 내림차순 정렬 (가장 최근 날짜가 먼저 오도록)
    diary = diary.sort_values(by='datetime', ascending=False)
    return diary