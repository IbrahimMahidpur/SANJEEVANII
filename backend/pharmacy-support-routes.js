// ============================================================================
// PHARMACY SUPPORT - REAL-TIME API ROUTES
// Using free APIs: Overpass, CoWIN, RxNorm, OpenFDA
// ============================================================================

import express from 'express';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import realtimeAPIs from './realtime-apis.js';

const router = express.Router();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PHARMACY_DATA_PATH = path.join(__dirname, 'pharmacy-support', 'data');

// Helper: Load JSON file
async function loadJSON(filename) {
  try {
    const data = await fs.readFile(path.join(PHARMACY_DATA_PATH, filename), 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return [];
  }
}

// Helper: Save JSON file
async function saveJSON(filename, data) {
  await fs.writeFile(path.join(PHARMACY_DATA_PATH, filename), JSON.stringify(data, null, 2));
}

// ============================================================================
// 1. NEARBY FACILITIES - REAL-TIME (Overpass API)
// ============================================================================

router.get('/facilities/nearby', async (req, res) => {
  try {
    const { lat, lng, radius = 5000, type = 'all' } = req.query;
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lng);
    const searchRadius = parseInt(radius);

    console.log(`🔍 [REAL-TIME] Searching ${type} facilities within ${searchRadius}m`);

    try {
      // Fetch REAL-TIME data from OpenStreetMap via Overpass API
      const results = await realtimeAPIs.getOverpassFacilities(latitude, longitude, searchRadius, type);

      res.json({
        success: true,
        count: results.length,
        results,
        source: 'overpass_api',
        realTime: true,
        timestamp: new Date().toISOString()
      });
    } catch (overpassError) {
      console.warn('⚠️ Overpass API unavailable, using local fallback');

      // Fallback to local data
      const pharmacies = await loadJSON('pharmacies.json');
      const results = pharmacies.map(p => ({
        ...p,
        distance: realtimeAPIs.calculateDistance(latitude, longitude, p.location.lat, p.location.lng)
      })).filter(p => p.distance <= searchRadius / 1000);

      results.sort((a, b) => a.distance - b.distance);

      res.json({
        success: true,
        count: results.length,
        results,
        source: 'local_cache',
        realTime: false
      });
    }
  } catch (error) {
    console.error('❌ Facilities API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// 2. MEDICINE AVAILABILITY - ENHANCED WITH REAL-TIME INFO
// ============================================================================

router.get('/inventory/availability', async (req, res) => {
  try {
    const { medicine, lat, lng, radius = 5000 } = req.query;
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lng);
    const searchRadius = parseInt(radius) / 1000;
    const searchTerm = medicine.toLowerCase().trim();

    console.log(`🔍 [REAL-TIME] Searching medicine: ${medicine}`);

    // Get medicine info from RxNorm (real-time)
    const medicineInfo = await realtimeAPIs.getRxNormMedicineInfo(medicine);
    const drugSafety = await realtimeAPIs.getOpenFDADrugInfo(medicine);

    // Search local pharmacy inventory
    const pharmacies = await loadJSON('pharmacies.json');
    const availability = [];

    for (const pharmacy of pharmacies) {
      const distance = realtimeAPIs.calculateDistance(latitude, longitude, pharmacy.location.lat, pharmacy.location.lng);
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

    res.json({
      success: true,
      medicine,
      count: availability.length,
      availability,
      medicineInfo: medicineInfo ? {
        name: medicineInfo.name,
        rxcui: medicineInfo.rxcui,
        source: 'rxnorm',
        realTime: true
      } : null,
      safetyInfo: drugSafety ? {
        brandName: drugSafety.brandName,
        genericName: drugSafety.genericName,
        manufacturer: drugSafety.manufacturer,
        warnings: drugSafety.warnings?.substring(0, 200) + '...',
        source: 'openfda',
        realTime: true
      } : null,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('❌ Medicine API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// 3. HEALTH CAMPS - REAL-TIME (CoWIN API)
// ============================================================================

router.get('/health-camps', async (req, res) => {
  try {
    const { lat, lng, radius = 25000, type } = req.query;
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lng);
    const searchRadius = parseInt(radius) / 1000;

    console.log(`🔍 [REAL-TIME] Fetching health camps from CoWIN...`);

    let camps = [];

    try {
      // Fetch REAL-TIME vaccination data from CoWIN
      // District ID for Indore: 425 (you can make this dynamic based on lat/lng)
      const today = new Date();
      const dateStr = `${String(today.getDate()).padStart(2, '0')}-${String(today.getMonth() + 1).padStart(2, '0')}-${today.getFullYear()}`;

      const cowinCenters = await realtimeAPIs.getCowinVaccinationCenters(425, dateStr);
      camps = cowinCenters;

      console.log(`✅ Found ${cowinCenters.length} REAL vaccination centers from CoWIN`);
    } catch (cowinError) {
      console.warn('⚠️ CoWIN API unavailable, using local data');
    }

    // Add local health camps
    const localCamps = await loadJSON('health-camps.json');
    camps = [...camps, ...localCamps];

    // Filter by distance
    camps = camps.map(camp => ({
      ...camp,
      distance: realtimeAPIs.calculateDistance(latitude, longitude, camp.location.lat, camp.location.lng)
    })).filter(camp => camp.distance <= searchRadius);

    // Filter by type if specified
    if (type) {
      camps = camps.filter(camp => camp.type === type);
    }

    // Sort by date
    camps.sort((a, b) => new Date(a.date) - new Date(b.date));

    res.json({
      success: true,
      count: camps.length,
      camps,
      sources: ['cowin_api', 'local_database'],
      realTime: true,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('❌ Health camps API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// 4. DOCTORS API (Local Database)
// ============================================================================

router.get('/doctors', async (req, res) => {
  try {
    const { specialization } = req.query;
    let doctors = await loadJSON('doctors.json');

    if (specialization) {
      const searchTerm = specialization.toLowerCase();
      doctors = doctors.filter(d => d.specialization.toLowerCase().includes(searchTerm));
    }

    res.json({ success: true, count: doctors.length, doctors });
  } catch (error) {
    console.error('❌ Doctors API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// 5. DOCTOR AVAILABILITY API
// ============================================================================

router.get('/doctors/:doctorId/availability', async (req, res) => {
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

    const bookings = await loadJSON('bookings.json');
    const dateBookings = bookings.filter(b => b.doctorId === doctorId && b.date === date);

    const slots = dayAvailability.slots.map(slot => ({
      ...slot,
      available: slot.available && !dateBookings.some(b => b.time === slot.startTime),
      booked: dateBookings.some(b => b.time === slot.startTime)
    }));

    res.json({ success: true, doctorId, date, available: true, day: dayOfWeek, slots });
  } catch (error) {
    console.error('❌ Availability API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// 6. BOOKING API
// ============================================================================

router.post('/doctors/booking', async (req, res) => {
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
    console.error('❌ Booking API error:', error);
    res.status(500).json({ error: error.message });
  }
});

// ============================================================================
// 7. AI CHATBOT API (GPT-OSS 120B)
// ============================================================================

router.post('/chatbot/query', async (req, res) => {
  try {
    const { message } = req.body;

    const systemPrompt = `You are a helpful medical assistant. Provide concise, accurate medical information. Always remind users to consult a doctor for serious issues.`;

    // This will be handled by the main server's ollama instance
    res.json({
      success: true,
      response: "AI chatbot response will be integrated with the main Ollama instance.",
      note: "Please use the main chatbot endpoint for AI assistance"
    });
  } catch (error) {
    console.error('❌ Chatbot API error:', error);
    res.json({
      success: true,
      response: "I apologize, but I'm having trouble processing your request right now. Please try again or consult with a healthcare professional for immediate assistance.",
      error: true
    });
  }
});

console.log('✅ Pharmacy Support Real-Time APIs loaded');

export default router;
