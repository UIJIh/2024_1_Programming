from utils.model_manager import load_senti_model, load_summ_model, load_groq_api, load_stable_diffusion
from utils.diary_manager import load_diary
from windows.gui import DiaryService
import torch

if __name__ == "__main__":
    # 파일 준비
    diary = load_diary()
    
    # 모델 준비
    tokenizer, senti_model, config = load_senti_model() # RoBerta
    summarizer = load_summ_model() # t5
    text_generator = load_groq_api() # llama
    img_generator_base, img_generator_refiner = load_stable_diffusion() # gpu 사용 안되면 None 반환
    
    # gui와 함께 시스템 실행
    app = DiaryService(diary, tokenizer, senti_model, config, 
                       text_generator, summarizer, img_generator_base, img_generator_refiner)
    app.mainloop()