import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Traductor por Voz",
    page_icon="🎤",
    layout="centered"
)

# ---------------- ESTILO ----------------
st.markdown("""
<style>
/* Quitar sensación gris */
section[data-testid="stSidebar"] {
    background-color: #fafafa;
}

/* Botones más visibles */
.stButton > button {
    border-radius: 12px;
    border: none;
    background-color: #ff4b4b;
    color: white;
    font-weight: bold;
}

.stButton > button:hover {
    background-color: #ff2e2e;
}

/* Selectbox más claros */
div[data-baseweb="select"] {
    background-color: white !important;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🎤 Traductor por Voz")
st.write("Habla y obtén tu traducción en segundos.")

image = Image.open('OIG7.jpg')
st.image(image, width=220)

# ---------------- IDIOMAS ----------------
idiomas = {
    "Español": "es",
    "Inglés": "en",
    "Coreano": "ko",
    "Mandarín": "zh-cn",
    "Japonés": "ja"
}

# ---------------- SELECTORES PRINCIPALES ----------------
st.markdown("### 🌍 Configura tu traducción")

col1, col2 = st.columns(2)

with col1:
    in_lang = st.selectbox("Idioma que hablas", list(idiomas.keys()))

with col2:
    out_lang = st.selectbox("Idioma al que quieres traducir", list(idiomas.keys()))

# ---------------- BOTÓN GRABAR ----------------
st.markdown("### 🎤 Paso 1: Habla")

stt_button = Button(label="🎙️ Empezar a grabar", width=250)

stt_button.js_on_event("button_click", CustomJS(code="""
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognition = new SpeechRecognition();

    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'es-ES';

    document.dispatchEvent(new CustomEvent("LISTENING", {detail: "start"}));

    recognition.onresult = function (e) {
        var text = e.results[0][0].transcript;
        document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: text}));
    }

    recognition.onend = function() {
        document.dispatchEvent(new CustomEvent("LISTENING", {detail: "stop"}));
    }

    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT,LISTENING",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# ---------------- ESTADO ----------------
if result and "LISTENING" in result:
    if result["LISTENING"] == "start":
        st.info("🎙️ Te estoy escuchando...")
    elif result["LISTENING"] == "stop":
        st.success("✅ Listo")

# ---------------- TEXTO ----------------
text = ""

if result and "GET_TEXT" in result:
    text = result.get("GET_TEXT")
    st.markdown("### 📝 Esto fue lo que dijiste")
    st.success(text)

# ---------------- TRADUCCIÓN ----------------
translator = Translator()

def text_to_speech(input_language, output_language, text):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text

    tts = gTTS(trans_text, lang=output_language)

    if not os.path.exists("temp"):
        os.mkdir("temp")

    file_path = "temp/audio.mp3"
    tts.save(file_path)

    return file_path, trans_text

# ---------------- BOTÓN TRADUCIR ----------------
if text:
    st.markdown("### 🌍 Paso 2: Traducir")

    if st.button("Traducir"):

        with st.spinner("Traduciendo..."):
            audio_path, output_text = text_to_speech(
                idiomas[in_lang],
                idiomas[out_lang],
                text
            )

        st.markdown("### 📄 Resultado")
        st.success(output_text)

        st.markdown("### 🔊 Escuchar")
        st.audio(audio_path)

# ---------------- LIMPIEZA ----------------
def remove_files():
    files = glob.glob("temp/*.mp3")
    now = time.time()
    for f in files:
        if os.stat(f).st_mtime < now - 86400:
            os.remove(f)

remove_files()

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Hecho para una experiencia simple y clara ✨")
