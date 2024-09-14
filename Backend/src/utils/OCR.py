from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
import os
from dotenv import load_dotenv
import requests

load_dotenv()

subscription_key = os.getenv("SUBSCRIPTION_KEY")
endpoint = os.getenv("ENDPOINT")

# Authenticate the client
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


def is_url_image(image_url):
    if ".png" in image_url or ".jpg" in image_url or ".jpeg" in image_url:
        return True
    else:
        return False

def azure_ocr_image_to_text(URL):
    # Perform OCR on the image
    ocr_result = computervision_client.read(URL, raw=True)
    # Get the operation location (URL with an ID at the end) from the response
    operation_location = ocr_result.headers["Operation-Location"]
    operation_id = operation_location.split("/")[-1]

    # Wait for the operation to complete
    while True:
        result = computervision_client.get_read_result(operation_id)
        if result.status not in ['notStarted', 'running']:
            break

    # Extract and print the text
    if result.status == 'succeeded':
        extracted_text = ""
        for page in result.analyze_result.read_results:
            for line in page.lines:
                extracted_text += line.text + " "
        return extracted_text
    else:
        return "OCR operation failed."
