import requests
import numpy as np
from PIL import Image
from io import BytesIO
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model
from dotenv import load_dotenv
import os

load_dotenv()

model = load_model('/Users/limmalcolm/Desktop/hacx/Hacx/Backend/src/db/models/deepfake_detector.h5')


def detect_deepfake_from_url(image_url):
    """
    Checks if an image is a deepfake using the pre-trained deepfake detection model, given the image URL.
    
    Args:
        image_url (str): The URL of the image to analyze.

    Returns:
        str: A message indicating whether the image is predicted to be a deepfake.
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
        
        if prediction[0][0] > 0.5:
            return f'The image is predicted to be a deepfake with a confidence of {prediction[0][0]:.2f}'
        else:
            return f'The image is predicted to be real with a confidence of {1 - prediction[0][0]:.2f}'
    except Exception as e:
        return f"Error in detecting deepfake: {str(e)}"


def test_deepfake_detection():
    """
    Test function for deepfake detection.
    """
    # Example URL of the image to test
    image_url = "https://static1.straitstimes.com.sg/s3fs-public/styles/large30x20/public/articles/2024/09/12/photo2024-09-1220-02-58.jpg?VersionId=7myfDE8u5PbBtvSEHtgdcMKJfTiz3hDF&itok=jkKsKHgn"
    
    deepfake_result = detect_deepfake_from_url(image_url)
    print("Deepfake Detection Result:\n", deepfake_result)


if __name__ == "__main__":
    test_deepfake_detection()