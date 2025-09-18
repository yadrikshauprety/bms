# 🩺 AI-Enabled Virtual Health Assistant for Refugees

Refugees and displaced communities often lack access to reliable healthcare.  
This project provides an **AI-powered platform** that empowers vulnerable populations with accessible health support.  

---

## ✨ Key Features

- ✅ **Medical Report Simplification** – Upload PDF medical reports, auto-extract text, and generate a secure SHA-256 hash for data integrity.  
- ✅ **Symptom Checker with AI Triage** – Input symptoms via text or voice. Get AI-powered advice with color-coded severity levels (🔴 Emergency, 🟡 Moderate, 🟢 Mild).  
- ✅ **Voice Input & Output** – Speech-to-Text for users with low literacy and Text-to-Speech for multilingual accessibility.  
- ✅ **Camera-Based Anemia Detection** – Prototype using OpenCV to analyze eye/lip images for anemia signs.  
- ✅ **Vaccination Tracking** – Personalized vaccination records linked to user ID and stored in SQLite.  
- ✅ **Nearby Humanitarian Health Services** – Lookup from `clinics.json` for closest available services.  
- ✅ **Downloadable Health Records** – Generate a personal PDF record of chats, uploaded reports, and report hashes.  

---

## 🛠️ Tech Stack

- **Frontend/UI:** [Streamlit](https://streamlit.io/)  
- **AI Model:** [Google Gemini](https://ai.google.dev/) via `google-generativeai`  
- **Database:** SQLite3  
- **PDF Handling:** `pdfplumber`, `fpdf`  
- **Voice:** Vosk (Speech-to-Text), `gTTS` (Text-to-Speech)  
- **Camera/ML:** OpenCV (`cv2`)  
- **Env Management:** `python-dotenv`  

---

## 📂 Project Structure

📁 refugeehealthassistant
├── app.py # Main Streamlit app
├── db.py # Database logic (symptoms, vaccinations)
├── speech.py # Voice input handler
├── vision.py # Camera-based anemia check
├── guidelines.json # Mini knowledge base for common symptoms
├── clinics.json # List of nearby health services
├── requirements.txt # Python dependencies
└── README.md # Project documentation


---

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/refugeehealthassistant.git
   cd refugeehealthassistant
2. Create a virtual env:
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   
3. Install depedencies:
    pip install -r requirements.txt
   
4.Add your gemini api key in a .env file:
  GOOGLE_API_KEY=your_api_key_here

## Usage

  Run the Streamlit app:

  streamlit run app.py


  Then open http://localhost:8501
  in your browser.


## 👨‍👩‍👧 Authors

Built with ❤️ for humanitarian innovation.

Team: VitalSync
