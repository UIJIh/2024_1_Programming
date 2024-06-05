from io import BytesIO
import base64
from PIL import Image

def text_to_image_base64(base, refiner, texts):
    """
    텍스트를 입력 받아 Stable Diffusion 모델을 사용하여 이미지를 생성하고, 해당 이미지를 Base64 문자열로 변환합니다.
    
    매개변수:
        base: Stable Diffusion 기본 모델 파이프라인 객체
        refiner: Stable Diffusion 보정 모델 파이프라인 객체
        texts: 이미지 생성을 위한 텍스트 프롬프트 (문자열)
    
    반환값:
        image: 생성된 PIL 이미지 객체
        img_str: Base64로 인코딩된 이미지 문자열
    """
    prompt = texts  # 텍스트 프롬프트를 설정
    n_steps = 100  # 추론 단계 수
    high_noise_frac = 0.9  # 노이즈 비율 (매끄럽게 처리하기 위함)
    
    # 기본 모델을 사용하여 이미지 생성 (잠재 공간에서의 이미지 생성)
    image = base(
      prompt="A painting of" + prompt, # 프롬프팅
      num_inference_steps=n_steps,
      denoising_end=high_noise_frac,
      output_type="latent",  # 잠재 공간에서의 이미지 출력
    ).images
    
    # 보정 모델을 사용하여 생성된 이미지를 개선
    image = refiner(
      prompt="A painting of" + prompt, # 프롬프팅
      num_inference_steps=n_steps,
      denoising_start=high_noise_frac,
      image=image,
    ).images[0]

    # 이미지 객체를 Base64로 인코딩된 문자열로 변환
    buffered = BytesIO()  # 바이트 스트림 버퍼 생성
    image.save(buffered, format="JPEG")  # 이미지 데이터를 JPEG 포맷으로 버퍼에 저장
    img_str = base64.b64encode(buffered.getvalue()).decode()  # 버퍼의 바이트 데이터를 Base64 문자열로 인코딩
    
    return img_str

def decode_image_base64(img_str):
    """
    Base64로 인코딩된 이미지 문자열을 디코딩하여 PIL 이미지 객체로 변환합니다.
    
    매개변수:
        img_str: Base64로 인코딩된 이미지 문자열
    
    반환값:
        image: 디코딩된 PIL 이미지 객체
    """
    # Base64 문자열을 디코딩하여 이미지 데이터로 변환
    img_bytes = base64.b64decode(img_str)    
    # 바이트 데이터에서 이미지를 생성
    image = Image.open(BytesIO(img_bytes))  # 디코딩된 바이트 데이터를 사용하여 이미지 객체 생성

    return image