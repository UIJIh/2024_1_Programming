import numpy as np
import torch
from scipy.special import softmax

def preprocess(text):
    """
    텍스트를 전처리하여 사용자 태그(@user)와 URL(http)을 일반화합니다.
    
    매개변수:
        text (str): 원본 텍스트 문자열
    
    반환값:
        new_text (str): 전처리된 텍스트 문자열
    """
    new_text = []  # 전처리된 텍스트를 저장할 리스트
    for t in text.split(" "):  # 텍스트를 공백을 기준으로 분할
        # '@'로 시작하고 길이가 1보다 큰 단어를 '@user'로 대체
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        # 'http'로 시작하는 단어를 'http'로 대체
        t = 'http' if t.startswith('http') else t
        new_text.append(t)  # 전처리된 단어를 리스트에 추가
    return " ".join(new_text)  # 리스트를 공백으로 구분하여 문자열로 변환

def sentiment_analysis(tokenizer, model, config, text):
    """
    텍스트에 대한 감정 분석을 수행합니다.
    
    매개변수:
        tokenizer: 텍스트를 토큰화하는 토크나이저 객체
        model: 감정 분석을 위한 사전 학습된 모델 객체
        config: 모델의 설정을 포함하는 객체
        text (str): 분석할 텍스트 문자열
    
    반환값:
        sentiment (str): 가장 높은 확률의 감정 라벨
    """
    # 텍스트를 토큰화하여 모델 입력 형식으로 변환
    encoded_input = tokenizer(text, return_tensors='pt')
    
    # 모델 추론을 위해 no_grad() 컨텍스트에서 실행 (기울기 계산 비활성화)
    with torch.no_grad():
        # 모델을 사용하여 입력 데이터에 대한 예측 수행 (CPU 사용)
        output = model(**encoded_input.to('cpu'))
    
    # 모델 출력에서 감정 점수를 추출하고 numpy 배열로 변환
    scores = output[0][0].detach().numpy()
    # 감정 점수에 softmax 함수를 적용하여 확률 값으로 변환
    scores = softmax(scores)
    # 확률 값의 내림차순으로 정렬된 인덱스를 반환
    ranking = np.argsort(scores)[::-1]
    # 가장 높은 확률의 감정 라벨을 추출
    sentiment = config.id2label[ranking[0]]
    
    return sentiment  # 가장 높은 확률의 감정 라벨 반환