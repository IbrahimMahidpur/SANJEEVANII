# Sanjeevani Chatbot - Setup Instructions

## Prerequisites

1. **Ollama**: Make sure Ollama is installed and running on your system.
   - Install from: https://ollama.ai
   - Pull the mistral model: `ollama pull mistral`
   - Start Ollama: `ollama serve`

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies (already done):
   ```bash
   npm install
   ```

3. Start the backend server:
   ```bash
   npm start
   ```

   The server will run on `http://localhost:5000`

## Frontend Setup

1. In a new terminal, navigate to the project root:
   ```bash
   cd ..
   ```

2. Start the frontend (if not already running):
   ```bash
   npm run dev
   ```

   The frontend will run on `http://localhost:3000`

## Usage

1. Make sure both Ollama and the backend server are running
2. Open the frontend in your browser
3. Navigate to the Chat page
4. Start chatting with Sanjeevani!

## Troubleshooting

- **"Failed to get response from Ollama"**: Make sure Ollama is running (`ollama serve`)
- **Backend connection error**: Verify the backend is running on port 5000
- **Model not found**: Run `ollama pull mistral` to download the model

## Features

- **Multilingual Support**: Automatically detects and responds in the user's language
- **Medical Focus**: Specialized in providing accurate medical information
- **Streaming Responses**: Real-time response generation
- **Chat History**: Maintains conversation context
