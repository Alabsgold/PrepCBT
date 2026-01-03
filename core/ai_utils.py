import requests
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def generate_text_gemini(prompt):
    """
    Helper function to call Gemini API via HTTP.
    """
    if not settings.GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY is not set.")
        return None

    headers = {'Content-Type': 'application/json'}
    params = {'key': settings.GOOGLE_API_KEY}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        # Extract text from response structure
        # { "candidates": [ { "content": { "parts": [ { "text": "..." } ] } } ] }
        try:
            return result['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            logger.error(f"Unexpected API response structure: {result}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Gemini API Request Error: {e}")
        return None

def generate_quiz_content(subject, topic, num_questions=5, difficulty='medium'):
    """
    Generates quiz questions using Google Gemini via REST API.
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

    text = generate_text_gemini(prompt)
    if not text:
        return None

    # Clean up markdown if present
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
        
    try:
        data = json.loads(text.strip())
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {e} - Content: {text}")
        return None

def get_ai_explanation(question_text, correct_answer_text):
    """
    Gets an AI explanation using REST API.
    """
    prompt = f"""
    Explain why '{correct_answer_text}' is the correct answer to the question: '{question_text}'.
    Provide a concise, helpful explanation for a student.
    """
    
    explanation = generate_text_gemini(prompt)
    if not explanation:
        return "Could not retrieve explanation at this time."
    return explanation
