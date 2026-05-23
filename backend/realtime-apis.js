// ============================================================================
// REAL-TIME FREE API INTEGRATIONS
// Using: Overpass API, CoWIN, OpenFDA, RxNorm
// ============================================================================

import axios from 'axios';

// Cache for API responses (in-memory, 1 hour TTL)
const apiCache = new Map();
const CACHE_TTL = 3600000; // 1 hour

function getCached(key) {
  const cached = apiCache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  return null;
}

function setCache(key, data) {
  apiCache.set(key, { data, timestamp: Date.now() });
}

// Helper: Calculate distance between two coordinates
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c * 10) / 10;
}

// ============================================================================
// 1. OVERPASS API - Real-time Pharmacy/Hospital Data from OpenStreetMap
// ============================================================================

export async function getOverpassFacilities(lat, lng, radius, type = 'all') {
  const cacheKey = `overpass_${lat}_${lng}_${radius}_${type}`;
  const cached = getCached(cacheKey);
  if (cached) {
    console.log('✅ Using cached Overpass data');
    return cached;
  }

  let amenityTypes = [];
  if (type === 'all' || type === 'pharmacy') amenityTypes.push('pharmacy');
  if (type === 'all' || type === 'hospital') amenityTypes.push('hospital', 'clinic');
  if (type === 'all' || type === 'doctor') amenityTypes.push('doctors', 'clinic');

  const overpassQuery = `
    [out:json][timeout:25];
    (
      ${amenityTypes.map(t => `
        node["amenity"="${t}"](around:${radius},${lat},${lng});
        way["amenity"="${t}"](around:${radius},${lat},${lng});
      `).join('')}
    );
    out body;
    >;
    out skel qt;
  `;

  try {
    console.log(`🔍 Fetching REAL-TIME data from Overpass API (OpenStreetMap)...`);

    const response = await axios.post(
      'https://overpass-api.de/api/interpreter',
      overpassQuery,
      {
        headers: { 'Content-Type': 'text/plain' },
        timeout: 30000
      }
    );

    const elements = response.data.elements || [];
    const results = [];

    for (const element of elements) {
      if (element.type !== 'node' && element.type !== 'way') continue;
      if (!element.tags) continue;

      const elementLat = element.lat || (element.center?.lat);
      const elementLon = element.lon || (element.center?.lon);
      if (!elementLat || !elementLon) continue;

      const distance = calculateDistance(lat, lng, elementLat, elementLon);

      results.push({
        id: `osm_${element.id}`,
        name: element.tags.name || element.tags['name:en'] || `${element.tags.amenity} (Unnamed)`,
        address: [
          element.tags['addr:street'],
          element.tags['addr:housenumber'],
          element.tags['addr:city'] || 'Indore',
          element.tags['addr:postcode']
        ].filter(Boolean).join(', ') || 'Address not available',
        location: { lat: elementLat, lng: elementLon },
        facilityType: element.tags.amenity,
        types: [element.tags.amenity],
        phone: element.tags.phone || element.tags['contact:phone'] || null,
        website: element.tags.website || null,
        openingHours: element.tags.opening_hours || null,
        isOpen: null,
        rating: null,
        totalRatings: 0,
        distance,
        source: 'openstreetmap',
        realTime: true,
        lastUpdated: new Date().toISOString()
      });
    }

    results.sort((a, b) => a.distance - b.distance);

    setCache(cacheKey, results);
    console.log(`✅ Found ${results.length} REAL facilities from OpenStreetMap`);

    return results;
  } catch (error) {
    console.error('❌ Overpass API error:', error.message);
    throw error;
  }
}

// ============================================================================
// 2. COWIN API - Real-time Vaccination Centers
// ============================================================================

