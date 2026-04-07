import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
import os

# CONFIG
st.set_page_config(page_title="Traductor por Voz", page_icon="🎤")

st.title("🎤 Traductor por Voz")
st.write("Presiona el botón y habla")

idiomas = {
    "Español": "es",
    "Inglés": "en",
    "Coreano": "ko",
    "Mandarín": "zh-cn",
    "Japonés": "ja"
}

col1, col2 = st.columns(2)

with col1:
    in_lang = st.selectbox("Idioma que hablas", list(idiomas.keys()))

with col2:
    out_lang = st.selectbox("Traducir a", list(idiomas.keys()))

translator = Translator()

# 🎤 BOTÓN GRABAR
if st.button("🎤 Grabar voz"):

    r = sr.Recognizer()

    with sr.Microphone() as source:
        st.info("🎙️ Escuchando...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language=idiomas[in_lang])
        st.success(f"📝 {text}")

        # TRADUCIR
        translation = translator.translate(text, src=idiomas[in_lang], dest=idiomas[out_lang])
        output_text = translation.text

        st.success(f"🌍 {output_text}")

        # AUDIO
        tts = gTTS(output_text, lang=idiomas[out_lang])
        tts.save("audio.mp3")

        audio_file = open("audio.mp3", "rb")
        st.audio(audio_file.read(), format="audio/mp3")

    except:
        st.error("❌ No entendí lo que dijiste")
