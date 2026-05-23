const axios = require('axios');
const cacheService = require('./cache-service');

const OVERPASS_API = 'https://overpass-api.de/api/interpreter';

/**
 * Query Overpass API for nearby facilities
 */
async function queryOverpass(lat, lng, radius, amenityType) {
  const cacheKey = cacheService.generateGeoKey(lat, lng, radius, amenityType);

  // Check cache first
  const cached = cacheService.getCached(cacheKey);
  if (cached) {
    console.log(`✅ Cache hit for ${amenityType} near ${lat},${lng}`);
    return cached;
  }

  // Rate limiting
  if (!cacheService.checkRateLimit('overpass')) {
    console.log('⏱️ Rate limited, waiting...');
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  const query = `
    [out:json][timeout:25];
    (
      node["amenity"="${amenityType}"](around:${radius},${lat},${lng});
      way["amenity"="${amenityType}"](around:${radius},${lat},${lng});
      relation["amenity"="${amenityType}"](around:${radius},${lat},${lng});
    );
    out body;
    >;
    out skel qt;
  `;

  try {
    console.log(`🌍 Fetching ${amenityType} from Overpass API...`);
    const response = await axios.post(OVERPASS_API, query, {
      headers: { 'Content-Type': 'text/plain' },
      timeout: 30000
    });

    const facilities = parseOverpassResponse(response.data, lat, lng, amenityType);

    // Cache the results
    cacheService.setCached(cacheKey, facilities);

    console.log(`✅ Found ${facilities.length} ${amenityType}(s)`);
    return facilities;

  } catch (error) {
    console.error(`❌ Overpass API error:`, error.message);

    // Return empty array on error
    return [];
  }
}

/**
 * Parse Overpass API response
 */
function parseOverpassResponse(data, userLat, userLng, facilityType) {
  if (!data.elements || data.elements.length === 0) {
    return [];
  }

  const facilities = [];

  data.elements.forEach(element => {
    if (element.type === 'node' && element.tags) {
      const facility = {
        id: `osm_${element.id}`,
        name: element.tags.name || `${capitalizeFirst(facilityType)} ${element.id}`,
        address: buildAddress(element.tags),
        location: {
          lat: element.lat,
          lng: element.lon
        },
        phone: element.tags.phone || element.tags['contact:phone'] || null,
        website: element.tags.website || element.tags['contact:website'] || null,
        openingHours: element.tags.opening_hours || null,
        distance: calculateDistance(userLat, userLng, element.lat, element.lon),
        facilityType: facilityType,
        types: [facilityType],
        rating: null,
        totalRatings: 0,
        isOpen: null,
        source: 'openstreetmap'
      };

      facilities.push(facility);
    }
  });

  // Sort by distance
  facilities.sort((a, b) => a.distance - b.distance);

  return facilities;
}

/**
 * Build address from OSM tags
 */
function buildAddress(tags) {
  const parts = [];

  if (tags['addr:housenumber']) parts.push(tags['addr:housenumber']);
  if (tags['addr:street']) parts.push(tags['addr:street']);
  if (tags['addr:suburb']) parts.push(tags['addr:suburb']);
  if (tags['addr:city']) parts.push(tags['addr:city']);
  if (tags['addr:state']) parts.push(tags['addr:state']);
  if (tags['addr:postcode']) parts.push(tags['addr:postcode']);

  return parts.length > 0 ? parts.join(', ') : 'Address not available';
}

/**
 * Calculate distance between two points (Haversine formula)
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);

  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;

  return Math.round(distance * 10) / 10; // Round to 1 decimal
}

function toRad(degrees) {
  return degrees * (Math.PI / 180);
}

function capitalizeFirst(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Get nearby pharmacies
 */
async function getNearbyPharmacies(lat, lng, radius = 5000) {
  return await queryOverpass(lat, lng, radius, 'pharmacy');
}

/**
 * Get nearby hospitals
 */
async function getNearbyHospitals(lat, lng, radius = 5000) {
  return await queryOverpass(lat, lng, radius, 'hospital');
}

/**
 * Get nearby doctors/clinics
 */
async function getNearbyDoctors(lat, lng, radius = 5000) {
  return await queryOverpass(lat, lng, radius, 'doctors');
}

/**
 * Search facilities by name
 */
async function searchFacilities(query, lat, lng, radius = 5000) {
  // Get all facility types
  const [pharmacies, hospitals, doctors] = await Promise.all([
    getNearbyPharmacies(lat, lng, radius),
    getNearbyHospitals(lat, lng, radius),
    getNearbyDoctors(lat, lng, radius)
  ]);

  const allFacilities = [...pharmacies, ...hospitals, ...doctors];

  // Filter by query
  const searchTerm = query.toLowerCase();
  const filtered = allFacilities.filter(facility =>
    facility.name.toLowerCase().includes(searchTerm) ||
    facility.address.toLowerCase().includes(searchTerm)
  );

  return filtered;
}

module.exports = {
  getNearbyPharmacies,
  getNearbyHospitals,
  getNearbyDoctors,
  searchFacilities,
  calculateDistance
};
