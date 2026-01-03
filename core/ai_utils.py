import requests
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-001:generateContent"

def generate_text_gemini(prompt):
    """
    Helper function to call Gemini API via HTTP.
    Returns (text, error_message).
    """
    if not settings.GOOGLE_API_KEY:
        msg = "GOOGLE_API_KEY is not set."
        logger.error(msg)
        return None, msg

    headers = {'Content-Type': 'application/json'}
    params = {'key': settings.GOOGLE_API_KEY}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data, timeout=30)
        
        # Check for HTTP errors and log the body if failed
        if response.status_code != 200:
            msg = f"Gemini API Error: Status {response.status_code} - Body: {response.text}"
            logger.error(msg)
            return None, msg
            
        result = response.json()
        # Extract text from response structure
        try:
            return result['candidates'][0]['content']['parts'][0]['text'], None
        except (KeyError, IndexError):
            msg = f"Unexpected API response structure: {result}"
            logger.error(msg)
            return None, msg
            
    except requests.exceptions.RequestException as e:
        msg = f"Gemini API Request Error: {e}"
        logger.error(msg)
        return None, msg

def generate_quiz_content(subject, topic, num_questions=5, difficulty='medium'):
    """
    Generates quiz questions using Google Gemini via REST API.
    Returns (data, error_message).
    """
    prompt = f"""
    Create a multiple-choice quiz for the subject '{subject}' on the topic '{topic}'.
    Difficulty: {difficulty}.
    Number of questions: {num_questions}.
    
    Return ONLY a raw JSON array (no markdown code blocks) where each object has:
    - "text": The question string.
    - "options": An array of 4 strings (assignments for A, B, C, D).
    - "correct_index": Integer 0-3 indicating which option is correct.
    - "rationale": A brief explanation of the answer.
    """

    text, error = generate_text_gemini(prompt)
    if error:
        return None, error

    # Clean up markdown if present
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
        
    try:
        data = json.loads(text.strip())
        return data, None
    except json.JSONDecodeError as e:
        msg = f"JSON Decode Error: {e} - Content: {text}"
        logger.error(msg)
        return None, msg

def get_ai_explanation(question_text, correct_answer_text):
    """
    Gets an AI explanation using REST API.
    Returns (explanation, error_message)
    """
    prompt = f"""
    Explain why '{correct_answer_text}' is the correct answer to the question: '{question_text}'.
    Provide a concise, helpful explanation for a student.
    """
    
    explanation, error = generate_text_gemini(prompt)
    if error:
        return None, error
    return explanation, None