export async function getCowinVaccinationCenters(districtId, date) {
  const cacheKey = `cowin_${districtId}_${date}`;
  const cached = getCached(cacheKey);
  if (cached) {
    console.log('✅ Using cached CoWIN data');
    return cached;
  }

  try {
    console.log(`🔍 Fetching REAL-TIME vaccination data from CoWIN API...`);

    const response = await axios.get(
      `https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict`,
      {
        params: {
          district_id: districtId,
          date: date // DD-MM-YYYY format
        },
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        },
        timeout: 15000
      }
    );

    const centers = response.data.centers || [];
    const results = centers.map(center => ({
      id: `cowin_${center.center_id}`,
      name: center.name,
      type: 'vaccine',
      organizer: 'Government of India - CoWIN',
      location: {
        lat: center.lat || 22.7196, // Default to Indore if not available
        lng: center.long || 75.8577,
        address: `${center.address}, ${center.block_name}, ${center.district_name}, ${center.state_name} - ${center.pincode}`
      },
      date: date,
      startTime: center.from || '09:00',
      endTime: center.to || '17:00',
      services: [
        `Vaccine: ${center.vaccine || 'Multiple'}`,
        `Fee: ${center.fee_type}`,
        `Age: ${center.sessions?.[0]?.min_age_limit}+`,
        `Available: ${center.sessions?.[0]?.available_capacity || 0} doses`
      ],
      registrationRequired: true,
      contactPhone: null,
      source: 'cowin',
      realTime: true,
      availableCapacity: center.sessions?.[0]?.available_capacity || 0,
      vaccine: center.vaccine,
      feeType: center.fee_type,
      lastUpdated: new Date().toISOString()
    }));

    setCache(cacheKey, results);
    console.log(`✅ Found ${results.length} REAL vaccination centers from CoWIN`);

    return results;
  } catch (error) {
    console.error('❌ CoWIN API error:', error.message);
    throw error;
  }
}

// ============================================================================
// 3. RXNORM API - Real-time Medicine Information
// ============================================================================

export async function getRxNormMedicineInfo(medicineName) {
  const cacheKey = `rxnorm_${medicineName.toLowerCase()}`;
  const cached = getCached(cacheKey);
  if (cached) {
    console.log('✅ Using cached RxNorm data');
    return cached;
  }

  try {
    console.log(`🔍 Fetching REAL-TIME medicine data from RxNorm API...`);

    // Search for the medicine
    const searchResponse = await axios.get(
      `https://rxnav.nlm.nih.gov/REST/drugs.json`,
      {
        params: { name: medicineName },
        timeout: 10000
      }
    );

    const drugGroup = searchResponse.data.drugGroup;
    if (!drugGroup || !drugGroup.conceptGroup) {
      return null;
    }

    const concepts = drugGroup.conceptGroup
      .flatMap(group => group.conceptProperties || [])
      .filter(Boolean);

    if (concepts.length === 0) {
      return null;
    }

    const firstConcept = concepts[0];
    const rxcui = firstConcept.rxcui;

    // Get detailed information
    const detailsResponse = await axios.get(
      `https://rxnav.nlm.nih.gov/REST/rxcui/${rxcui}/allrelated.json`,
      { timeout: 10000 }
    );

    const result = {
      name: firstConcept.name,
      rxcui: rxcui,
      synonym: firstConcept.synonym,
      tty: firstConcept.tty,
      details: detailsResponse.data.allRelatedGroup,
      source: 'rxnorm',
      realTime: true,
      lastUpdated: new Date().toISOString()
    };

    setCache(cacheKey, result);
    console.log(`✅ Found REAL medicine info for: ${medicineName}`);

    return result;
  } catch (error) {
    console.error('❌ RxNorm API error:', error.message);
    return null;
  }
}

// ============================================================================
// 4. OPENFDA API - Medicine Safety Information
// ============================================================================

export async function getOpenFDADrugInfo(medicineName) {
  const cacheKey = `openfda_${medicineName.toLowerCase()}`;
  const cached = getCached(cacheKey);
  if (cached) {
    console.log('✅ Using cached OpenFDA data');
    return cached;
  }

  try {
    console.log(`🔍 Fetching REAL-TIME drug safety data from OpenFDA...`);

    const response = await axios.get(
      `https://api.fda.gov/drug/label.json`,
      {
        params: {
          search: `openfda.brand_name:"${medicineName}" OR openfda.generic_name:"${medicineName}"`,
          limit: 1
        },
        timeout: 10000
      }
    );

    if (!response.data.results || response.data.results.length === 0) {
      return null;
    }

    const drug = response.data.results[0];
    const result = {
      brandName: drug.openfda?.brand_name?.[0],
      genericName: drug.openfda?.generic_name?.[0],
      manufacturer: drug.openfda?.manufacturer_name?.[0],
      purpose: drug.purpose?.[0],
      warnings: drug.warnings?.[0],
      dosage: drug.dosage_and_administration?.[0],
      sideEffects: drug.adverse_reactions?.[0],
      source: 'openfda',
      realTime: true,
      lastUpdated: new Date().toISOString()
    };

    setCache(cacheKey, result);
    console.log(`✅ Found REAL drug safety info for: ${medicineName}`);

    return result;
  } catch (error) {
    console.error('❌ OpenFDA API error:', error.message);
    return null;
  }
}

export default {
  getOverpassFacilities,
  getCowinVaccinationCenters,
  getRxNormMedicineInfo,
  getOpenFDADrugInfo,
  calculateDistance
};
