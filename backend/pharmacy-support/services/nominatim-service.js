const axios = require('axios');
const cacheService = require('./cache-service');

const NOMINATIM_API = 'https://nominatim.openstreetmap.org';
const USER_AGENT = 'Sanjeevani-Pharmacy-Support/1.0';

/**
 * Reverse geocoding - Get address from coordinates
 */
async function reverseGeocode(lat, lng) {
  const cacheKey = `nominatim_reverse_${lat}_${lng}`;

  // Check cache
  const cached = cacheService.getCached(cacheKey);
  if (cached) {
    return cached;
  }

  // Rate limiting
  if (!cacheService.checkRateLimit('nominatim')) {
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  try {
    const response = await axios.get(`${NOMINATIM_API}/reverse`, {
      params: {
        lat,
        lon: lng,
        format: 'json',
        addressdetails: 1
      },
      headers: {
        'User-Agent': USER_AGENT
      },
      timeout: 10000
    });

    const result = {
      displayName: response.data.display_name,
      address: response.data.address,
      city: response.data.address.city || response.data.address.town || response.data.address.village,
      state: response.data.address.state,
      country: response.data.address.country,
      postcode: response.data.address.postcode
    };

    cacheService.setCached(cacheKey, result);
    return result;

  } catch (error) {
    console.error('❌ Nominatim reverse geocoding error:', error.message);
    return null;
  }
}

/**
 * Forward geocoding - Get coordinates from address
 */
async function forwardGeocode(address) {
  const cacheKey = `nominatim_forward_${address}`;

  // Check cache
  const cached = cacheService.getCached(cacheKey);
  if (cached) {
    return cached;
  }

  // Rate limiting
  if (!cacheService.checkRateLimit('nominatim')) {
    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  try {
    const response = await axios.get(`${NOMINATIM_API}/search`, {
      params: {
        q: address,
        format: 'json',
        addressdetails: 1,
        limit: 1
      },
      headers: {
        'User-Agent': USER_AGENT
      },
      timeout: 10000
    });

    if (response.data.length === 0) {
      return null;
    }

    const result = {
      lat: parseFloat(response.data[0].lat),
      lng: parseFloat(response.data[0].lon),
      displayName: response.data[0].display_name,
      address: response.data[0].address
    };

    cacheService.setCached(cacheKey, result);
    return result;

  } catch (error) {
    console.error('❌ Nominatim forward geocoding error:', error.message);
    return null;
  }
}

/**
 * Get city name from coordinates
 */
async function getCityName(lat, lng) {
  const geocoded = await reverseGeocode(lat, lng);
  return geocoded ? geocoded.city : null;
}

module.exports = {
  reverseGeocode,
  forwardGeocode,
  getCityName
};
