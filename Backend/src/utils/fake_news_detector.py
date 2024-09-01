import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification


model_name = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
tokenizer = None
model = None

def load_model():
    global tokenizer, model
    print("Loading model... This may take a few moments.")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = TFAutoModelForSequenceClassification.from_pretrained(model_name)
    print("Model loaded successfully.")

def detect_fake_news(text):
    inputs = tokenizer(text, return_tensors="tf", truncation=True, max_length=512)
    outputs = model(inputs)
    predictions = tf.nn.softmax(outputs.logits, axis=-1)
    label_names = ["entailment", "neutral", "FAKE"]
    scores = {name: float(pred) for name, pred in zip(label_names, predictions[0])}
    return scores

def interpret_results(scores):
    if scores["contradiction"] > 0.5:
        return "This text is likely to contain fake news or misinformation."
    elif scores["entailment"] > 0.5:
        return "This text is likely to be factual or true."
    else:
        return "The authenticity of this text is uncertain. Further fact-checking is recommended."
