# LLM Model 3: Logistic Regression Model (Last line of defence)

from transformers import pipeline
import pickle

#function to run for prediction
def logReg_detect_fake_news(var):    
#retrieving the best model for prediction call
    load_model = pickle.load(open('./final_model.sav', 'rb'))
    prediction = load_model.predict([var])
    prob = load_model.predict_proba([var])

    return prediction[0], prob[0][1]

    # return (print("The given statement is ",prediction[0]),
    #     print("The truth probability score is ",prob[0][1]))

