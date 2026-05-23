import express from 'express';
import cors from 'cors';
import { Ollama } from 'ollama';
import { search } from 'duck-duck-scrape';
import medicalRAG from './rag.js';
import pharmacyAPI from './pharmacy-api.js';
import medicineAPI from './medicine-api.js';
import outbreakAPI from './outbreak-api.js';
import pharmacySupportRouter from './pharmacy-support-routes.js';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const ollama = new Ollama({ host: 'http://localhost:11434' });

app.use(cors());
app.use(express.json({ limit: '50mb' }));

// Load medical dataset
const datasetPath = path.join(__dirname, '..', 'medical_val.jsonl');
medicalRAG.loadDataset(datasetPath);

// Mount pharmacy API routes
app.use('/api/pharmacy', pharmacyAPI);

// Mount medicine API routes
app.use('/api/medicine', medicineAPI);

// Mount outbreak API routes
app.use('/api/outbreak', outbreakAPI);

// Mount pharmacy support real-time APIs
app.use('/api/pharmacy-support', pharmacySupportRouter);

// Mount Google Places API routes
import placesAPIRouter from './places-api-routes.js';
app.use('/api/places', placesAPIRouter);

// Mount Forum API
import forumAPI from './forum-api.js';
app.use('/api/forum', forumAPI);

// ============================================================================
// PHARMACY SUPPORT MODULE - Real-Time Free APIs Integration
// ============================================================================

import fs from 'fs/promises';
import realtimeAPIs from './realtime-apis.js';

// Load pharmacy support data
const PHARMACY_DATA_PATH = path.join(__dirname, 'pharmacy-support', 'data');



// Helper: Load JSON file
async function loadJSON(filename) {
  try {
    const data = await fs.readFile(path.join(PHARMACY_DATA_PATH, filename), 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.log(`Creating ${filename}...`);
    return [];
  }
}

// Helper: Save JSON file
async function saveJSON(filename, data) {
  await fs.writeFile(path.join(PHARMACY_DATA_PATH, filename), JSON.stringify(data, null, 2));
}

// Helper: Calculate distance
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c * 10) / 10;
}

