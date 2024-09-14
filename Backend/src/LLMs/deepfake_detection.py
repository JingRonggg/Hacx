import requests
import numpy as np
from PIL import Image
from io import BytesIO
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model

model = load_model('./src/LLMs/models/deepfake_detector.h5')


def detect_deepfake_from_url(image_url):
    """
    Checks if an image is a deepfake using the pre-trained deepfake detection model, given the image URL.
    
    Args:
        image_url (str): The URL of the image to analyze.

    Returns:
        int: The percentage likelihood that the image is a deepfake.
    """
    try:
        response = requests.get(image_url)
        if response.status_code != 200:
            raise ValueError("Unable to fetch image from the provided URL.")
        
        #Resize to match model input size
        img = Image.open(BytesIO(response.content)).resize((224, 224))  

        # Convert the image to an array
        img_array = image.img_to_array(img)

        # Expand dimensions to match the input shape of the model
        img_array = np.expand_dims(img_array, axis=0)

        img_array /= 255.0

        prediction = model.predict(img_array)
        prediction = prediction[0][0] * 100
        prediction = round(prediction, 2)
        return prediction
    except Exception as e:
        return None


# def test_deepfake_detection():
#     """
#     Test function for deepfake detection.
#     """
#     # Example URL of the image to test
#     image_url = "https://assets1.cbsnewsstatic.com/hub/i/r/2023/03/28/fabd7f51-3635-4172-8d82-29eb27691013/thumbnail/1240x780g2/cd8b154b1e8cf23be7e82397ad721da7/960x0.jpg?v=d2d77bee90bcafa285fd6d60bd8b3612"
    
#     deepfake_result = detect_deepfake_from_url(image_url)
#     print("Deepfake Detection Result:\n", deepfake_result)
