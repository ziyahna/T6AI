from dotenv import load_dotenv
import os
import streamlit as st
from PIL import Image
import google.generativeai as genai
import azure.cognitiveservices.speech as speechsdk
from io import BytesIO

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro-vision')

def get_gemini_response(input_text, image_data, prompt):
    response = model.generate_content([input_text, image_data[0], prompt])
    return response.text

def input_image_details(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{"mime_type": uploaded_file.type, "data": bytes_data}]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

def text_to_speech(text):
    subscription_key = os.getenv("AZURE_SPEECH_SUBSCRIPTION_KEY")
    region = os.getenv("AZURE_SPEECH_REGION")

    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
    speech_config.speech_synthesis_language = "en-US"
    speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"

    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = synthesizer.speak_text_async(text).get()
    return result.audio_data

# Streamlit app
st.title("Invoice Analysis and Text to Speech Converter")

# Input area for user prompt
input_promt = """
You are expert in understanding invoices. We will upload an image of an invoice, and you will have to answer any questions based on the uploaded invoices.
"""

input_prompt_text = st.text_input("Input Prompt:", input_promt)

# File uploader for the invoice image
uploaded_file = st.file_uploader("Choose an image of the invoice...", type=("jpg", "jpeg", "png"))
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_column_width=True)

# Button to trigger analysis
if st.button("Analyze Invoice"):
    if input_prompt_text and uploaded_file:
        image_data = input_image_details(uploaded_file)
        response = get_gemini_response(input_prompt_text, image_data, "")
        st.subheader("The Respone is:")
        st.write(response)

        # Convert text to speech
        audio_data = text_to_speech(response)

        # Play the audio
        st.audio(audio_data, format='audio/wav')

        # Save the audio
        # st.audio(audio_data, format='audio/wav', file_format='wav')
    else:
        st.warning("Please input prompt and upload an image")

# Text to Speech Converter
st.title("Text to Speech Converter")

# Input text area for user input
input_text = st.text_area("Enter the text to convert to speech")

#Convert button
if st.button("Covert to Speech"):
    if input_text:
        # Convert text to speech
        audio_data = text_to_speech(input_text)

        # Play the audio
        st.audio(audio_data, format='audio/wav')
    else:
        st.warning("Please enter some text to convert.")


