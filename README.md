# 🤖 Marky - AI Marketing Chatbot

Marky is a conversational AI chatbot developed to assist users with digital marketing queries. Designed for small and medium-sized businesses, Marky leverages NLP, machine learning, and OpenAI to provide personalized marketing support through a web-based interface.

---

## 📦 Setup & Installation

Follow these steps to download, install, and run Marky on your local machine:

### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Methvin Marketing Chatbot (Marky)"
```

### 2. Create and Activate a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Packages
Install all dependencies using pip:
```bash
pip install -r requirements.txt
```
If `requirements.txt` is missing, install manually:
```bash
pip install flask nltk torch openai google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 4. Set Up API Keys
- Obtain API keys for:
  - [OpenAI](https://platform.openai.com/)
  - [Google Calendar API](https://developers.google.com/calendar)
  - [Google Custom Search](https://programmablesearchengine.google.com/)
- Add your API keys to a `.env` file or directly in the configuration section of the code as required.

### 5. Run the Application
```bash
python app.py
```
The chatbot will be available at `http://127.0.0.1:5000/` in your browser.

---

## 📌 Features

- Natural Language Understanding (NLU)
- Personalized marketing advice
- Voice input support
- Real-time chat response using ML models
- Integration with:
  - OpenAI API (fallback queries)
  - Google Calendar (event scheduling)
  - Google Search API (dynamic lookup)
- Dark/Light mode interface
- Self-learning from chat logs
- Scalable and modular codebase

---

## 🛠️ Technologies Used

| Component        | Technology               |
|------------------|--------------------------|
| Backend Framework| Flask (Python)           |
| NLP Toolkit      | NLTK                     |
| ML Framework     | PyTorch, DistilBERT      |
| Frontend         | HTML, CSS, JavaScript    |
| Voice Input      | Web Speech API           |
| Database         | JSON, CSV, SQLite        |
| APIs             | OpenAI, Google Calendar  |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Pip / Virtualenv
- API keys for:
  - [OpenAI](https://platform.openai.com/)
  - [Google Calendar API](https://developers.google.com/calendar)
  - [Google Custom Search](https://programmablesearchengine.google.com/)

## Future Enhancements
- Multilingual support
- Sentiment-based tone adjustment
- File upload and analysis (PDF, image)
- Response rating (👍/👎) and feedback learning
- Full voice-enabled interactions (TTS + STT)

## References
- NLTK: https://www.nltk.org/
- PyTorch: https://pytorch.org/
- OpenAI API: https://platform.openai.com/
- Flask: https://flask.palletsprojects.com/
- Google Calendar API: https://developers.google.com/calendar

👥 Authors
- Dison Methvin – E178054
- Ralph Shenal – E007487 

