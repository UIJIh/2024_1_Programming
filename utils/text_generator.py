#from utils.model_manager import load_groq_api

def generate_texts(client, user_input, temperature=0.7):
    """
    사용자의 입력을 기반으로 일기 텍스트를 생성합니다.
    
    매개변수:
        client: Groq API 클라이언트 객체
        user_input (str): 사용자가 입력한 키워드 또는 문장
        temperature (float): 생성 텍스트의 다양성을 조절하는 파라미터 (기본값은 0.7)
    
    반환값:
        generated_text (str): 생성된 일기 텍스트
    """
    # Groq API 클라이언트를 로드 (현재 주석 처리됨)
    #client = load_groq_api()
    
    # 생성 요청을 만듭니다.
    completion = client.chat.completions.create(
        model="llama3-8b-8192",  # 사용할 언어 모델 지정
        messages=[
            {
                "role": "system",
                "content": "You are a \"Daily Diary Generator.\"\nGenerate an entire diary within 100 words referring to some keywords given from users.\nRemove the date. Only diary text should be generated."
            },
            {
                "role": "user",
                "content": user_input  # 사용자가 입력한 내용을 포함
            },
            {
                "role": "assistant",
                "content": ""  # 어시스턴트의 초기 응답은 빈 문자열
            }
        ],
        temperature=temperature,  # 텍스트 생성의 무작위성을 조절
        max_tokens=100,  # 최대 생성 토큰 수
        top_p=1,  # nucleus sampling의 확률 임계값
        stream=True,  # 스트리밍 모드로 응답을 받음
        stop="[end]",  # 텍스트 생성을 중지할 시퀀스
    )

    generated_text = ""  # 생성된 텍스트를 저장할 변수
    for chunk in completion:  # 스트리밍 응답의 각 청크를 반복
        generated_text += chunk.choices[0].delta.content or ""  # 생성된 텍스트 청크를 추가

    return generated_text  # 최종 생성된 텍스트 반환

def generate_summaries(client, user_input, temperature=0.5, max_tokens=150):
    """
    사용자의 입력을 기반으로 일기 요약 텍스트를 생성합니다.
    
    매개변수:
        client: Groq API 클라이언트 객체
        user_input (str): 사용자가 입력한 일기들
        temperature (float): 생성 텍스트의 다양성을 조절하는 파라미터 (기본값은 0.5)
        max_tokens (int): 생성할 요약 텍스트의 최대 토큰 수 (기본값은 150)
    
    반환값:
        generated_text (str): 생성된 일기 요약 텍스트
    """
    # Groq API 클라이언트를 로드 
    #client = load_groq_api()
    
    # 생성 요청을 만듭니다.
    completion = client.chat.completions.create(
        model="llama3-8b-8192",  # 사용할 언어 모델 지정
        messages=[
            {
                "role": "system",
                "content": f"You are a \"Diary Summarizer.\"\nSummarize all the follwoing diaries together within {max_tokens} words.\nRemove the date or words indicating dates(today, this week, tomorrow, and so on.) Only summarized text should be printed as an answer. Start with \"I\"."
            },
            {
                "role": "user",
                "content": user_input  # 사용자가 입력한 일기 텍스트들
            },
            {
                "role": "assistant",
                "content": ""  # 어시스턴트의 초기 응답은 빈 문자열
            }
        ],
        temperature=temperature,  # 텍스트 생성의 무작위성을 조절
        max_tokens=max_tokens,  # 최대 생성 토큰 수
        top_p=1,  # nucleus sampling의 확률 임계값
        stream=True,  # 스트리밍 모드로 응답을 받음
        stop="[end]",  # 텍스트 생성을 중지할 시퀀스
    )

    generated_text = ""  # 생성된 텍스트를 저장할 변수
    for chunk in completion:  # 스트리밍 응답의 각 청크를 반복
        generated_text += chunk.choices[0].delta.content or ""  # 생성된 텍스트 청크를 추가

    return generated_text  # 최종 생성된 텍스트 반환