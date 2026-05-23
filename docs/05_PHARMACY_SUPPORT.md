# 🏥 Feature 5: Pharmacy Support System

## Overview

The **Pharmacy Support System** is a comprehensive healthcare infrastructure module that provides:
- **Nearby pharmacy & hospital locator** (location-based)
- **Real-time medicine availability checker** across pharmacies
- **Doctor finder & appointment booking**
- **Health camp discovery**
- **AI-powered medical chatbot**
- **Insurance verification**

All data is geo-filtered using the Haversine formula and served through a dedicated REST API integrated into the main Express backend.

---

## 📁 Key Files

| File | Role |
|------|------|
| [`src/components/pharmacy/`](../src/components/pharmacy/) | Frontend pharmacy UI components |
| [`src/pages/PharmacySupport.tsx`](../src/pages/PharmacySupport.tsx) | Main page entry point |
| [`backend/pharmacy-api.js`](../backend/pharmacy-api.js) | Pharmacy data CRUD API (22KB) |
| [`backend/pharmacy-support-routes.js`](../backend/pharmacy-support-routes.js) | Real-time support routes |
| [`backend/medicine-api.js`](../backend/medicine-api.js) | Medicine search & pricing |
| [`backend/places-api-routes.js`](../backend/places-api-routes.js) | Google Places integration |
| [`backend/indore-pharmacies.js`](../backend/indore-pharmacies.js) | Indore-specific pharmacy data |
| [`backend/pharmacy-support/`](../backend/pharmacy-support/) | JSON data store directory |
| [`pharmacy-system/`](../pharmacy-system/) | Standalone pharmacy system |
| [`pharmacy-support/`](../pharmacy-support/) | Support service module |

---

## 🧩 Features

### 1. Nearby Facilities Locator
**Endpoint:** `GET /api/pharmacy-support/facilities/nearby`

Finds pharmacies and healthcare facilities within a specified radius using the **Haversine formula** for accurate geo-distance:

```javascript
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2)² + Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)²;
  return Math.round(R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)) * 10) / 10;
}
```

**Query Parameters:**
```
?lat=22.7196&lng=75.8577&radius=5000&type=pharmacy
```

**Response:**
```json
{
  "success": true,
  "count": 12,
  "results": [{
    "id": "pharm_001",
    "name": "Apollo Pharmacy",
    "address": "AB Road, Indore",
    "location": { "lat": 22.7210, "lng": 75.8600 },
    "distance": 0.3,
    "facilityType": "pharmacy",
    "isOpen": true
  }]
}
```

### 2. Medicine Availability Search
**Endpoint:** `GET /api/pharmacy-support/inventory/availability`

Searches all nearby pharmacies for a specific medicine and returns real-time stock status:

```
?medicine=Paracetamol&lat=22.7196&lng=75.8577&radius=5000
```

**Response per pharmacy:**
```json
{
  "pharmacyName": "MedPlus Pharmacy",
  "distance": 1.2,
  "available": true,
  "medicine": {
    "name": "Paracetamol 500mg",
    "quantity": 150,
    "price": 32.50,
    "expiryDate": "2026-08"
  },
  "estimatedPrice": { "amount": 32.50, "currency": "INR" },
  "confidence": 0.95
}
```

### 3. Doctor Finder
**Endpoint:** `GET /api/pharmacy-support/doctors`

Searches by specialization:
```
?specialization=cardiologist
```

Returns full doctor profiles including:
- Hospital name, qualification, experience
- Consultation fee
- Weekly availability schedule
- Languages spoken

### 4. Doctor Appointment Booking
**Check Availability:** `GET /api/pharmacy-support/doctors/:doctorId/availability`
```
?date=2025-06-15
```
Returns available time slots, excluding already-booked slots.

**Book Appointment:** `POST /api/pharmacy-support/doctors/booking`
```json
{
  "doctorId": "dr_001",
  "patientName": "Rahul Sharma",
  "phone": "9876543210",
  "email": "rahul@example.com",
  "date": "2025-06-15",
  "time": "10:00",
  "reason": "Chest pain follow-up"
}
```

