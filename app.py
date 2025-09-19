import streamlit as st
import os
import hashlib
import pdfplumber
import json
from dotenv import load_dotenv
import google.generativeai as genai
from speech import speech_to_text
from vision import check_anemia
from db import get_due_vaccines, log_symptom, get_symptom_history
from gtts import gTTS
import tempfile
import base64
from fpdf import FPDF

# Load .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Page config
st.set_page_config(page_title="AI Refugee Health Assistant", page_icon="🩺", layout="wide")
st.title("🩺 AI Virtual Health Assistant for Refugees")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- Sidebar Navigation ----------------
page = st.sidebar.selectbox(
    "Navigate",
    ["💬 Symptom Checker", "📄 Upload Medical Report", "📷 Camera Health Check", "💉 Vaccination Records", "🏥 Nearby Health Services"]
)

# ---------------- PDF Upload & Hashing ----------------
if page == "📄 Upload Medical Report":
    st.subheader("📄 Upload Medical Report (PDF)")
    uploaded_pdf = st.file_uploader("Upload your lab report:", type=["pdf"])
    extracted_text = ""
    pdf_hash = ""

    if uploaded_pdf:
        pdf_hash = hashlib.sha256(uploaded_pdf.read()).hexdigest()
        st.success(f"✅ Report securely hashed: {pdf_hash[:20]}...")
        uploaded_pdf.seek(0)
        with pdfplumber.open(uploaded_pdf) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() or ""

        if extracted_text:
            st.text_area("📑 Extracted Text from Report:", extracted_text, height=150)

# ---------------- Symptom Checker ----------------
elif page == "💬 Symptom Checker":
    st.subheader("💬 Symptom Input")
    user_input_text = st.text_input("Type your symptoms here:")
    lang = st.selectbox("🌐 Select language:", ["en", "hi", "bn"])
    user_input_voice = None

    if st.button("🎙️ Start Voice Input"):
        try:
            user_input_voice = speech_to_text(lang=lang)
            st.success(f"🗣️ You said: {user_input_voice}")
        except Exception as e:
            st.error(f"Voice input failed: {e}")

    user_input = user_input_voice if user_input_voice else user_input_text

    if user_input:
        # Mini-RAG Knowledge Base
        guideline = "Stay hydrated and consult a doctor if symptoms worsen."
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"Patient symptom: {user_input}. Provide minimal triage advice."
            response = model.generate_content(prompt)
            reply = response.text if response else "⚠️ No AI response"
        except Exception as e:
            reply = f"⚠️ Error: {e}"

        # Color coded advice
        if "emergency" in reply.lower():
            reply = "🔴 Emergency: Seek help immediately!\n\n" + reply
        elif "soon" in reply.lower():
            reply = "🟡 Moderate: Visit a doctor soon.\n\n" + reply
        else:
            reply = "🟢 Mild: Can be managed with self-care.\n\n" + reply

        # Save to DB
        log_symptom("user1", user_input, reply)

        # Add to chat
        st.session_state.chat_history.append(("User", user_input))
        st.session_state.chat_history.append(("AI", reply))

        # Optional TTS
        if st.checkbox("🔊 Speak response"):
            tts = gTTS(reply, lang="en")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
                st.audio(tmp.name, format="audio/mp3")

        # ---------------- Knowledge Graph Insights ----------------
        knowledge_graph = {
            "diarrhea": {
                "causes": ["infection", "food poisoning", "dehydration"],
                "treatments": ["ORS", "hydration", "probiotics"],
                "emergency": ["severe dehydration", "blood in stool"]
            },
            "fever": {
                "causes": ["infection", "malaria", "flu"],
                "treatments": ["paracetamol", "hydration", "rest"],
                "emergency": ["very high fever", "confusion", "seizures"]
            },
            "cough": {
                "causes": ["cold", "flu", "respiratory infection"],
                "treatments": ["steam inhalation", "hydration", "rest"],
                "emergency": ["difficulty breathing", "chest pain"]
            }
        }
        symptom_lower = user_input.lower()
        kg_advice = knowledge_graph.get(symptom_lower, None)
        if kg_advice:
            st.markdown("**💡 Knowledge Graph Insights:**")
            st.markdown(f"- Causes: {', '.join(kg_advice['causes'])}")
            st.markdown(f"- Treatments: {', '.join(kg_advice['treatments'])}")
            if kg_advice.get("emergency"):
                st.markdown(f"- Emergency Signs: {', '.join(kg_advice['emergency'])}")

    # Display chat
    st.subheader("💬 Chat History")
    for sender, message  in st.session_state.chat_history:
        if sender == "User":
            st.markdown(f"**🧑 You:** {message}")
        else:
            st.markdown(f"**🤖 AI:** <span style='color:blue'>{message}</span>", unsafe_allow_html=True)

# ---------------- Camera Health Check ----------------
elif page == "📷 Camera Health Check":
    st.subheader("📷 Camera Health Check (Anemia)")
    if st.button("Start Camera Check"):
        import cv2
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            st.image(frame, channels="BGR")
            result = check_anemia(frame)
            st.success(f"Camera Analysis: {result}")
        else:
            st.error("Camera not accessible")
        cap.release()

# ---------------- Vaccination Records ----------------
elif page == "💉 Vaccination Records":
    st.subheader("💉 Vaccination Records")
    user_id = st.text_input("Enter your user ID:")
    if user_id:
        vaccines = get_due_vaccines(user_id)
        if vaccines:
            for vaccine, date in vaccines:
                st.markdown(f"- 💉 {vaccine} : {date}")
        else:
            st.info("✅ No pending vaccinations found.")

        # Show past symptom history
        st.subheader("📜 Symptom History")
        history = get_symptom_history()
        if history:
            for sym, reply in history:
                st.markdown(f"- **{sym}** → {reply}")
        else:
            st.info("No symptom history yet.")

# ---------------- Nearby Health Services ----------------
elif page == "🏥 Nearby Health Services":
    st.subheader("🏥 Nearby Health Services")
    clinics_file = "clinics.json"
    if os.path.exists(clinics_file):
        with open(clinics_file, "r", encoding="utf-8") as f:
            clinics = json.load(f)
    else:
        clinics = []
        st.warning("⚠️ clinics.json file not found. Nearby health services cannot be displayed.")

    service_type = st.selectbox("Select service needed:", ["general", "vaccination", "anemia"])
    nearby = [c for c in clinics if service_type.lower() in [s.lower() for s in c.get("services", [])]]
    if nearby:
        for clinic in nearby:
            st.markdown(f"- **{clinic['name']}** | {clinic['address']} | {clinic['phone']}")
    else:
        st.info("No nearby clinics found for the selected service.")
