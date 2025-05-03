import gradio as gr
from datetime import datetime
from modules.audio_processing import transcribe_audio
from modules.image_processing import encode_image_to_base64
from modules.text_processing import get_user_query
from modules.gemini_response import generate_medical_response
from modules.reminder_scheduler import add_reminder

# Chatbot logic
def chatbot_fn(user_message, history, audio_file=None, image_file=None, tone="Friendly and Simple"):
    transcribed_text = None
    if audio_file:
        transcribed_text = transcribe_audio(audio_file)

    query = get_user_query(user_message, transcribed_text)
    image_base64 = encode_image_to_base64(image_file) if image_file else None

    tone_instruction = f"(Respond in a '{tone}' tone)\n"
    full_query = tone_instruction + query

    messages = history or []
    messages.append({"role": "user", "content": full_query})

    response = generate_medical_response(full_query, image_base64=image_base64, history=messages)

    return response

chatbot_ui = gr.ChatInterface(
    fn=chatbot_fn,
    additional_inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="🎤 Speak (optional)"),
        gr.Image(type="filepath", label="🖼️ Upload Medical Image (optional)"),
        gr.Dropdown(["Friendly and Simple", "Detailed and Clinical", "Explain Like I'm 5"],
                    label="🗣️ Response Tone", value="Friendly and Simple")
    ],
    title="🩺 Medical AI Chatbot",
    description="Ask medical questions using text, voice, or images. The AI will respond like a helpful doctor.",
    theme="soft",
    type="messages"
)

# Reminder logic
from datetime import datetime

def submit_reminder(subject, description, datetime_val, email, confirm):
    if not confirm:
        return "❌ Please check the confirmation box before submitting."
    if not subject or not datetime_val or not email:
        return "❌ Please fill in Subject, Date/Time, and Email."

    try:
        # Convert float timestamp to datetime object
        reminder_time = datetime.fromtimestamp(datetime_val)
    except Exception as e:
        return f"❌ Failed to process date/time: {e}"

    full_description = f"{subject} — {description}" if description else subject
    add_reminder(email=email, med=full_description, time_obj=reminder_time)

    return f"✅ Reminder set for '{subject}' at {reminder_time.strftime('%I:%M %p on %B %d, %Y')} to {email}."

with gr.Blocks() as reminder_ui:
    gr.Markdown("### ⏰ Set Medication Reminder")

    with gr.Row():
        subject_input = gr.Textbox(label="🧪 Subject", placeholder="Insulin Injection")
        time_input = gr.DateTime(label="📅 Date & Time", value=datetime.now())

    with gr.Row():
        email_input = gr.Textbox(label="📧 Email", placeholder="user@example.com")
        confirm_checkbox = gr.Checkbox(label="✅ Confirm to receive email reminder")

    description_input = gr.Textbox(label="📝 Description (optional)", placeholder="Take after dinner")

    send_btn = gr.Button("📩 Set Reminder")
    output_text = gr.Textbox(label="Status")

    send_btn.click(
        fn=submit_reminder,
        inputs=[subject_input, description_input, time_input, email_input, confirm_checkbox],
        outputs=output_text
    )

gr.TabbedInterface([chatbot_ui, reminder_ui], ["💬 Medical Chatbot", "⏰ Medication Reminder"]).launch(debug=True)