**Response:**
```json
{
  "success": true,
  "booking": {
    "id": "booking_1718441200000",
    "doctorName": "Dr. Anita Gupta",
    "hospitalName": "Bombay Hospital",
    "date": "2025-06-15",
    "time": "10:00",
    "status": "confirmed",
    "consultationFee": 600
  }
}
```

### 5. Health Camp Discovery
**Endpoint:** `GET /api/pharmacy-support/health-camps`

Finds nearby free or paid health camps:
```
?lat=22.7196&lng=75.8577&radius=25000&type=eye
```

Returns camps sorted by upcoming date, including:
- Camp type (eye, blood, dental, vaccination, general)
- Date, timing, organizing institution
- Distance from user
- Contact details

### 6. AI Medical Chatbot
**Endpoint:** `POST /api/pharmacy-support/chatbot/query`

```json
{ "message": "What are the symptoms of dengue?" }
```

Powered by the Ollama LLM model with a medical assistant system prompt:
```javascript
const systemPrompt = `You are a helpful medical assistant. Provide concise, accurate 
medical information. Always remind users to consult a doctor for serious issues.`;
```

**Response:**
```json
{
  "success": true,
  "response": "Dengue symptoms include high fever (104°F+)...",
  "sessionId": "session_1718441200000"
}
```

### 7. Google Places Integration
**Endpoint:** `GET /api/places/nearby`

Live Google Places API integration for real-time pharmacies and hospitals near any location.

### 8. Real-Time APIs Module
`backend/realtime-apis.js` — Integrates free public health APIs for live data:
- Government health advisories
- Drug recall notifications
- Hospital bed availability

---

## 📦 Data Store

All pharmacy support data is stored as JSON files in `backend/pharmacy-support/data/`:

| File | Contents |
|------|---------|
| `pharmacies.json` | Pharmacy locations + inventory |
| `doctors.json` | Doctor profiles + availability |
| `health-camps.json` | Upcoming health camp listings |
| `bookings.json` | Appointment bookings (append-only) |

Data is loaded with async file I/O:
```javascript
async function loadJSON(filename) {
  const data = await fs.readFile(path.join(PHARMACY_DATA_PATH, filename), 'utf8');
  return JSON.parse(data);
}
```

---

## 🏗️ Architecture

```
Frontend (PharmacySupport.tsx)
     ↓ User location (browser Geolocation API)
     ↓ Search radius + filters
     ↓
Express Backend (port 5000)
     ├── /api/pharmacy → pharmacyAPI (CRUD)
     ├── /api/pharmacy-support/facilities → nearby search
     ├── /api/pharmacy-support/inventory → medicine availability
     ├── /api/pharmacy-support/doctors → doctor search
     ├── /api/pharmacy-support/doctors/:id/availability → slots
     ├── /api/pharmacy-support/doctors/booking → book appointment
     ├── /api/pharmacy-support/health-camps → camp discovery
     ├── /api/pharmacy-support/chatbot → AI chatbot
     └── /api/places → Google Places (live)
     
Data Layer: pharmacy-support/data/*.json (JSON flat files)
```

---

## 🔌 Complete API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/pharmacy-support/facilities/nearby` | Nearby pharmacies/hospitals |
| GET | `/api/pharmacy-support/inventory/availability` | Medicine stock across pharmacies |
| GET | `/api/pharmacy-support/health-camps` | Nearby health camps |
| GET | `/api/pharmacy-support/doctors` | Find doctors by specialization |
| GET | `/api/pharmacy-support/doctors/:id/availability` | Check appointment slots |
| POST | `/api/pharmacy-support/doctors/booking` | Book appointment |
| POST | `/api/pharmacy-support/chatbot/query` | AI medical query |
| GET | `/api/pharmacy` | Full pharmacy CRUD |
| GET | `/api/medicine` | Medicine database search |
| GET | `/api/places/nearby` | Google Places live search |

---

## 📊 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React + TypeScript |
| Backend | Node.js + Express |
| Geolocation | Browser Geolocation API + Haversine |
| Data | JSON flat files (async fs) |
| Maps | Google Places API |
| AI Chatbot | Ollama LLM |
| Real-time APIs | `realtime-apis.js` (free public APIs) |

---

## 🚀 Running

```bash
cd backend
npm install
npm start   # All pharmacy APIs available at port 5000
```
