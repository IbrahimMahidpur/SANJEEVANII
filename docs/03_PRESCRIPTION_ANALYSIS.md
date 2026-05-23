# 💊 Feature 3: Prescription Analysis (AI-Powered OCR)

## Overview

The **Prescription Analysis** feature allows users to upload a photo of a handwritten or printed prescription and have it automatically processed using a two-stage AI pipeline:

1. **OCR Stage** — A Flask/Python microservice extracts raw text from the image
2. **LLM Refinement Stage** — Ollama's `llama3.2` model parses the raw text into structured, human-readable medicine data

The output includes medicine names, dosages, frequency, duration, instructions, patient/doctor info, and a plain-language usage guide.

---

## 📁 Key Files

| File | Role |
|------|------|
| [`src/pages/PrescriptionAnalysis.tsx`](../src/pages/PrescriptionAnalysis.tsx) | Frontend — upload UI + results display |
| [`prescriptionAnalysis/MediScribe-OCR/`](../prescriptionAnalysis/MediScribe-OCR/) | Python OCR microservice (Flask, port 5001) |
| [`backend/server.js`](../backend/server.js) | `/api/prescription/refine` — LLM refinement endpoint |

---

## 🔄 How It Works

### Two-Stage Pipeline

```
User uploads image (JPG/PNG/PDF)
         ↓
Stage 1: Flask OCR Service (port 5001)
  - Endpoint: POST /upload
  - Processes image → returns raw_text (OCR output)
         ↓
Stage 2: Ollama LLM Refinement (port 5000)
  - Endpoint: POST /api/prescription/refine
  - Input: { text: raw_text }
  - Output: Structured JSON (medicines, patient, doctor, instructions)
         ↓
Frontend renders structured result cards
```

---

## 🧩 Feature Breakdown

### 1. Drag & Drop File Upload
- Accepts: `image/*`, `.pdf`
- Instant image preview after selection
- Shows file name and size
- Animated dashed border upload zone

```tsx
<input type="file" accept="image/*,.pdf" onChange={handleFileSelect} />
```

### 2. OCR Text Extraction (Stage 1)
```typescript
const formData = new FormData();
formData.append('prescription_image', selectedFile);
const response = await fetch('http://localhost:5001/upload', {
  method: 'POST',
  body: formData
});
// Returns: { raw_text: "Dr. Smith\nParacetamol 500mg..." }
```

The Python OCR service processes the image and returns extracted text.

### 3. LLM Structured Parsing (Stage 2)
```typescript
const refineResponse = await fetch('http://localhost:5000/api/prescription/refine', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: data.raw_text })
});
```

**LLM Prompt (in server.js):**
```
You are an expert medical prescription parser. Extract structured information from OCR text.
Return ONLY valid JSON:
{
  "medicines": [
    { 
      "name": "Medicine Name",
      "type": "Tablet/Syrup/Injection",
      "dosage": "500mg",
      "frequency": "twice daily after food",
      "duration": "5 days",
      "instructions": "take with warm water"
    }
  ],
  "patient_name": "Name or null",
  "doctor_name": "Name or null",
  "date": "Date or null",
  "instructions": ["Instruction 1"],
  "usage_guide": "Simple paragraph explaining how to take medicines"
}
```

Model used: `llama3.2` (Ollama, JSON mode enabled)

### 4. Structured Results Display

#### Patient & Doctor Info Card
```
Patient: [Name]    Doctor: [Name]    Date: [Date]
```

#### Medicine Cards
Each prescribed medicine gets its own card showing:
- **Name** + medicine type (Tablet/Syrup/Injection)
- 💊 Dosage badge (e.g., `500mg`)
- ⏱️ Duration badge (e.g., `5 days`)
- When to take (frequency)
- How to take (instructions)

#### Usage Guide Section
A plain-language paragraph explaining the entire prescription in simple terms.

#### Doctor's Notes
Additional instructions extracted from the prescription.

#### Raw OCR Debug View
A collapsible `<details>` section shows the original extracted text for verification.

### 5. Graceful Fallback
If Stage 2 (LLM refinement) fails:
- Warning banner shown
- Raw OCR text displayed in monospace format
- Still usable even without structured output

### 6. Loading States
- "Analyzing..." button state with spinner during processing
- `isAnalyzing` flag disables button to prevent double-submissions

---

## 🔌 API Endpoints

### `POST http://localhost:5001/upload` (Python OCR Service)
**Request:** `multipart/form-data`
- `prescription_image`: File (JPG/PNG/PDF)

**Response:**
```json
{
  "raw_text": "Dr. Sharma\nPatient: Rahul\nParacetamol 500mg - 1 tablet twice daily for 5 days\nCefixime 200mg - 1 tablet once daily for 7 days"
}
```

### `POST /api/prescription/refine` (Express Backend)
**Request:**
```json
{ "text": "raw OCR text from prescription" }
```

**Response:**
```json
{
  "medicines": [
    {
      "name": "Paracetamol",
      "type": "Tablet",
      "dosage": "500mg",
      "frequency": "twice daily",
      "duration": "5 days",
      "instructions": "after food"
    }
  ],
  "patient_name": "Rahul",
  "doctor_name": "Dr. Sharma",
  "date": null,
  "instructions": ["Stay hydrated", "Rest well"],
  "usage_guide": "Take Paracetamol 500mg twice daily after meals for 5 days..."
}
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│   React Frontend (port 5173)    │
│   PrescriptionAnalysis.tsx      │
│   - File upload UI              │
│   - Preview image               │
│   - Render results              │
└───────────┬─────────────────────┘
            │ POST multipart
            ↓
┌─────────────────────────────────┐
│  Python Flask OCR (port 5001)  │
│  prescriptionAnalysis/          │
│  - Image preprocessing          │
│  - OCR text extraction          │
└───────────┬─────────────────────┘
            │ raw_text
            ↓
┌─────────────────────────────────┐
│  Express Backend (port 5000)   │
│  /api/prescription/refine       │
│  - Ollama llama3.2 (JSON mode)  │
│  - Structured data extraction   │
└─────────────────────────────────┘
```

---

## 📊 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React + TypeScript |
| OCR Service | Python + Flask (port 5001) |
| LLM Parsing | Ollama `llama3.2` (JSON mode) |
| Backend | Node.js + Express (port 5000) |
| Icons | Lucide React |

---

## 🚀 Setup & Running

```bash
# 1. Start Python OCR service
cd prescriptionAnalysis/MediScribe-OCR
pip install -r requirements.txt
python app.py   # Runs on port 5001

# 2. Start main backend
cd backend
npm start   # Runs on port 5000

# 3. Start frontend
npm run dev   # Runs on port 5173
```

Navigate to: `http://localhost:5173/prescription-analysis`

---

## 📸 Supported Input Formats

- **JPEG / JPG** — Most common for photos
- **PNG** — Screenshots and scanned documents
- **PDF** — Printed prescriptions

**Best results:** Clear lighting, prescription text horizontal, minimal shadows
