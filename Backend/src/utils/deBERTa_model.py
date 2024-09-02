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
    scores = {name: float(pred) for name, pred in zip(label_names, predictions[0])}
    
    return scores

def interpret_results(scores):
    if scores["FAKE"] > 0.5:
        return "FAKE"
    elif scores["entailment"] > 0.5:
        return "LIKELY TRUE"
    else:
        return "CHECK AGAIN or CROSS CHECK WITH GPT"

def main():
    
    while True:
        text = input("Enter the news text to check (or 'quit' to exit): ")
        if text.lower() == 'quit':
            break
        
        scores = detect_fake_news(text)
        interpretation = interpret_results(scores)
        
        print("\nResults:")
        for label, score in scores.items():
            print(f"{label}: {score:.2f}")
        print(f"\nInterpretation: {interpretation}\n")
