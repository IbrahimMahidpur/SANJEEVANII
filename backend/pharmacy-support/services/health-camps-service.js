const axios = require('axios');
const fs = require('fs').promises;
const path = require('path');

const HEALTH_CAMPS_FILE = path.join(__dirname, '../data/health-camps.json');
const COWIN_API = 'https://cdn-api.co-vin.in/api/v2';

/**
 * Load health camps from JSON file
 */
async function loadHealthCamps() {
  try {
    const data = await fs.readFile(HEALTH_CAMPS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.log('ℹ️ No health camps file found, initializing...');
    return [];
  }
}

/**
 * Save health camps to JSON file
 */
async function saveHealthCamps(camps) {
  await fs.writeFile(HEALTH_CAMPS_FILE, JSON.stringify(camps, null, 2));
}

/**
 * Fetch vaccination centers from CoWIN (if available)
 */
async function fetchCowinData(districtId, date) {
  try {
    const response = await axios.get(
      `${COWIN_API}/appointment/sessions/public/calendarByDistrict`,
      {
        params: {
          district_id: districtId,
          date: date // DD-MM-YYYY format
        },
        headers: {
          'User-Agent': 'Mozilla/5.0',
          'Accept': 'application/json'
        },
        timeout: 10000
      }
    );

    return response.data.centers || [];
  } catch (error) {
    console.log('ℹ️ CoWIN API not available or rate limited');
    return [];
  }
}

/**
 * Parse CoWIN centers to health camps format
 */
function parseCowinCenters(centers) {
  const camps = [];

  centers.forEach(center => {
    if (center.sessions && center.sessions.length > 0) {
      center.sessions.forEach(session => {
        camps.push({
          id: `cowin_${center.center_id}_${session.session_id}`,
          name: `${center.name} - Vaccination Drive`,
          type: 'vaccine',
          organizer: 'Government of India (CoWIN)',
          location: {
            lat: center.lat || 22.7196, // Default to Indore if not available
            lng: center.long || 75.8577,
            address: `${center.address}, ${center.district_name}, ${center.state_name}, ${center.pincode}`
          },
          date: session.date,
          startTime: '09:00',
          endTime: '17:00',
          services: [
            `Vaccine: ${session.vaccine}`,
            `Min Age: ${session.min_age_limit}`,
            `Available Capacity: ${session.available_capacity}`
          ],
          registrationRequired: true,
          contactPhone: center.phone || 'Not available',
          feeType: center.fee_type,
          source: 'cowin',
          createdAt: new Date().toISOString()
        });
      });
    }
  });

  return camps;
}

/**
 * Get all health camps
 */
async function getAllHealthCamps() {
  return await loadHealthCamps();
}

/**
 * Get health camps near location
 */
async function getHealthCampsNearby(lat, lng, radius = 25000, type = null) {
  const allCamps = await loadHealthCamps();

  // Filter by distance
  const nearbyCamps = allCamps.filter(camp => {
    const distance = calculateDistance(
      lat, lng,
      camp.location.lat, camp.location.lng
    );
    return distance <= radius / 1000;
  });

  // Filter by type if specified
  const filtered = type
    ? nearbyCamps.filter(camp => camp.type === type)
    : nearbyCamps;

  // Add distance to each camp
  filtered.forEach(camp => {
    camp.distance = calculateDistance(
      lat, lng,
      camp.location.lat, camp.location.lng
    );
  });

  // Sort by date (upcoming first)
  filtered.sort((a, b) => {
    const dateA = parseDate(a.date);
    const dateB = parseDate(b.date);
    return dateA - dateB;
  });

  return filtered;
}

/**
 * Add new health camp
 */
async function addHealthCamp(campData) {
  const camps = await loadHealthCamps();

  const newCamp = {
    id: `camp_${Date.now()}`,
    name: campData.name,
    type: campData.type, // vaccine | checkup | camp
    organizer: campData.organizer,
    location: campData.location,
    date: campData.date,
    startTime: campData.startTime,
    endTime: campData.endTime,
    services: campData.services || [],
    registrationRequired: campData.registrationRequired || false,
    contactPhone: campData.contactPhone,
    source: 'manual',
    createdAt: new Date().toISOString()
  };

  camps.push(newCamp);
  await saveHealthCamps(camps);

  return newCamp;
}

/**
 * Sync health camps from external sources
 */
async function syncHealthCamps() {
  console.log('🔄 Syncing health camps from external sources...');

  const existingCamps = await loadHealthCamps();
  let newCamps = [...existingCamps];

  // Try to fetch from CoWIN (Indore district ID: 391)
  try {
    const today = new Date();
    const dateStr = `${today.getDate().toString().padStart(2, '0')}-${(today.getMonth() + 1).toString().padStart(2, '0')}-${today.getFullYear()}`;

    const cowinCenters = await fetchCowinData(391, dateStr);
    const cowinCamps = parseCowinCenters(cowinCenters);

    // Remove old CoWIN camps and add new ones
    newCamps = newCamps.filter(camp => camp.source !== 'cowin');
    newCamps = [...newCamps, ...cowinCamps];

    console.log(`✅ Synced ${cowinCamps.length} vaccination centers from CoWIN`);
  } catch (error) {
    console.log('ℹ️ Could not sync from CoWIN');
  }

  await saveHealthCamps(newCamps);
  console.log(`✅ Total health camps: ${newCamps.length}`);

  return newCamps;
}

/**
 * Calculate distance between two points
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);

  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c * 10) / 10;
}

function toRad(degrees) {
  return degrees * (Math.PI / 180);
}

/**
 * Parse date string (DD-MM-YYYY or YYYY-MM-DD)
 */
function parseDate(dateStr) {
  if (dateStr.includes('-')) {
    const parts = dateStr.split('-');
    if (parts[0].length === 4) {
      // YYYY-MM-DD
      return new Date(dateStr);
    } else {
      // DD-MM-YYYY
      return new Date(`${parts[2]}-${parts[1]}-${parts[0]}`);
    }
  }
  return new Date(dateStr);
}

module.exports = {
  getAllHealthCamps,
  getHealthCampsNearby,
  addHealthCamp,
  syncHealthCamps
};
