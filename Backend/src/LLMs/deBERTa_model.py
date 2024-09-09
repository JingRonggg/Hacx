##LLM Model 2: MoritzLaurer's Zero-Shot Classification trained on Microsoft's Dataset (2nd line of defence)

# Citation:
# Laurer, Moritz, Wouter van Atteveldt, Andreu Salleras Casas, and Kasper Welbers. 2022. 
# ‘Less Annotating, More Classifying – Addressing the Data Scarcity Issue of Supervised Machine Learning 
# with Deep Transfer Learning and BERT - NLI’. Preprint, June. Open Science Framework.

import tensorflow as tf
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification

# Load the model at startup
print("Loading model... This may take a few moments.")
model_name = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = TFAutoModelForSequenceClassification.from_pretrained(model_name)
print("Model loaded successfully.")

def detect_fake_news(text):
    inputs = tokenizer(text, return_tensors="tf", truncation=True, max_length=512)
    outputs = model(inputs)
    predictions = tf.nn.softmax(outputs.logits, axis=-1)
    label_names = ["entailment", "neutral", "FAKE"]
    # Multiply by 100 and format to 2 decimal places
    scores = {name: round(float(pred) * 100, 2) for name, pred in zip(label_names, predictions[0])}
    print(scores)
    return scores

def interpret_results(scores):
    if scores["FAKE"] > 50:
        return "FAKE"
    elif scores["entailment"] > 50:
        return "LIKELY TRUE"
    else:
        return "Unsure (Neutral)"
