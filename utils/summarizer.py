import pandas as pd
from datetime import datetime
import os, re

def sentiment_to_numeric(sentiment):
    """감정 상태를 숫자 점수로 변환합니다."""
    if sentiment == 'positive':
        return 100  # -100 ~ 50 ~ 100점이 기준
    elif sentiment == 'negative':
        return -100
    else:  # 'neutral'
        return 50

def summarizer(diary, client, model, task):
    """
    일기 데이터를 주별 또는 월별로 요약합니다.
    
    매개변수:
        diary (DataFrame): 일기 데이터프레임
        client: Groq API 클라이언트 객체
        model: 텍스트 요약을 위한 모델 함수
        task (str): 요약할 기준 ('weekly' 또는 'monthly')
    
    반환값:
        DataFrame: 요약된 일기 데이터프레임
    """
    # 주별 요약을 위한 처리
    if task == 'weekly':
        # datetime 형식으로 변환
        diary['datetime'] = pd.to_datetime(diary['datetime'], format="%Y-%m-%d")
        # 감정 점수
        diary['sentiment_numeric'] = diary['sentiment'].apply(sentiment_to_numeric)
        
        # 주(week) 정보를 기준으로 그룹화
        grouped = diary.groupby(pd.Grouper(key='datetime', freq='W'))
        # 주별 요약 데이터를 저장할 리스트
        weekly_summaries = []
        for _, group_data in grouped:
            if not group_data.empty:
                # 그룹화된 데이터에서 정보 추출
                start_date = group_data['datetime'].min().strftime('%Y-%m-%d')
                end_date = group_data['datetime'].max().strftime('%Y-%m-%d')
                num_entries = len(group_data)
                combined_text = "\n".join(group_data['texts'].tolist())
                avg_sentiment = group_data['sentiment_numeric'].mean()  # 감정 점수의 평균 계산
                
                # 단어 개수 계산하고, max_length 동적으로 결정하도록 (input length가 항상 다르니까)
                #word_cnt = len(combined_text.split())
                #max_length = min(150, max(10, word_cnt // 2))
                # print(max_length)
                
                # 요약 생성
                try:
                    # T5 모델을 사용할 경우
                    #summary = model(combined_text, max_length=max_length, min_length=10, do_sample=False)[0]['summary_text']
                    # 특정 가까운 날짜를 가리키는 말들은 제거함 (요약이니까)
                    #summary = re.sub(r'\b(today|yesterday|tomorrow)\b', '', summary, flags=re.IGNORECASE).strip()
                    
                    # Llama 모델을 사용하여 요약 생성
                    summary = model(client, combined_text).strip()
                                    
                except Exception as e:
                    print(f"Error in summarization: {e}")
                    summary = "Summary not available"
                
                # 주별 요약 데이터 저장
                weekly_summaries.append({
                    'Week': f'{start_date} ~ {end_date}',  # 주의 시작일과 종료일
                    'Number': num_entries,  # 해당 주의 일기 수
                    'Average Sentiment': int(avg_sentiment),  # 평균 감정 점수 (정수로 반환)
                    'Summary': summary  # 요약 텍스트
                })
        return pd.DataFrame(weekly_summaries).sort_values(by='Week', ascending=False)  # 요약 데이터프레임 반환 및 주별 정렬
        
    # 월별 요약을 위한 처리
    if task == 'monthly':
        # datetime 형식으로 변환
        diary['datetime'] = pd.to_datetime(diary['datetime'], format="%Y-%m-%d")
        # 달(month) 정보를 기준으로 그룹화
        grouped = diary.groupby(pd.Grouper(key='datetime', freq='ME'))
        # 월별 요약 데이터를 저장할 리스트
        monthly_summaries = []
        for _, group_data in grouped:
            if not group_data.empty:
                # 그룹화된 데이터에서 정보 추출
                start_date = group_data['datetime'].min().strftime('%Y-%m-%d')
                end_date = group_data['datetime'].max().strftime('%Y-%m-%d')
                num_entries = len(group_data)
                combined_text = "\n".join(group_data['texts'].tolist())
                avg_sentiment = group_data['sentiment_numeric'].mean()  # 감정 점수의 평균 계산
                
                # 단어 개수 계산하고, max_length 동적으로 결정하도록 (input length가 항상 다르니까)
                #word_cnt = len(combined_text.split())
                #max_length = min(150, max(10, word_cnt // 2))
                # print(max_length)
                
                # 요약 생성
                try:
                    # T5 모델을 사용할 경우
                    #summary = model(combined_text, max_length=max_length, min_length=10, do_sample=False)[0]['summary_text']
                    # 특정 가까운 날짜를 가리키는 말들은 제거함 (요약이니까)
                    #summary = re.sub(r'\b(today|yesterday|tomorrow)\b', '', summary, flags=re.IGNORECASE).strip()
                    
                    # Llama 모델을 사용하여 요약 생성
                    summary = model(client, combined_text, max_tokens=200).strip()
                except Exception as e:
                    print(f"Error in summarization: {e}")
                    summary = "Summary not available"
                
                # 월별 요약 데이터 저장
                monthly_summaries.append({
                    'Month': f'{start_date} ~ {end_date}',  # 달의 시작일과 종료일
                    'Number': num_entries,  # 해당 달의 일기 수
                    'Average Sentiment': int(avg_sentiment),  # 평균 감정 점수 (정수로 반환)
                    'Summary': summary  # 요약 텍스트
                })
                
        return pd.DataFrame(monthly_summaries).sort_values(by='Month', ascending=False)  # 요약 데이터프레임 반환 및 월별 정렬