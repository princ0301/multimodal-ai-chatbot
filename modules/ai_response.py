# llama_response.py
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def load_system_prompt():
    prompt_path = os.path.join(os.path.dirname(__file__), "../prompts/system_prompt.txt")
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def generate_medical_response(query, image_base64=None, history=None, model="meta-llama/llama-4-maverick-17b-128e-instruct"):
    client = Groq(api_key=GROQ_API_KEY)
    system_prompt = load_system_prompt()

    messages = [{"role": "system", "content": system_prompt}]

    if history:
        messages.extend(history[-5:])

    user_content = [{"type": "text", "text": query}]
    if image_base64:
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        })

    messages.append({"role": "user", "content": user_content})

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    return response.choices[0].message.content
