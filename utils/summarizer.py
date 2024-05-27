import pandas as pd
from datetime import datetime
import os, re

def summarizer_per_week(diary, summarizer):
    # datetime 형식으로 변환
    diary['datetime'] = pd.to_datetime(diary['datetime'], format="%Y-%m-%d")
    # 주(week) 정보를 기준으로 그룹화
    grouped = diary.groupby(pd.Grouper(key='datetime', freq='W'))
    # 주별 요약 데이터를 저장할 리스트
    weekly_summaries = []
    for _, group_data in grouped:
        if not group_data.empty:
            # 정보들
            start_date = group_data['datetime'].min().strftime('%Y-%m-%d')
            end_date = group_data['datetime'].max().strftime('%Y-%m-%d')
            num_entries = len(group_data)
            combined_text = "\n".join(group_data['texts'].tolist())
            
            # 단어 개수 계산하고, max_length 동적으로 결정하도록 (input length가 항상 다르니까)
            word_cnt = len(combined_text.split())
            max_length = min(150, max(10, word_cnt // 2))
            # print(max_length)
            
            # 요약 추가
            try:
                summary = summarizer(combined_text, max_length=max_length, min_length=10, do_sample=False)[0]['summary_text']
                # 특정 가까운 날짜를 가리키는 말들은 제거함 (요약이니까)
                summary = re.sub(r'\b(today|yesterday|tomorrow)\b', '', summary, flags=re.IGNORECASE).strip()
            except Exception as e:
                print(f"Error in summarization: {e}")
                summary = "Summary not available"
            
            # 주별 요약 데이터 저장
            weekly_summaries.append({
                'Week': f'{start_date} ~ {end_date}',
                'Number': num_entries,
                #'Average Sentiment': avg_sentiment,
                'Summary': summary
            })
    return pd.DataFrame(weekly_summaries)