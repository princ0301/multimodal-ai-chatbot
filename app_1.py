import gradio as gr
from modules.audio_processing import transcribe_audio
from modules.image_processing import encode_image_to_base64
from modules.text_processing import get_user_query
#from modules.ai_response import generate_medical_response
from modules.gemini_response import generate_medical_response

def process_inputs(text_input, audio_file, image_file, history):
    transcribed_text = None
    if audio_file:
        transcribed_text = transcribe_audio(audio_file)

    query = get_user_query(text_input, transcribed_text)
    image_base64 = encode_image_to_base64(image_file) if image_file else None

    if history is None:
        history = []

    # Add user message to history
    history.append({"role": "user", "content": query})

    # Get doctor response
    doctor_response = generate_medical_response(query, image_base64=image_base64, history=history)

    # Add doctor response to history
    history.append({"role": "assistant", "content": doctor_response})

    return transcribed_text or "", doctor_response, history

iface = gr.Interface(
    fn=process_inputs,
    inputs=[
        gr.Textbox(label="Type your medical question (optional)"),
        gr.Audio(sources=["microphone"], type="filepath", label="Speak your question (optional)"),
        gr.Image(type="filepath", label="Upload a related medical image (optional)"),
        gr.State([])  # <-- Chat history
    ],
    outputs=[
        gr.Textbox(label="Transcribed Audio"),
        gr.Textbox(label="Doctor's Detailed Response"),
        gr.State()  # <-- Return updated history
    ],
    title="Multimodal Medical AI Chatbot",
    description="Ask about diseases or chronic illnesses using text, audio, or images."
)

if __name__ == "__main__":
    iface.launch(debug=True)
