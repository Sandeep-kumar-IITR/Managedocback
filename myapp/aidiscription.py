import google.generativeai as genai
from dotenv import load_dotenv
import os
from .models import Doc
import json
# import logging
# logger = logging.getLogger('myapp')  # Use the name from your LOGGING config

load_dotenv()

api_key = os.getenv("API_KEY")
api_key1 = os.getenv("API_KEY1")
from .models import Doc
from .models import ChatMessage
import pdfplumber
import requests

API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
HEADERS = {"Authorization": f"Bearer {api_key1}"}






def generate_ai_description_from_pdf_text(text):
    # logging.debug(api_key)
    genai.configure(api_key = api_key)
    client = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f'''From the given PDF text, create a Python list named `question` containing concise keyword-style sufficient questions for each keyword and short 2-line factual answers.

    Format each item as:  
    "keyword-question? brief 2-line answer."

    Requirements:  
    - Questions should be minimal and direct, avoiding filler words like "what" or "why."  
    - Answers must be clear, factual, and no longer than two lines.  
    - Focus only on key facts and important details, avoiding unnecessary context.  
    - Keep formatting consistent for easy similarity comparison.

    PDF text:  

 
    \n\n{text[:8000]}'''  # Truncate if long

    response = client.generate_content(prompt)
    text1 = response.text

    # Extract list from the text response
    inner = text1[text1.find('[')+1:text1.find(']')]
    lst  =  [item.strip().strip('"').strip("'") for item in inner.split(',') if item.strip()]

    response_description = client.generate_content(f"Generate a concise description of the PDF content in 2-3 professional sentences. Use the following text: {inner[:8000]}")
    descp = response_description.text.strip()
    return {
        'questions': lst,   # List of questions 
        'description': descp  # Concise description of the PDF content
    }
    


def get_similar_questions(docss , query, top_k=8):
    """
    Returns the top_k most similar AI-generated questions across all Docs for a given query.
    """

    all_questions = []

    for doc in docss:


        if doc:
            try:
                questions = json.loads(doc)

                if isinstance(questions, list):
                    for question in questions:
                        all_questions.append(question)
                        # question_to_doc.append(doc)
            except json.JSONDecodeError:
                continue

    if not all_questions:

        return []

    # Compute embeddings
    payload = {
        "inputs": {
            "source_sentence": query,
            "sentences": all_questions
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    similarity_scores = response.json()  # List of similarity scores

    # Pair sentences with scores
    scored_sentences = list(zip(all_questions, similarity_scores))

    # Sort by similarity score descending
    top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:top_k]

    # Extract only sentences
    top_sentences_only = [sentence for sentence, score in top_sentences]

    # Concatenate into one string
    result_string = " ".join(top_sentences_only)

    return result_string






def generate_ai_user_response(usser, text):
    user_docs = Doc.objects.filter(user=usser).values_list('AI_questions', flat=True)
    # concatenated_text = ' '.join(filter(None, user_docs))
    # logger.info("hey i am working 1 ")
    concatenated_text = get_similar_questions(user_docs, text, top_k=5)
    # logger.info(f"Concatenated text for user  {concatenated_text}")

    last_three_msgs = ChatMessage.objects.filter(user=usser).order_by('-id').values_list('user_message', flat=True)[1:2]
    last_three_msgs = list(reversed(last_three_msgs))  # Reverse for correct order

    last_three_msgs_ai = ChatMessage.objects.filter(user=usser).order_by('-id').values_list('assistant_response', flat=True)[:1]
    last_three_msgs_ai = list(reversed(last_three_msgs_ai))  # Reverse for correct order

    message_text ="Answer for query " + text + "last query and answer provided by you is " + ' '.join(filter(None, last_three_msgs))+ ' '.join(filter(None, last_three_msgs_ai)) 




    augmented_prompt = f"""
        Read this content and find the answer to the question in 2-3 professional sentences.

        Context:  
        {concatenated_text}  

        Query: {message_text}
        """


    genai.configure(api_key=api_key)
    client = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"{augmented_prompt}"  # Truncate if needed
    response = client.generate_content(prompt)
    return response.text



def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""  # Avoid NoneType
    return text
