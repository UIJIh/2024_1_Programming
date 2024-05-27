import pandas as pd
import os

def load_diary():
    try:
        diary_path = os.path.join(os.path.dirname(__file__), '../datasets/diary_data.csv')
        diary = pd.read_csv(diary_path, parse_dates=['datetime'])
    except FileNotFoundError:  # 파일이 없으면 새로운 데이터프레임 생성
        diary = pd.DataFrame(columns=['datetime', 'texts', 'sentiment', 'pic'])
    return diary

def save_diary(diary):
    try:
        diary_path = os.path.join(os.path.dirname(__file__), '../datasets/diary_data.csv')
        diary.to_csv(diary_path, index=False, encoding='utf-8')
    except Exception as e:
        print(f"Failed to save the file: {e}")

def sort_diary(diary):
    diary['datetime'] = pd.to_datetime(diary['datetime'], format="%Y-%m-%d")  # datetime 객체로 변환
    diary = diary.sort_values(by='datetime', ascending=False)  # 최신순 정렬
    return diary