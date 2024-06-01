from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from transformers import pipeline
from diffusers import DiffusionPipeline
from groq import Groq
import torch

def load_senti_model():
    """
    감정 분석 모델을 로드합니다. (RoBerta)
    
    반환값:
        tokenizer: 토큰화를 위한 AutoTokenizer 객체
        model: 감정 분석을 위한 사전 학습된 모델 (AutoModelForSequenceClassification)
        config: 모델의 설정을 포함하는 AutoConfig 객체
    """
    LOCAL_MODEL_PATH = "datasets/model/twitter-roberta"  # 로컬에 저장된 모델 경로
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH)  # 토크나이저 로드
    model = AutoModelForSequenceClassification.from_pretrained(LOCAL_MODEL_PATH)  # 모델 로드
    config = AutoConfig.from_pretrained(LOCAL_MODEL_PATH)  # 모델 설정 로드
    model.eval()  # 모델을 평가 모드로 설정 (드롭아웃 등 비활성화)
    return tokenizer, model, config

def load_summ_model():
    """
    텍스트 요약 모델을 로드합니다. (t5)
    
    반환값:
        summarizer: 사전 학습된 요약 모델을 사용하는 파이프라인 객체
    """
    summarizer = pipeline("summarization", model="Falconsai/text_summarization")  # 요약 파이프라인 로드
    return summarizer

def load_groq_api():
    """
    Groq API 클라이언트를 로드합니다. (llama)
    
    반환값:
        client: Groq API 클라이언트 객체
    """
    client = Groq(api_key="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")  # API 키를 사용하여 클라이언트 초기화
    return client

def load_stable_diffusion():
    """
    Stable Diffusion 모델을 로드합니다. GPU가 필요합니다.
    
    반환값:
        base: Stable Diffusion 기본 모델 파이프라인 객체
        refiner: Stable Diffusion 보정 모델 파이프라인 객체
    """
    # GPU 사용 가능 여부를 확인
    if not torch.cuda.is_available():
        # GPU가 없으면 None을 반환
        #print("GPU is not available. Returning None.")
        return None, None    
    
    try:
        # 기본 모델 로드
        base = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-base-1.0", 
            torch_dtype=torch.float16,  # float16 데이터 타입 사용
            variant="fp16", 
            use_safetensors=True  # 안전한 텐서 사용
        )
        base.to("cuda")  # 모델을 GPU로 이동
        
        # 보정 모델 로드
        refiner = DiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-xl-refiner-1.0",
            text_encoder_2=base.text_encoder_2,  # 기본 모델의 텍스트 인코더 사용
            vae=base.vae,  # 기본 모델의 VAE 사용
            torch_dtype=torch.float16,  # float16 데이터 타입 사용
            use_safetensors=True, 
            variant="fp16",
        )
        refiner.to("cuda")  # 모델을 GPU로 이동
        
        return base, refiner
        
    except Exception as e:
        # 모델 로드 중 오류가 발생하면 에러 메시지 출력
        print(f"Error loading models: {e}")
        return None, None
