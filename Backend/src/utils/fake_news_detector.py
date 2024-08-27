<<<<<<< HEAD
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
        return "CHECK AGAIN"
=======
from transformers import pipeline
import pickle

#function to run for prediction
def detecting_fake_news(var):    
#retrieving the best model for prediction call
    load_model = pickle.load(open('./final_model.sav', 'rb'))
    prediction = load_model.predict([var])
    prob = load_model.predict_proba([var])

    return (print("The given statement is ",prediction[0]),
        print("The truth probability score is ",prob[0][1]))


var = input("Please enter the news text you want to verify: ")
print("You entered: " + str(var))

detecting_fake_news(var)
>>>>>>> 95bb7cd (trained version1 of our model, added new libraries to environment.yml, included a gpt.py which cannot work due to API-Token billing issues)
