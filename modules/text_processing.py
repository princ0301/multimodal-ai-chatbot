def get_user_query(text_input, transcribed_audio):
    if text_input:
        return text_input
    elif transcribed_audio:
        return transcribed_audio
    else:
        return "Can you help me understand what's wrong?"
