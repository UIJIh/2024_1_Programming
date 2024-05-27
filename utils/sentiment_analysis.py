import numpy as np
import torch
from scipy.special import softmax

def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)

def sentiment_analysis(tokenizer, model, config, text):
    encoded_input = tokenizer(text, return_tensors='pt')
    with torch.no_grad():
        output = model(**encoded_input.to('cpu'))  # CPU 사용
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    ranking = np.argsort(scores)[::-1]
    #sentiment_scores = {config.id2label[ranking[i]]: np.round(float(scores[ranking[i]]), 2) for i in range(scores.shape[0])}
    # 가장 큰 감정 하나만 가져옴
    sentiment = config.id2label[ranking[0]]
    return sentiment