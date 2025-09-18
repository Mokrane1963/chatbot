# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 20:28:01 2025

@author: mokrane
"""
#python -m streamlit run moteurAR_st.py
import streamlit as st
import requests
import json
from PIL import Image
import io
import base64
import sys

# Dictionnaire de traduction
TRANSLATIONS = {
    "fr": {
        "title": "💬 Assistant Ollama",
        "subtitle": "",
        "settings": "⚙ Paramètres du Chat",
        "model": "Modèle IA",
        "creativity": "Créativité (température)",
        "max_length": "Longueur max des réponses",
        "repeat_penalty": "Pénalité de répétition",
        "upload": "📤 Téléverser une image",
        "input_placeholder": "Écrivez votre message...",
        "thinking": "Réflexion en cours",
        "clear": "🗑️ Effacer la discussion",
        "save": "💾 Sauvegarder l'historique",
        "saved": "Historique sauvegardé!",
        "quit": "🚪 Quitter le chat",
        "error": "❌ Erreur: {}"
    },
    "ar": {
        "title": "💬 مساعد أولاما",
        "subtitle": "",
        "settings": "⚙ إعدادات الدردشة",
        "model": "نموذج الذكاء الاصطناعي",
        "creativity": "الإبداع (درجة الحرارة)",
        "max_length": "الحد الأقصى لطول الإجابات",
        "repeat_penalty": "عقوبة التكرار",
        "upload": "📤 رفع صورة",
        "input_placeholder": "اكتب رسالتك هنا ... ",
        "thinking": "...يفكر",
        "clear": "🗑️ مسح المحادثة",
        "save": "💾 حفظ المحادثة",
        "saved": "!تم الحفظ",
        "quit": "🚪 خروج",
        "error": "❌ خطأ: {}"
    }
}

# Configuration de la page
st.set_page_config(
    page_title="Assistant Ollama Chat",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation de la session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "current_language" not in st.session_state:
    st.session_state.current_language = "fr"  # fr par défaut

def t(key):
    """Fonction de traduction"""
    return TRANSLATIONS[st.session_state.current_language][key]

# Fonction pour formater le texte RTL
def format_rtl(text):
    """Version simplifiée sans arabic-reshaper"""
    return f'<div style="direction: rtl; text-align: right; unicode-bidi: embed; font-family: Arial, sans-serif;">{text}</div>'

# Header avec logo et titre



    st.title(t("title"))
    st.markdown("""
<div style="text-align: left; font-family: Courier New;">
  <p style="color: red; 
            font-weight: bold; 
            font-size: 18px; 
            margin-top: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
    analyse, description, réponse à des questions sur une image
  </p>
</div>
""", unsafe_allow_html=True)

# Sélecteur de langue dans la sidebar
with st.sidebar:
    st.session_state.current_language = st.radio(
        "Langue / اللغة",
        ["fr", "ar"],
        index=0 if st.session_state.current_language == "fr" else 1,
        horizontal=True
    )

# Texte descriptif sous le titre
st.markdown(f"""
<style>
.subtitle {{
    text-align: center;
    font-size: 16px;
    color: #666;
    margin-bottom: 20px;
}}
.rtl-text {{
    direction: rtl;
    text-align: right;
    font-family: 'Arial', sans-serif;
}}
</style>
<p class="subtitle">{t("subtitle")}</p>
""", unsafe_allow_html=True)

# Sidebar pour les paramètres
with st.sidebar:
    st.header(t("settings"))
    
    st.session_state.model = st.selectbox(
        t("model"),
        ["Gemma3:12b","Llama3.2-vision:11b"],
        index=0,help='choisissez un modèle'
    )
    
    st.session_state.temperature = st.slider(
        t("creativity"),
        0.1, 1.0, 0.7
    )
    
    st.session_state.max_tokens = st.slider(
        t("max_length"),
        100, 500, 5000
    )
    
    st.session_state.repeat_penalty = st.slider(
        t("repeat_penalty"),
        1.0, 2.0, 1.1, 0.1
    )

# Fonction pour encoder les images
def encode_image(uploaded_file):
    img = Image.open(uploaded_file)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# Zone d'upload d'images
uploaded_file = st.file_uploader(
    t("upload"), 
    type=["jpg", "jpeg", "png"]
)
if uploaded_file:
    st.session_state.uploaded_image = uploaded_file

# Affichage de l'historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["type"] == "text":
            if message.get("language", "fr") == "ar":
                st.markdown(format_rtl(message["content"]), unsafe_allow_html=True)
            else:
                st.markdown(message["content"])
        elif message["type"] == "image":
            st.image(message["content"], width=300)

# Gestion de la discussion
if prompt := st.chat_input(t("input_placeholder")):
    # Déterminer la langue du message
    lang = "ar" if st.session_state.current_language == "ar" else "fr"
    
    # Ajout du message utilisateur
    st.session_state.messages.append({
        "role": "user", 
        "type": "text", 
        "content": prompt,
        "language": lang
    })
    
    # Gestion de l'image uploadée
    image_content = None
    if st.session_state.uploaded_image:
        st.session_state.messages.append({
            "role": "user", 
            "type": "image", 
            "content": st.session_state.uploaded_image
        })
        image_content = encode_image(st.session_state.uploaded_image)
        st.session_state.uploaded_image = None

    # Affichage des messages utilisateur
    with st.chat_message("user"):
        if lang == "ar":
            st.markdown(format_rtl(prompt), unsafe_allow_html=True)
        else:
            st.markdown(prompt)
        if image_content:
            st.image(Image.open(io.BytesIO(base64.b64decode(image_content))), width=300)

    # Génération de la réponse en streaming
    with st.chat_message("assistant"):
        with st.spinner(t("thinking")):
            response_container = st.empty()
            full_response = ""
            
            payload = {
                "model": st.session_state.model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": st.session_state.temperature,
                    "num_predict": st.session_state.max_tokens,
                    'repeat_penalty': st.session_state.repeat_penalty
                }
            }
            
            if image_content:
                payload["images"] = [image_content]
            
            try:
                with requests.post(
                    "http://localhost:11434/api/generate",
                    json=payload,
                    stream=True
                ) as response:
                    response.raise_for_status()
                    
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'response' in chunk:
                                full_response += chunk['response']
                                if lang == "ar":
                                    response_container.markdown(format_rtl(full_response), unsafe_allow_html=True)
                                else:
                                    response_container.markdown(full_response)
                            
                            if chunk.get('done', False):
                                st.session_state.messages.append({
                                    "role": "assistant", 
                                    "type": "text", 
                                    "content": full_response,
                                    "language": lang
                                })
                                break
            
            except Exception as e:
                error_msg = t("error").format(str(e))
                if lang == "ar":
                    response_container.markdown(format_rtl(error_msg), unsafe_allow_html=True)
                else:
                    response_container.markdown(error_msg)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "type": "text", 
                    "content": error_msg,
                    "language": lang
                })

# Boutons de contrôle
col1, col2 = st.columns(2)
with col1:
    if st.button(t("clear")):
        st.session_state.messages = []
        st.rerun()
with col2:
    if st.button(t("save")): 
        with open("historique_chat.json", "w") as f:
            json.dump(st.session_state.messages, f)
        st.success(t("saved"))

# Bouton Quitter
with st.sidebar:
    if st.button(t("quit")):
        st.session_state.clear()
        st.rerun()
        st.stop()
        sys.exit()