# Hacx tryhards


## For Backend
- cd into Backend and follow the below steps
### Installing miniconda
- Follow this installation guide on https://docs.anaconda.com/miniconda/
- Then add conda to path https://www.geeksforgeeks.org/how-to-setup-anaconda-path-to-environment-variable/

### Creating conda env
- Run the following command in vscode terminal
```
conda env create -f environment.yml
```
- Then run
```
conda activate hacx
```
- This should install and run the env for hacx

```
npm install chart.js
```
- This should install visualisation tools
  

### Running the backend
- run
```
uvicorn src.api.backend:app --reload
```
- Backend is hosted on localhost:8000
- To see the docs, go to localhost:8000/localhost



# Project Documentation: Detection and Attribution of Online Spread of Disinformation

## Project Overview
This project addresses the challenge of detecting and attributing the online spread of disinformation. It focuses on using both textual and visual data to identify misinformation, fake news, and propaganda across digital platforms. The project utilizes web crawling, natural language processing, large language models (LLMs), sentiment analysis, and image analysis to enhance detection capabilities.

## Goals
- **Detect Fake News**: Automatically analyze online news articles and identify whether they contain disinformation or fake news.
- **Attribution of Disinformation**: Attribute disinformation to the appropriate sources, providing detailed explanations and analyses of the detected content.
- **Sentiment and Target Audience Analysis**: Provide additional context through sentiment analysis and identification of target audiences for clearer insights.
- **Propaganda Detection**: Identify disinformation and propaganda in images, including text-based disinformation.

## Workflow

### News Articles Detection
1. **Web Crawling**: 
   - Input: Root URLs (e.g., ABC News).
   - The system crawls all the links within the provided URL and stores these links for further processing.
   
2. **Text Extraction**:
   - The links are processed by a text extraction module to pull relevant details such as the author, body text, and publication date.
   
3. **Fake News Detection via OpenAI**:
   - The extracted text is passed to an OpenAI model to check for fake news. The model evaluates the content's authenticity.
   
4. **Fallback to DeBERTa Model**:
   - If the OpenAI model is unable to generate a high-confidence result, the text is forwarded to a DeBERTa model for further verification.
   
5. **Output**:
   - The final result includes:
     - Fake news confidence level.
     - An explanation of the detection process.
     - Target audience and sentiment analysis.
     - Information returned to the backend for storage and future retrieval.

### Image Disinformation Detection
1. **Propaganda and Text Detection**:
   - Input: Image URLs.
   - The system first checks whether the image contains text using Optical Character Recognition (OCR).
   
2. **Image Analysis via LLMs**:
   - The image is analyzed by LLMs to detect propaganda, deepfakes, and misinformation.
   
3. **Output**:
   - The results, including confidence scores, are passed to the backend and database for storage and are made accessible to the frontend.

## 3. Technical Architecture

### System Architecture
*System Architecture Diagram: (workflow.jpg)

### Technology Stack
- **Azure OpenAI**: For text and image analysis using advanced language models.
- **Python**: The core programming language for the backend and analysis algorithms.
- **FastAPI**: A fast and modern web framework to handle backend API calls.
- **Azure SQL Database**: For storing processed data and analysis results.

## Prompt Engineering Techniques for LLMs
To optimize the accuracy and reliability of the LLMs, the following prompt engineering techniques are employed:
1. **Clear Task Definition**: Clearly define the task for the model, ensuring it understands whether it needs to detect fake news, propaganda, or deepfake content.
   
2. **Structured Output**: Using regex to extract relevant information from the LLM responses ensures consistency and accurate parsing.

3. **Role Assignment**: The LLM is instructed to act in specific roles (e.g., "fact-checker" or "disinformation analyst") to enhance its response focus.

4. **Context**: Providing adequate context from the article or image to improve the LLM's understanding and ensure nuanced analysis.

5. **Chain of Thought**: A step-by-step explanation is requested from the LLM, which provides a detailed breakdown of how it arrived at the final decision.

---

This project integrates advanced AI and machine learning techniques to create a robust system for detecting and attributing online disinformation, offering detailed and insightful analysis in real-time.
