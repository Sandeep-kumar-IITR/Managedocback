import google.generativeai as genai
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer, util
from .models import Doc
import json
# import logging

# Configure logging
# logging.basicConfig(
#     level=logging.INFO,  # Use DEBUG, INFO, WARNING, ERROR, or CRITICAL
#     format='%(asctime)s - %(levelname)s - %(message)s'
# )

# Load environment variables from .env file
load_dotenv()

# Access the API key
api_key = os.getenv("API_KEY")
# api_key = "AIzaSyAN7bDuqfpCvkOGdpu-I_1S2AcR_rGpRiE"


# print("My API key is:", api_key)  # You can remove this line later

# Configure your Gemini API Key

# from .views import Listdoc
from .models import Doc
from .models import ChatMessage
from django.contrib.auth.models import User
import pdfplumber

import ast

# import logging


from sentence_transformers import SentenceTransformer
import json
from .models import Doc

model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight and fast

# logger = logging.getLogger('myapp')  # Use the name from your LOGGING config


def generate_ai_description_from_pdf_text(text):
    # logging.debug(api_key)
    genai.configure(api_key = api_key)
    client = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f'''From the given PDF text, create a Python list named `question` containing concise keyword-style questions and short 2-line factual answers.

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
    


# Load the SentenceTransformer model
# model = SentenceTransformer('all-MiniLM-L6-v2')

def get_similar_questions(docss , query, top_k=5):
    """
    Returns the top_k most similar AI-generated questions across all Docs for a given query.
    """

    all_questions = []
    # question_to_doc = []  # To map back questions to their docs

    # Collect all questions
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

    question_embeddings = model.encode(all_questions, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Compute cosine similarities
    similarities = util.pytorch_cos_sim(query_embedding, question_embeddings)[0]

    # Get top_k matches
    top_results = similarities.topk(k=min(top_k, len(all_questions)))

    # Create the concatenated string of top questions
    top_questions = [all_questions[idx] for idx in top_results.indices]
    result_string = " ".join(top_questions)


    return result_string





def generate_ai_user_response(usser, text):
    user_docs = Doc.objects.filter(user=usser).values_list('AI_questions', flat=True)
    # concatenated_text = ' '.join(filter(None, user_docs))

    concatenated_text = get_similar_questions(user_docs, text, top_k=5)




    # Get last 3 messages from the user, ordered by some field (e.g., timestamp or id)

    last_three_msgs = ChatMessage.objects.filter(user=usser).order_by('-id').values_list('user_message', flat=True)[1:3]
    last_three_msgs = list(reversed(last_three_msgs))  # Reverse for correct order

    message_text ="Answer for query " + text + "two previous query be " + ' '.join(filter(None, last_three_msgs)) 




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
