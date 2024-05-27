from utils.model_manager import load_senti_model, load_summ_model
from utils.diary_manager import load_diary
from windows.gui import DiaryService
# from diffusers import StableDiffusionPipeline
import torch

if __name__ == "__main__":
    diary = load_diary()
    tokenizer, senti_model, config = load_senti_model()   
    summarizer = load_summ_model()

    if torch.cuda.is_available():
        diffusion = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
        diffusion = diffusion.to("cuda")
    else: # gpu 안되면 이미지 생성 포기
        diffusion = None
        
    app = DiaryService(diary, tokenizer, senti_model, config, summarizer, diffusion)
    app.mainloop()