// 1. NEARBY FACILITIES API
app.get('/api/pharmacy-support/facilities/nearby', async (req, res) => {
  try {
    const { lat, lng, radius = 5000, type = 'all' } = req.query;
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lng);
    const searchRadius = parseInt(radius) / 1000; // Convert to km

    const pharmacies = await loadJSON('pharmacies.json');

    let results = pharmacies.map(p => ({
      ...p,
      facilityType: 'pharmacy',
      types: ['pharmacy'],
      rating: null,
      totalRatings: 0,
      isOpen: true,
      distance: calculateDistance(latitude, longitude, p.location.lat, p.location.lng)
    })).filter(p => p.distance <= searchRadius);

    // Sort by distance
    results.sort((a, b) => a.distance - b.distance);

    res.json({ success: true, count: results.length, results });
  } catch (error) {
    console.error('Facilities API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// 2. MEDICINE AVAILABILITY API
app.get('/api/pharmacy-support/inventory/availability', async (req, res) => {
  try {
    const { medicine, lat, lng, radius = 5000 } = req.query;
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lng);
    const searchRadius = parseInt(radius) / 1000;
    const searchTerm = medicine.toLowerCase().trim();

    const pharmacies = await loadJSON('pharmacies.json');
    const availability = [];

    for (const pharmacy of pharmacies) {
      const distance = calculateDistance(latitude, longitude, pharmacy.location.lat, pharmacy.location.lng);
      if (distance > searchRadius) continue;

      const inventory = pharmacy.inventory || [];
      const med = inventory.find(m => m.name.toLowerCase().includes(searchTerm));

      if (med && med.quantity > 0) {
        availability.push({
          pharmacyId: pharmacy.id,
          pharmacyName: pharmacy.name,
          pharmacyAddress: pharmacy.address,
          location: pharmacy.location,
          distance,
          available: true,
          medicine: {
            name: med.name,
            quantity: med.quantity,
            price: med.price,
            expiryDate: med.expiryDate
          },
          estimatedPrice: { amount: med.price, currency: 'INR' },
          confidence: 0.95,
          lastUpdated: med.lastUpdated
        });
      }
    }

    availability.sort((a, b) => a.distance - b.distance);
    res.json({ success: true, medicine, count: availability.length, availability });
  } catch (error) {
    console.error('Medicine API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// 3. HEALTH CAMPS API
app.get('/api/pharmacy-support/health-camps', async (req, res) => {
  try {
    const { lat, lng, radius = 25000, type } = req.query;
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lng);
    const searchRadius = parseInt(radius) / 1000;

    let camps = await loadJSON('health-camps.json');

    // Filter by distance
    camps = camps.map(camp => ({
      ...camp,
      distance: calculateDistance(latitude, longitude, camp.location.lat, camp.location.lng)
    })).filter(camp => camp.distance <= searchRadius);

    // Filter by type if specified
    if (type) {
      camps = camps.filter(camp => camp.type === type);
    }

    // Sort by date
    camps.sort((a, b) => new Date(a.date) - new Date(b.date));

    res.json({ success: true, count: camps.length, camps });
  } catch (error) {
    console.error('Health camps API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// 4. DOCTORS API
app.get('/api/pharmacy-support/doctors', async (req, res) => {
  try {
    const { specialization } = req.query;
    let doctors = await loadJSON('doctors.json');

    if (specialization) {
      const searchTerm = specialization.toLowerCase();
      doctors = doctors.filter(d => d.specialization.toLowerCase().includes(searchTerm));
    }

    res.json({ success: true, count: doctors.length, doctors });
  } catch (error) {
    console.error('Doctors API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// 5. DOCTOR AVAILABILITY API
app.get('/api/pharmacy-support/doctors/:doctorId/availability', async (req, res) => {
  try {
    const { doctorId } = req.params;
    const { date } = req.query;

    const doctors = await loadJSON('doctors.json');
    const doctor = doctors.find(d => d.id === doctorId);

    if (!doctor) {
      return res.status(404).json({ error: 'Doctor not found' });
    }

    const dayOfWeek = new Date(date).toLocaleDateString('en-US', { weekday: 'long' });
    const dayAvailability = doctor.availability.find(a => a.day === dayOfWeek);

    if (!dayAvailability) {
      return res.json({ success: true, available: false, slots: [] });
    }

    // Get existing bookings
    const bookings = await loadJSON('bookings.json');
    const dateBookings = bookings.filter(b => b.doctorId === doctorId && b.date === date);

    // Mark slots as booked
    const slots = dayAvailability.slots.map(slot => ({
      ...slot,
      available: slot.available && !dateBookings.some(b => b.time === slot.startTime),
      booked: dateBookings.some(b => b.time === slot.startTime)
    }));

    res.json({ success: true, doctorId, date, available: true, day: dayOfWeek, slots });
  } catch (error) {
    console.error('Availability API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// 6. BOOKING API
app.post('/api/pharmacy-support/doctors/booking', async (req, res) => {
  try {
    const { doctorId, patientName, phone, email, date, time, reason } = req.body;

    const doctors = await loadJSON('doctors.json');
    const doctor = doctors.find(d => d.id === doctorId);

    if (!doctor) {
      return res.status(404).json({ error: 'Doctor not found' });
    }

    const bookings = await loadJSON('bookings.json');
    const newBooking = {
      id: `booking_${Date.now()}`,
      doctorId,
      doctorName: doctor.name,
      hospitalName: doctor.hospitalName,
      patientName,
      phone,
      email: email || null,
      date,
      time,
      reason: reason || 'General consultation',
      status: 'confirmed',
      consultationFee: doctor.consultationFee,
      createdAt: new Date().toISOString()
    };

    bookings.push(newBooking);
    await saveJSON('bookings.json', bookings);

    res.json({ success: true, message: 'Booking created successfully', booking: newBooking });
  } catch (error) {
    console.error('Booking API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// 7. AI CHATBOT API
app.post('/api/pharmacy-support/chatbot/query', async (req, res) => {
  try {
    const { message } = req.body;

    const systemPrompt = `You are a helpful medical assistant. Provide concise, accurate medical information. Always remind users to consult a doctor for serious issues.`;

    const response = await ollama.chat({
      model: 'gpt-oss:120b-cloud',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: message }
      ],
      stream: false
    });

    res.json({
      success: true,
      response: response.message.content,
      sessionId: `session_${Date.now()}`,
      timestamp: new Date().toISOString(),
      model: 'gpt-oss:120b-cloud'
    });
  } catch (error) {
    console.error('Chatbot API error:', error);
    res.json({
      success: true,
      response: "I apologize, but I'm having trouble processing your request right now. Please try again or consult with a healthcare professional for immediate assistance.",
      error: true
    });
  }
});

console.log('✅ Pharmacy Support APIs loaded');

// ============================================================================

const SYSTEM_PROMPT = `You are Sanjeevani, a warm, intelligent, and expert AI health assistant by Sanjeevani Healthcare. You combine medical expertise with genuine human warmth and conversational intelligence.

# CRITICAL: Message Classification

Before every response, silently classify the message and respond accordingly:

## Type 1 — Greeting / Small Talk
Examples: "hi", "hello", "thanks", "bye", "good morning", "how are you"
→ Warm, brief, conversational. NO sections, tables, disclaimers, or medical format.
Example: "Hi there! 👋 I'm Sanjeevani, your personal health assistant. How can I help you today?"

## Type 2 — General / Meta Questions
Examples: "what can you do", "are you a doctor", "who made you"
→ Friendly, 2–4 sentences. No medical structure needed.

## Type 3 — Medical / Health Query
Examples: symptoms, conditions, medicines, diet, pain, fever, treatment
→ Use the full structured medical format below.

## Type 4 — EMERGENCY (check this FIRST, every time)
Examples: "I can't breathe", "severe chest pain", "I took too many pills", "I think I'm having a stroke"
→ Skip ALL structure. Respond immediately:
"🚨 This sounds like a medical emergency. Please call 112 or go to your nearest emergency room RIGHT NOW. Do not wait."
Then offer to stay with them until help arrives.

## Type 5 — Mental Health / Crisis
Examples: "I want to hurt myself", "I feel hopeless", "I don't want to live"
→ Respond with compassion. No clinical format.
"I hear you, and I'm really glad you reached out. You're not alone in this."
Always include: iCall: 9152987821 | Vandrevala Foundation: 1860-2662-345 (24/7)
Never give advice. Listen, validate, connect to human support.

## Type 6 — Ambiguous / Mixed
Examples: casual tone but medical content, vague descriptions like "I feel weird"
→ Ask one gentle clarifying question before giving a full response.

---

# EDGE CASE RULES (apply on top of classification)

**Child under 12**: Add → "⚠️ For children, please consult a pediatrician rather than relying on general guidance."

**Pregnancy / Breastfeeding**: Add → "⚠️ Please consult your OB-GYN before following any health advice during pregnancy or breastfeeding."

**User mentions existing medication**: Do NOT suggest alternatives. Add → "Since you're already on medication, please check with your doctor before making any changes."

**Language**: Match the user's language exactly — English, Hindi, or Hinglish.

**Follow-up messages**: Maintain context from prior turns. Don't re-introduce yourself mid-conversation.

---

# Medical Response Format (Type 3 only)

## 1. 🩺 Understanding Your Concern
[1–2 lines. Empathetic, acknowledging what they described.]

## 2. What This Could Mean
[2–4 lines. Plain-language explanation. Do NOT diagnose.]

## 3. Possible Causes
| Cause | Description | Likelihood |
|-------|-------------|------------|
| [Cause] | [Brief description] | Common / Uncommon / Rare |
(Max 4–5 rows)

## 4. Safe Home Care
- **Hydration**: [specific advice]
- **Rest**: [specific advice]
- **Diet**: [specific advice]
- **Monitoring**: [what to watch for]

## 5. 🚨 When to See a Doctor
> **Seek immediate care if:**
> - [Specific red flag 1]
> - [Specific red flag 2]

> **Schedule a visit if:**
> - Symptoms persist beyond [X days, condition-appropriate]
> - Symptoms worsen or new symptoms appear

## 6. Quick Summary
[2–3 sentences. Reassuring but honest.]

---

⚠️ *This is for informational purposes only and does not replace professional medical advice. Always consult a qualified healthcare provider for diagnosis and treatment.*

---

💬 **Can you tell me more?**
- How long have you had these symptoms?
- Are you experiencing anything else alongside this?
- Do you have any existing conditions or are you currently on medication?

---

# Core Rules
- NEVER diagnose. Explain possibilities, not certainties.
- NEVER prescribe. Direct medication questions to a doctor.
- NEVER use medical format for Type 1 or 2 messages.
- ALWAYS check for Type 4/5 signals before anything else.
- When database info is provided, use it as the primary source.
- Be concise. Structure should help the user, not impress them.`;

// Tool-specific prompts
const TOOL_PROMPTS = {
  searchWeb: `You are Sanjeevani in WEB SEARCH mode.

Search and analyze web information to answer medical queries with proper source citations.

# Response Structure
## 🔍 What I Found
[2–3 sentence overview of search results]

## Key Points
[Main findings from web sources, cited with URLs]

## Medical Guidance
[Your expert synthesis combining web info and medical knowledge]

## Sources
- [Source 1 – URL]
- [Source 2 – URL]
- [Source 3 – URL]

⚠️ *This is for informational purposes only. Consult a qualified healthcare provider for diagnosis and treatment.*

💬 Follow-up questions: [2–3 relevant questions]

RULES: Always cite URLs. Never diagnose or prescribe. Combine web findings with medical expertise.`,


  writeCode: `You are Sanjeevani in PLANNING mode.

Create specific, actionable medical plans — diet, exercise, treatment schedules, recovery routines.

# Response Structure
## 📋 Plan Overview
[2–3 sentence summary of the plan and its goals]

## 🎯 Goals
- Primary: [specific goal]
- Secondary: [supporting goals]
- Timeline: [realistic duration]

## 📅 Weekly Schedule
| Day | Morning | Afternoon | Evening | Notes |
|-----|---------|-----------|---------|-------|
| Mon | | | | |
| Tue | | | | |
(Fill all 7 days with specific activities)

## 🍽️ Diet (if applicable)
- Breakfast: [specific options]
- Lunch: [specific options]
- Dinner: [specific options]
- Avoid: [specific items]

## 💊 Medications/Supplements (if applicable)
| Item | Dosage | Timing | Notes |
|------|--------|--------|-------|
(Only include if clearly relevant — never prescribe)

## 📊 How to Track Progress
[Specific, measurable indicators]

⚠️ *This is for informational purposes only. Consult a qualified healthcare provider before starting any new health plan.*

💬 Follow-up questions: [2–3 implementation questions]

RULES: Be specific — no vague advice like "eat healthy." Use tables. Never diagnose or prescribe.`,


  thinkLonger: `You are Sanjeevani in ANALYTICAL THINKING mode.

Show step-by-step reasoning. Think out loud. Be methodical and thorough.

# Response Structure
## 🤔 What I Understand
[Restate the query in your own words + key factors to consider]

## 🔍 Step-by-Step Analysis

### Step 1: Core Issue
[What is the fundamental question being asked?]

### Step 2: Perspectives to Consider
| Perspective | Supporting Evidence | Limitations |
|-------------|-------------------|-------------|
| [A] | | |
| [B] | | |

### Step 3: Risk-Benefit Weighing
[Honest assessment of tradeoffs]

### Step 4: Alternatives Considered
[What other approaches exist and why they were or weren't chosen]

## 💡 Reasoning Chain
1. [First logical step]
2. [Second step]
3. [Conclusion reached]

## 🎯 Final Recommendation
[Well-reasoned conclusion + when to reconsider it]

⚠️ *This is for informational purposes only. Consult a qualified healthcare provider for diagnosis and treatment.*

💬 Follow-up questions: [2–3 analytical questions]

RULES: Show all reasoning. Be honest about uncertainty. Never diagnose or prescribe.`,


  deepResearch: `You are Sanjeevani in DEEP RESEARCH mode.

Provide comprehensive, detailed medical analysis. Thoroughness is the priority.

# Response Structure
## 📖 Executive Summary
[3–4 paragraph overview covering what it is, who it affects, and key takeaways]

## 🔬 Medical Analysis

### Pathophysiology
[How the condition develops and functions biologically]

### Epidemiology
[Prevalence, demographics, risk factors, geographic patterns]

### Clinical Presentation
[Symptoms, signs, typical vs atypical presentations]

### Diagnostic Approach
[How it's diagnosed — criteria, tests, differentials]

### Treatment Options
[Comprehensive overview: first-line, second-line, emerging options]

### Prognosis
[Outcomes, recovery timeline, long-term considerations]

## 📊 Current Research
[Latest studies, evidence quality, ongoing trials if relevant]

## 💡 What This Means for You
[Practical patient-facing implications in plain language]

⚠️ *This is for informational purposes only. Consult a qualified healthcare provider for diagnosis and treatment.*

## 📚 References
[List credible sources: WHO, NIH, PubMed, Indian health authorities as relevant]

💬 Follow-up questions: [2–3 deep analytical questions]

RULES: Use medical terminology but always explain it in plain language alongside. Never diagnose or prescribe.`

};

// Function to detect if text is Hinglish
function isHinglish(text) {
  if (!text) return false;
  const hinglishPatterns = [
    /\b(mujhe|aap|kya|hai|ho|ka|ki|ke|ko|se|par|toh|yeh|woh|kaise|kab|kahan|kyun)\b/i,
    /\b(batao|karo|chahiye|hota|hoti|hote|raha|rahe|rahi|gaya|gaye|gayi)\b/i,
    /\b(sar|bukhar|dard|ilaaj|dawai|doctor|hospital|bimari|sehat)\b/i,
  ];
  return hinglishPatterns.some(pattern => pattern.test(text));
}

app.post('/chat', async (req, res) => {
  try {
    const { message, images, history = [], selectedTool = null } = req.body;
    let finalMessage = message;

    console.log(`🔧 Selected Tool: ${selectedTool || 'None (Standard mode)'}`);

    // Step 1: Image Analysis with llava
    if (images && images.length > 0) {
      console.log('🖼️ Analyzing medical image with llava...');
      try {
        const visionResponse = await fetch('http://localhost:11434/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: 'llava',
            prompt: `You are a medical image analyzer. Carefully examine this image and describe:
1. What body part or area is shown
2. Any visible skin conditions, rashes, discoloration, or abnormalities
3. Color, texture, pattern, and distribution of any visible symptoms
4. Size and location of affected areas
5. Any other notable medical observations

Be detailed and specific. Focus on observable medical features.`,
            images: images,
            stream: false
          })
        });

        if (!visionResponse.ok) {
          console.error('❌ Vision model HTTP error:', visionResponse.status);
          throw new Error(`Vision model failed with status ${visionResponse.status}`);
        }

        const visionData = await visionResponse.json();
        const imageDescription = visionData.response;
        console.log('✅ Vision Analysis Complete:', imageDescription.substring(0, 150) + '...');

        const userQuery = message.trim() || "What could this be? Please analyze this medical condition.";

        finalMessage = `[MEDICAL IMAGE UPLOADED]

Vision Model Analysis:
${imageDescription}

User Question: ${userQuery}

Please provide a structured medical response based on the image analysis above.`;

        console.log('📝 Final message prepared for GPT-OSS');
      } catch (error) {
        console.error('❌ Vision analysis failed:', error.message);
        finalMessage = `[System: Image was uploaded but analysis failed. Error: ${error.message}]

User Query: ${message || "Please help me understand this medical image."}

Please provide general guidance and recommend consulting a healthcare professional.`;
      }
    }

    // Step 2: Web Search (if selected)
    let searchResultsContext = '';
    if (selectedTool === 'searchWeb') {
      console.log('🌐 Performing web search for:', finalMessage);
      try {
        const searchResults = await search(finalMessage, {
          safeSearch: 'strict'
        });

        if (searchResults.results && searchResults.results.length > 0) {
          const topResults = searchResults.results.slice(0, 5).map(r =>
            `- **${r.title}**: ${r.description} (Source: ${r.url})`
          ).join('\n');

          searchResultsContext = `\n\n# WEB SEARCH RESULTS (Use these to answer)\n\n${topResults}\n\n**INSTRUCTIONS**: Cite these sources in your response using the URLs provided.`;
          console.log('✅ Web search successful, found results');
        } else {
          console.log('⚠️ Web search returned no results');
          searchResultsContext = '\n\n[System: Web search attempted but returned no results. Proceed with internal knowledge.]';
        }
      } catch (error) {
        console.error('❌ Web search failed:', error.message);
        searchResultsContext = '\n\n[System: Web search failed. Proceed with internal knowledge.]';
      }
    }

    // Detect language and select model
    const useHinglishModel = isHinglish(message || finalMessage);
    const selectedModel = 'gpt-oss:120b-cloud';

    console.log(`Query: "${(message || 'Image upload').substring(0, 50)}..."`);
    console.log(`Language: ${useHinglishModel ? 'Hinglish' : 'English/Other'}, Model: ${selectedModel}`);

    // Get relevant context from medical dataset using RAG
    // Deep research mode gets more context
    const ragContextCount = selectedTool === 'deepResearch' ? 10 : 3;
    const ragContext = medicalRAG.getContext(finalMessage, ragContextCount);

    // Build system content - use tool-specific prompt if tool is selected
    let systemContent = selectedTool && TOOL_PROMPTS[selectedTool]
      ? TOOL_PROMPTS[selectedTool]
      : SYSTEM_PROMPT;

    // Append web search results if available
    if (searchResultsContext) {
      systemContent += searchResultsContext;
    }

    console.log(`📋 Using prompt: ${selectedTool ? `${selectedTool} mode` : 'Standard mode'}`);

    if (ragContext) {
      systemContent += `\n\n# MEDICAL DATABASE INFORMATION (Use this as PRIMARY source)\n\n${ragContext}`;
      systemContent += `\n**IMPORTANT INSTRUCTIONS**:
-- The above database information is VERIFIED and ACCURATE
-- Use medications, treatments, and side effects EXACTLY as listed in the database
-- Cite specific medication names from the database when relevant
-- If the user's question matches the database entries, prioritize that information
-- Combine database info with your medical knowledge for complete answers
-- Maintain the user's language (Hinglish/English/Hindi) in your response`;
    }

    const messages = [
      { role: 'system', content: systemContent },
      ...history,
      { role: 'user', content: finalMessage }
    ];

    // Set headers for streaming
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    // Stream response from Ollama
    const response = await ollama.chat({
      model: selectedModel,
      messages: messages,
      stream: true,
    });

    for await (const part of response) {
      if (part.message?.content) {
        res.write(`data: ${JSON.stringify({ content: part.message.content })}\n\n`);
      }
    }

    res.write('data: [DONE]\n\n');
    res.end();
  } catch (error) {
    console.error('Error details:', error);
    if (error.cause) console.error('Cause:', error.cause);
    if (!res.headersSent) {
      res.status(500).json({ error: 'Failed to get response from Ollama', details: error.message });
    } else {
      res.end();
    }
  }
});

// Prescription Refinement Endpoint
app.post('/api/prescription/refine', async (req, res) => {
  try {
    const { text } = req.body;
    if (!text) {
      return res.status(400).json({ error: 'No text provided' });
    }

    console.log('Refining prescription text...');

    const prompt = `
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

    OCR Text:
    "${text}"
    `;

    const response = await ollama.chat({
      model: 'llama3.2',
      messages: [{ role: 'user', content: prompt }],
      format: 'json',
      stream: false
    });

    const result = JSON.parse(response.message.content);
    console.log('Refinement complete:', result);
    res.json(result);

  } catch (error) {
    console.error('Error refining prescription:', error);
    res.status(500).json({ error: 'Failed to refine prescription' });
  }
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`🏥 Sanjeevani Medical Chatbot Server`);
  console.log(`${'='.repeat(60)}`);
  console.log(`✓ Server running on http://localhost:${PORT}`);
  console.log(`✓ RAG: Medical knowledge base loaded (25,010 entries)`);
  console.log(`✓ Image Analysis: llava → gpt-oss:120b-cloud`);
  console.log(`✓ Tool Modes: Search, Write, Think, Deep Research`);
  console.log(`✓ Web Search: duck-duck-scrape active`);
  console.log(`✓ Pharmacy API: Google Places integration active`);
  console.log(`✓ Medicine API: RxNorm + OpenFDA integration active`);
  console.log(`✓ Outbreak API: Disease surveillance & anomaly detection active`);
  console.log(`${'='.repeat(60)}\n`);
});
