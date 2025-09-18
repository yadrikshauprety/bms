import streamlit as st
import os
import hashlib
import pdfplumber
import json
from dotenv import load_dotenv
import google.generativeai as genai
from db import get_due_vaccines, log_symptom, get_symptom_history
from gtts import gTTS
import tempfile
import base64
from fpdf import FPDF
from vision import check_anemia

# Load .env and configure Gemini
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.set_page_config(page_title="AI Refugee Health Assistant", page_icon="🩺", layout="wide")
st.title("🩺 AI Virtual Health Assistant for Refugees")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------------- PDF Upload & Hashing ----------------
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

# ---------------- Symptom Input ----------------
st.subheader("💬 Symptom Input")
user_input = st.text_input("Type your symptoms here:")

# Mini-RAG Knowledge Base
def get_guideline(symptom):
    try:
        with open("guidelines.json", "r", encoding="utf-8") as f:
            knowledge = json.load(f)
        for key in knowledge:
            if key.lower() in symptom.lower():
                return knowledge[key]
    except FileNotFoundError:
        return ""
    return "No specific guideline found, but stay hydrated and consult a doctor if it worsens."

# Gemini + RAG
if user_input:
    guideline = get_guideline(user_input)
    prompt = f"Patient symptom: {user_input}. Provide concise triage advice based on this guideline: {guideline}"
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        reply = response.text if response else "⚠️ No AI response"
    except Exception as e:
        reply = f"⚠️ Error: {e}"

    # Color-coded minimal triage
    if "emergency" in reply.lower():
        triage_level = "Emergency"
        reply = "🔴 Emergency: Seek help immediately!\n\n" + reply
    elif "soon" in reply.lower():
        triage_level = "Urgent"
        reply = "🟡 Moderate: Visit a doctor soon.\n\n" + reply
    else:
        triage_level = "Routine"
        reply = "🟢 Mild: Can be managed with self-care.\n\n" + reply

    # Save chat & DB
    st.session_state.chat_history.append(("User", user_input))
    st.session_state.chat_history.append(("AI", reply))
    log_symptom(user_input, triage_level, reply)

    # TTS optional
    if st.checkbox("🔊 Speak response"):
        tts = gTTS(reply, lang="en")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            st.audio(tmp.name, format="audio/mp3")

# ---------------- Chat Display ----------------
st.subheader("💬 Chat History")
for sender, message in st.session_state.chat_history:
    if sender == "User":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 AI:** <span style='color:blue'>{message}</span>", unsafe_allow_html=True)

# ---------------- Camera-based Anemia Check ----------------
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

# ---------------- Vaccination Tracking ----------------
st.subheader("💉 Vaccination Records")
user_id = st.text_input("Enter your user ID for vaccination tracking:")
if user_id:
    vaccines = get_due_vaccines(user_id)
    if vaccines:
        for vaccine, date in vaccines:
            st.markdown(f"- 💉 {vaccine} : {date}")
    else:
        st.info("✅ No pending vaccinations found.")

# ---------------- Download Health Record ----------------
if st.button("📥 Download My Health Record"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "My Health Record", ln=True, align="C")
    pdf.ln(10)

    pdf.multi_cell(0, 10, "Chat History:")
    for sender, message in st.session_state.chat_history:
        pdf.multi_cell(0, 10, f"{sender}: {message}")

    if extracted_text:
        pdf.ln(10)
        pdf.multi_cell(0, 10, "Uploaded Report Extract:")
        pdf.multi_cell(0, 10, extracted_text)

    if pdf_hash:
        pdf.ln(10)
        pdf.multi_cell(0, 10, f"Report Hash: {pdf_hash}")

    file_path = "health_record.pdf"
    pdf.output(file_path)

    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="health_record.pdf">📥 Download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
