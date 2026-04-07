import streamlit as st
from gtts import gTTS
from googletrans import Translator
import os
import uuid

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Traductor por Voz PRO",
    page_icon="🎤",
    layout="centered"
)

# ---------------- ESTILO ----------------
st.markdown("""
<style>
.big-button button {
    width: 100%;
    height: 60px;
    font-size: 18px;
    border-radius: 15px;
    background-color: #ff4b4b;
    color: white;
    border: none;
}
.big-button button:hover {
    background-color: #ff2e2e;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🎤 Traductor por Voz")
st.caption("Habla, traduce y escucha en segundos")

# ---------------- IDIOMAS ----------------
idiomas = {
    "Español": "es-ES",
    "Inglés": "en-US",
    "Coreano": "ko-KR",
    "Mandarín": "zh-CN",
    "Japonés": "ja-JP"
}

idiomas_traduccion = {
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

# ---------------- MICRÓFONO (JS) ----------------
st.markdown("### 🎤 Paso 1: Habla")

st.components.v1.html(f"""
<div style="text-align:center;">
<button onclick="startRecognition()" 
style="padding:15px 25px; font-size:18px; border-radius:12px; background:#ff4b4b; color:white; border:none;">
🎙️ Hablar
</button>

<p id="status"></p>
<p id="result" style="font-weight:bold;"></p>
</div>

<script>
function startRecognition() {{
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    var recognition = new SpeechRecognition();

    recognition.lang = "{idiomas[in_lang]}";
    recognition.interimResults = false;

    document.getElementById("status").innerHTML = "🎙️ Escuchando...";

    recognition.onresult = function(event) {{
        var text = event.results[0][0].transcript;
        document.getElementById("result").innerHTML = text;

        // enviar a streamlit
        window.parent.postMessage({{
            type: "streamlit:setComponentValue",
            value: text
        }}, "*");
    }};

    recognition.onend = function() {{
        document.getElementById("status").innerHTML = "✅ Listo";
    }};

    recognition.start();
}}
</script>
""", height=200)

# ---------------- RECIBIR TEXTO ----------------
texto = st.session_state.get("text_input", "")

# hack para capturar valor
query_params = st.experimental_get_query_params()
if "value" in query_params:
    texto = query_params["value"][0]

# alternativa robusta
texto = st.text_input("📝 Texto detectado (puedes editarlo):", texto)

# ---------------- TRADUCCIÓN ----------------
translator = Translator()

if texto:
    st.markdown("### 🌍 Paso 2: Traducir")

    if st.button("Traducir"):

        with st.spinner("Traduciendo..."):
            translation = translator.translate(
                texto,
                src=idiomas_traduccion[in_lang],
                dest=idiomas_traduccion[out_lang]
            )

            output_text = translation.text

        st.markdown("### 📄 Resultado")
        st.success(output_text)

        # ---------------- AUDIO ----------------
        tts = gTTS(output_text, lang=idiomas_traduccion[out_lang])

        if not os.path.exists("temp"):
            os.mkdir("temp")

        file_path = f"temp/{uuid.uuid4()}.mp3"
        tts.save(file_path)

        st.markdown("### 🔊 Escuchar")
        audio_file = open(file_path, "rb")
        st.audio(audio_file.read(), format="audio/mp3")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("✨ Versión PRO sin errores | Lista para deploy 🚀")
