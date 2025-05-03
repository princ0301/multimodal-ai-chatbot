import os
import base64
import io
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

def load_system_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/system_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def generate_medical_response(query, image_base64=None, history=None, model_name="models/gemini-1.5-pro"):
    model = genai.GenerativeModel(model_name)
    system_prompt = load_system_prompt()

    # Build chat context from history
    messages = []
    if history:
        for msg in history[-5:]:
            role = msg["role"].capitalize()
            content = msg["content"]
            if isinstance(content, list):  # handle multimodal input
                text = next((part["text"] for part in content if "text" in part), "")
            else:
                text = content
            messages.append(f"{role}: {text}")

    # Add current user input
    messages.append(f"User: {query}")
    full_prompt = f"{system_prompt}\n\n" + "\n".join(messages)

    # If image is included, decode it and use vision model
    if image_base64:
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))

        response = model.generate_content([full_prompt, image])
    else:
        response = model.generate_content(full_prompt)

    return response.text.strip()
