from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
from transformers import pipeline

def load_senti_model():
    LOCAL_MODEL_PATH = "datasets/model/twitter-roberta"
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(LOCAL_MODEL_PATH)
    config = AutoConfig.from_pretrained(LOCAL_MODEL_PATH)
    model.eval()  # 평가 모드로 설정
    return tokenizer, model, config

def load_summ_model():
    summarizer = pipeline("summarization", model="Falconsai/text_summarization")
    return summarizer