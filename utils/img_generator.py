from io import BytesIO
import base64

def text_to_image_base64(model, prompt):
    prompt = "A photo about.." + prompt
    image = model(prompt).images[0]
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return image, img_str