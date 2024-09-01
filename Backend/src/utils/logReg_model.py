#LLM Model 1: Logistic Regression Model

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

#if you run into "file not found error" you need to change terminal directory to ../utils first
detecting_fake_news(var)