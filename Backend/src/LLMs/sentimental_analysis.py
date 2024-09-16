import os
import requests
from dotenv import load_dotenv
import re

# Load environment variables from the .env file
load_dotenv()

# Configuration
API_KEY = os.getenv("OPENAI_API_KEY2")  # Get the API key from the .env file
ENDPOINT = os.getenv("AZURE_END_POINT2")  # Get the endpoint from the .env file

# Update headers to include the API key (not endpoint)
headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY,
}

# Function to get a response from the GPT model
def get_gpt_response(article_text):
    # Create the prompt for detecting fake news
    prompt = f"""
    You are a highly advanced AI with expertise in detecting disinformation. 
    Your task is to analyze the following article and provide an assessment of its sentiment and potential for disinformation. 
    First, determine the overall sentiment of the article and the emotions it conveys
    Second, based on the sentiment and the content, evaluate if the article shows signs of disinformation. 
    Consider factors like exaggerated claims, lack of evidence, or biased perspectives. 
    Provide a 1 line explanation of your assessment.
    With your analysis, provide me with the likely target audience of the article.
    Sentiment and Disinformation Assessment:
    Here is the article text:
    News article: {article_text}

    You should output your analysis in the following format:
    1. Overall Sentiment: [Sentiment classification]
    2. Explanation: [Brief explanation of the sentiment classification]
    3. Potential for Disinformation: [Disinformation classification]
    4. Explanation: [Brief explanation of the disinformation classification]
    5. Likely Target Audience: [Target audience of the article]

    Response:
    """

    role = """
    You are an advanced sentiment analysis AI,
    specialized in understanding and interpreting emotional tone in text.
    Your goal is to analyze the provided article and deliver a comprehensive sentiment analysis using logic, evidence, and critical analysis.
    """
    
    # Payload for the request
    payload = {
        "messages": [
            {"role": "system", "content": role},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "top_p": 0.95,
        "max_tokens": 2000
    }
    # Send request
    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.RequestException as e:
        raise SystemExit(f"Failed to make the request. Error: {e}")
    

import re

def parse_text(text):
    """
    Extracts and parses specific pieces of information from a formatted text string.

    The text is expected to be in a specific format with sections labeled as follows:
    1. Overall Sentiment: [sentiment]
    2. Explanation: [first explanation]
    3. Potential for Disinformation: [disinformation level]
    4. Explanation: [second explanation]
    5. Likely Target Audience: [target audience]

    Each section is expected to be on a new line and follows a specific pattern. The function 
    extracts and returns the sentiment, the first explanation, the potential for disinformation, 
    the second explanation, and the target audience from the text.

    Args:
        text (str): The input text string to be parsed. It should contain sections labeled 
                    as "Overall Sentiment", "Explanation", "Potential for Disinformation", 
                    and "Likely Target Audience" in the specified format.

    Returns:
        tuple: A tuple containing five elements:
            - sentiment (str): The overall sentiment extracted from the text. Defaults to "Unclear"
            if not found.
            - explanation1 (str): The first explanation extracted from the text. Defaults to "No explanation provided."
            if not found.
            - disinformation (str): The potential for disinformation extracted from the text. Defaults to "Unknown"
            if not found.
            - explanation2 (str): The second explanation extracted from the text. Defaults to "No explanation provided."
            if not found.
            - target_audience (str): The target audience extracted from the text. Defaults to "Not specified"
            if not found.
    """

    # Extract the overall sentiment
    sentiment_match = re.search(r"1\.\s*Overall Sentiment:\s*(.+)", text, re.IGNORECASE)
    sentiment = sentiment_match.group(1).strip() if sentiment_match else "Unclear"
    
    # Extract the first explanation
    explanation1_match = re.search(r"2\.\s*Explanation:\s*(.+?)(?=\n\d+\.\s*|$)", text, re.DOTALL)
    explanation1 = explanation1_match.group(1).strip() if explanation1_match else "No explanation provided."
    
    # Extract the potential for disinformation
    disinformation_match = re.search(r"3\.\s*Potential for Disinformation:\s*(.+)", text, re.IGNORECASE)
    disinformation = disinformation_match.group(1).strip() if disinformation_match else "Unknown"
    
    # Extract the second explanation
    explanation2_match = re.search(r"4\.\s*Explanation:\s*(.+?)(?=\n5\.\s*Likely Target Audience:|$)", text, re.DOTALL)
    explanation2 = explanation2_match.group(1).strip() if explanation2_match else "No explanation provided."
    
    # Extract the target audience
    target_audience_match = re.search(r"5\.\s*Likely Target Audience:\s*(.+)", text, re.IGNORECASE)
    target_audience = target_audience_match.group(1).strip() if target_audience_match else "Not specified"

    return sentiment, explanation1, disinformation, explanation2, target_audience

def sentimental_analysis(article_text):
    response = get_gpt_response(article_text)
    response = response['choices'][0]['message']['content'].strip()
    return parse_text(response)


# Test the function
article_text = '''
Chinese President Xi Jinping put the national focus on cultural and environmental protection as part of a four-day trip to a historic heartland in the northwest.
During his inspection tour of Gansu province from Tuesday to Friday, Xi called for improved conservation and management of the region's landscape, from mountain and forest areas, to farmland and water resources.

In particular, he stressed the need to protect the Yellow River, China's second-longest waterway.
Stopping in the provincial capital Lanzhou on Wednesday, Xi urged residents to “fulfil their duty in the joint protection of the Yellow River, so that the mother river will continue to benefit future generations”, according to state news agency Xinhua.

Inspection tours are a long-standing method used by Chinese political leaders to highlight policy priorities. Xi has made such trips to Gansu twice before – shortly before becoming president in 2013 and again in 2019.


08:25

China's Yellow River: Taming the cradle of Chinese civilisation

China's Yellow River: Taming the cradle of Chinese civilisation
In recent years, lower water levels and sediment build-up in sections of the Yellow River have affected flood control and agriculture.

The Yellow River is often described as the “mother river” in China, a reference to its place in early Chinese civilisation.

That historical importance was in focus earlier on Wednesday in the city of Tianshui.

Xi's trip to Gansu's No 2 city included a stop at the Maijishan Grottoes, a Unesco-listed heritage site that dates back about 1,600 years and is one of the most important Buddhist sites of its kind in the country. He also visited the Fuxi Temple, reputedly the biggest and best-preserved Ming dynasty temple and dedicated to the god Fuxi – a mythical emperor regarded as the ancestor of the Chinese people.

Gansu was once part of the ancient Silk Road and is home to the western end of the Great Wall.

Xi, who has promoted a mix of Marxism and traditional culture to foster unity at home and to counter Western influences, highlighted the historical value of the grottoes. It was imperative to protect and conserve such places to pass on their cultural heritage to future generations, as well as to further expand cultural tourism, he said.

Xi also called for more support for the Dunhuang Academy, which oversees another set of Unesco-list Buddhist grottoes in Gansu, as well as the creation of national cultural parks dedicated to the Yellow River, Great Wall, and the Long March. The year-long march in the mid-1930s is regarded as a turning point for the ruling Communist Party and has been a rallying cry for the president.
Xie Xiaorui, director of the Maijishan Scenic Area Management Committee, told Communist Party mouthpiece People's Daily: “We will promote the deep integration of culture and tourism and make the cultural tourism industry better and stronger.”

President Xi Jinping visits a section of the Yellow River in Lanzhou, Gansu, on Wednesday. Photo: Xinhua
President Xi Jinping visits a section of the Yellow River in Lanzhou, Gansu, on Wednesday. Photo: Xinhua
Xi also called to speed up Gansu's green and low-carbon transition, including building a national manufacturing base for new energy equipment.

Gansu is among China's top provinces in wind and solar production, with renewable energy accounting for nearly 62 per cent of its power generation capacity, ranking second in the country.

Efforts should also be made to speed up upgrades for traditional industry upgrades, strengthen industries with distinctive advantages, and develop strategic emerging industries, Xi said.

During a visit to an apple orchard in Tianshui, Xi spoke to farmers and encouraged them to optimise cultivation of the local Huaniu apple, and to use new marketing models to expand the industry.

Gansu is the second-largest province in terms of apple-planting area. Its 386,000 hectares (953,000 acres) of orchards produced 7.4 million tonnes of apples last year – an output value of 56 billion yuan (US$7.9 billion), according to ministry newspaper Science and Technology Daily.

Gansu apples are now exported to more than 20 countries around the world, with the largest percentage going to Vietnam, according to state media reports.

Xi called on the provincial agriculture sector to make the most of the region's cold and arid climate and nurture competitive brands.

President Xi Jinping visits an apple production base in Tianshui. Gansu is China's No 2 province in terms of apple-planting area. Photo: Xinhua
President Xi Jinping visits an apple production base in Tianshui. Gansu is China's No 2 province in terms of apple-planting area. Photo: Xinhua
While in Tianshui, Xi also visited a water diversion project whose construction site he had inspected in 2013. The project diverts water from the Taohe – a major tributary of the Yellow River – to ease shortages in central Gansu. Welcoming the news that it had benefited 6 million people, Xi stressed the need to prioritise projects that benefit the public.

Officials were urged to deepen reform and expand opening up in Gansu, including integrating into the building of a “unified national market” and encouraging the development of the private sector, in a reference to crucial factors in Beijing's goal of “building a high-standard market economy” by 2035.

Xi further urged Gansu to expand cross-provincial cooperation, integrate itself into belt and road cooperation, and help to build a land-sea corridor from western China down to Southeast Asia.

He also called for expanding urbanisation, and urged local officials to improve the lives of residents, especially the children and elderly, and to improve livelihoods.

Establishing common prosperity for all ethnic groups, pooling resources to address regional demands, alleviating poverty in rural areas, and advancing post-disaster recovery and reconstruction should all be a focus in the region, Xi said.
'''
print(sentimental_analysis(article_text))