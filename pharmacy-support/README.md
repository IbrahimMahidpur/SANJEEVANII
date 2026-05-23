# Pharmacy Support Module

Complete healthcare companion with Google Maps integration, real vaccine center data, and AI-powered medical assistance.

## 🚀 Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt

# Start Ollama first
ollama serve
ollama run gpt-oss:120b-cloud

# Run backend
python main.py
```

Backend runs on: http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs on: http://localhost:3000

## 📋 Features

- ✅ **Google Maps Integration** - Find nearby pharmacies, hospitals, doctors
- ✅ **Real Vaccine Data** - CoWIN API integration
- ✅ **AI Chatbot** - GPT-OSS 120B powered medical assistant
- ✅ **Responsive Design** - Works on all devices

## 🔑 API Keys

Google Maps API Key is already configured in `.env.local`

## 📚 Documentation

See `walkthrough.md` for complete documentation.

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: React, Google Maps API
- **AI**: Ollama (GPT-OSS 120B)
- **Data**: CoWIN Public API

## 📞 Support

For issues or questions, check the walkthrough document.
