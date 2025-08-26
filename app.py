import google.generativeai as genai
import streamlit as st
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Mengambil API Key dari secrets.toml di Streamlit Cloud
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("API Key belum diatur. Harap tambahkan API Key ke 'secrets.toml' di Streamlit Cloud.")
    st.stop()

# Nama model Gemini yang akan digunakan
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Saya adalah Ahli Masak. Saya akan memberikan jenis resep yang anda inginkan. Jawaban singkat dan jelas. Tolak pertanyaan non-masakan."]
    },
    {
        "role": "model",
        "parts": ["Baik! Saya akan memberikan resep yang anda inginkan."]
    }
]

# ==============================================================================
# FUNGSI UTAMA CHATBOT UNTUK STREAMLIT
# ==============================================================================

# Konfigurasi Streamlit Page
st.set_page_config(page_title="Chatbot Ahli Masak", page_icon="👨‍🍳")
st.title("Chatbot Ahli Masak")
st.markdown("Ketik jenis resep yang Anda inginkan di bawah ini.")

# Inisialisasi model dan chat
@st.cache_resource
def get_gemini_model():
    genai.configure(api_key=API_KEY)
    return genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )

model = get_gemini_model()

# Mengelola riwayat chat di Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT

# Menampilkan pesan-pesan yang ada di riwayat
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["parts"][0])
    else:
        st.chat_message("assistant").write(message["parts"][0])

# Mengelola input pengguna
if user_input := st.chat_input("Apa resep yang Anda inginkan?"):
    st.session_state.messages.append({"role": "user", "parts": [user_input]})
    st.chat_message("user").write(user_input)

    try:
        chat = model.start_chat(history=st.session_state.messages)
        response = chat.send_message(user_input, request_options={"timeout": 60})
        
        if response and response.text:
            st.session_state.messages.append({"role": "model", "parts": [response.text]})
            st.chat_message("assistant").write(response.text)
        else:
            st.chat_message("assistant").write("Maaf, saya tidak bisa memberikan balasan.")
    except Exception as e:
        st.chat_message("assistant").write(f"Maaf, terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
