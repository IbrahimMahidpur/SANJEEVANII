import express from 'express';
import axios from 'axios';
import NodeCache from 'node-cache';
import rateLimit from 'express-rate-limit';
import dotenv from 'dotenv';

dotenv.config();

const router = express.Router();
const cache = new NodeCache({ stdTTL: parseInt(process.env.CACHE_TTL) || 300 });

// Rate limiter: 100 requests per 15 minutes
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW) || 900000,
  max: parseInt(process.env.RATE_LIMIT_MAX) || 100,
  message: { error: 'Too many requests, please try again later.' }
});

router.use(limiter);

const GOOGLE_API_KEY = process.env.GOOGLE_MAPS_API_KEY;
const PLACES_API_URL = 'https://maps.googleapis.com/maps/api/place';

// Helper function to calculate distance between two coordinates
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Radius of Earth in kilometers
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * GET /api/pharmacy/nearby
 * Find nearby pharmacies or doctors
 * Query params: lat, lng, radius (in meters), type (pharmacy|doctor|hospital)
 */
router.get('/nearby', async (req, res) => {
  try {
    const { lat, lng, radius = 5000, type = 'pharmacy' } = req.query;

    if (!lat || !lng) {
      return res.status(400).json({ error: 'Latitude and longitude are required' });
    }

    const cacheKey = `nearby_${lat}_${lng}_${radius}_${type}`;
    const cachedData = cache.get(cacheKey);

    if (cachedData) {
      console.log('✓ Cache hit for nearby search');
      return res.json(cachedData);
    }

    // Map type to Google Places types
    const placeTypes = {
      pharmacy: 'pharmacy',
      doctor: 'doctor',
      hospital: 'hospital',
      clinic: 'health'
    };

    const placeType = placeTypes[type] || 'pharmacy';

    // Enhanced Places API request with pagination support
    let allResults = [];
    let nextPageToken = null;
    let pageCount = 0;
    const maxPages = 3; // Google allows max 3 pages (60 results per page = 180 total)

    do {
      const params = {
        location: `${lat},${lng}`,
        radius: radius,
        type: placeType,
        key: GOOGLE_API_KEY,
        rankby: 'prominence',
        language: 'en'
      };

      if (nextPageToken) {
        params.pagetoken = nextPageToken;
        // Wait 2 seconds before next page request (Google requirement)
        await new Promise(resolve => setTimeout(resolve, 2000));
      }

      const response = await axios.get(`${PLACES_API_URL}/nearbysearch/json`, { params });

      if (response.data.status !== 'OK' && response.data.status !== 'ZERO_RESULTS') {
        console.error('Google Places API Error:', response.data.status);
        if (allResults.length > 0) {
          break; // Use partial results if we have some
        }
        return res.status(500).json({
          error: 'Failed to fetch nearby locations',
          details: response.data.status
        });
      }

      // Add results from this page
      if (response.data.results) {
        allResults = allResults.concat(response.data.results);
      }

      nextPageToken = response.data.next_page_token || null;
      pageCount++;

      console.log(`✓ Fetched page ${pageCount}: ${response.data.results?.length || 0} results (total: ${allResults.length})`);

    } while (nextPageToken && pageCount < maxPages);

    // Format the results with enhanced data
    const results = allResults.map(place => {
      const distance = calculateDistance(
        parseFloat(lat),
        parseFloat(lng),
        place.geometry.location.lat,
        place.geometry.location.lng
      );

      return {
        id: place.place_id,
        name: place.name,
        address: place.vicinity,
        formattedAddress: place.formatted_address || place.vicinity,
        location: {
          lat: place.geometry.location.lat,
          lng: place.geometry.location.lng
        },
        distance: parseFloat(distance.toFixed(2)),
        rating: place.rating || null,
        totalRatings: place.user_ratings_total || 0,
        isOpen: place.opening_hours?.open_now || null,

        // Enhanced fields for better accuracy
        businessStatus: place.business_status || 'OPERATIONAL',
        priceLevel: place.price_level || null, // 0-4 scale
        plusCode: place.plus_code?.global_code || null,

        types: place.types,
        icon: place.icon,
        iconBackgroundColor: place.icon_background_color || null,
        iconMaskBaseUri: place.icon_mask_base_uri || null,

        photos: place.photos ? place.photos.slice(0, 5).map(photo => ({
          reference: photo.photo_reference,
          width: photo.width,
          height: photo.height,
          attributions: photo.html_attributions || []
        })) : [],

        // Additional metadata
        permanentlyClosed: place.business_status === 'CLOSED_PERMANENTLY',
        temporarilyClosed: place.business_status === 'CLOSED_TEMPORARILY',

        // Geometry viewport for better map display
        viewport: place.geometry.viewport || null
      };
    });

    // Sort by distance
    results.sort((a, b) => a.distance - b.distance);

    const responseData = {
      results,
      count: results.length,
      searchLocation: { lat: parseFloat(lat), lng: parseFloat(lng) },
      radius: parseInt(radius),
      type,
      pagesFetched: pageCount,
      // Add metadata about search quality
      searchQuality: {
        totalResults: results.length,
        averageDistance: results.length > 0
          ? (results.reduce((sum, r) => sum + r.distance, 0) / results.length).toFixed(2)
          : 0,
        hasPhotos: results.filter(r => r.photos.length > 0).length,
        hasRatings: results.filter(r => r.rating !== null).length
      }
    };

    cache.set(cacheKey, responseData);
    console.log(`✓ Found ${results.length} ${type}(s) within ${radius}m across ${pageCount} pages (avg distance: ${responseData.searchQuality.averageDistance}km)`);

    res.json(responseData);
  } catch (error) {
    console.error('Error in /nearby:', error.message);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

/**
 * GET /api/pharmacy/details/:placeId
 * Get detailed information about a specific place
 */
router.get('/details/:placeId', async (req, res) => {
  try {
    const { placeId } = req.params;

    if (!placeId) {
      return res.status(400).json({ error: 'Place ID is required' });
    }

    const cacheKey = `details_${placeId}`;
    const cachedData = cache.get(cacheKey);

    if (cachedData) {
      console.log('✓ Cache hit for place details');
      return res.json(cachedData);
    }

    // Request comprehensive fields from Places API for maximum accuracy
    const response = await axios.get(`${PLACES_API_URL}/details/json`, {
      params: {
        place_id: placeId,
        fields: [
          // Basic Information
          'name', 'formatted_address', 'formatted_phone_number', 'international_phone_number',
          'website', 'url', 'types', 'place_id',

          // Location & Geometry
          'geometry', 'plus_code', 'vicinity',

          // Business Information
          'business_status', 'price_level', 'rating', 'user_ratings_total',

          // Hours & Availability
          'opening_hours', 'current_opening_hours', 'secondary_opening_hours',

          // Media
          'photos', 'icon', 'icon_background_color', 'icon_mask_base_uri',

          // Reviews & Editorial
          'reviews', 'editorial_summary',

          // Accessibility & Services
          'wheelchair_accessible_entrance', 'delivery', 'dine_in', 'takeout',
          'reservable', 'serves_breakfast', 'serves_lunch', 'serves_dinner',
          'serves_beer', 'serves_wine', 'serves_brunch', 'serves_vegetarian_food',

          // Additional Details
          'utc_offset', 'adr_address'
        ].join(','),
        key: GOOGLE_API_KEY,
        language: 'en'
      }
    });

    if (response.data.status !== 'OK') {
      console.error('Google Places API Error:', response.data.status);
      return res.status(500).json({
        error: 'Failed to fetch place details',
        details: response.data.status
      });
    }

    const place = response.data.result;

    const detailsData = {
      id: placeId,
      name: place.name,
      address: place.formatted_address,
      vicinity: place.vicinity || null,
      phone: place.formatted_phone_number || null,
      internationalPhone: place.international_phone_number || null,
      website: place.website || null,
      googleMapsUrl: place.url || null,

      location: {
        lat: place.geometry.location.lat,
        lng: place.geometry.location.lng
      },
      viewport: place.geometry.viewport || null,
      plusCode: place.plus_code?.global_code || null,

      // Business Information
      businessStatus: place.business_status || 'OPERATIONAL',
      priceLevel: place.price_level || null,
      rating: place.rating || null,
      totalRatings: place.user_ratings_total || 0,

      // Opening Hours with enhanced data
      openingHours: place.opening_hours ? {
        isOpen: place.opening_hours.open_now,
        weekdayText: place.opening_hours.weekday_text || [],
        periods: place.opening_hours.periods || []
      } : null,

      // Current opening hours (if different from regular)
      currentOpeningHours: place.current_opening_hours || null,
      secondaryOpeningHours: place.secondary_opening_hours || null,

      types: place.types || [],

      // Media
      icon: place.icon || null,
      iconBackgroundColor: place.icon_background_color || null,
      iconMaskBaseUri: place.icon_mask_base_uri || null,
      photos: place.photos ? place.photos.slice(0, 10).map(photo => ({
        reference: photo.photo_reference,
        width: photo.width,
        height: photo.height,
        attributions: photo.html_attributions || []
      })) : [],

      // Reviews with enhanced data
      reviews: place.reviews ? place.reviews.slice(0, 5).map(review => ({
        authorName: review.author_name,
        authorUrl: review.author_url || null,
        language: review.language || 'en',
        profilePhotoUrl: review.profile_photo_url || null,
        rating: review.rating,
        relativeTimeDescription: review.relative_time_description,
        text: review.text,
        time: review.time
      })) : [],

      // Editorial Summary (AI-generated description from Google)
      editorialSummary: place.editorial_summary?.overview || null,

      // Accessibility & Services
      accessibility: {
        wheelchairAccessibleEntrance: place.wheelchair_accessible_entrance || null
      },

      services: {
        delivery: place.delivery || null,
        dineIn: place.dine_in || null,
        takeout: place.takeout || null,
        reservable: place.reservable || null
      },

      servesFood: {
        breakfast: place.serves_breakfast || null,
        lunch: place.serves_lunch || null,
        dinner: place.serves_dinner || null,
        brunch: place.serves_brunch || null,
        vegetarian: place.serves_vegetarian_food || null
      },

      servesBeverages: {
        beer: place.serves_beer || null,
        wine: place.serves_wine || null
      },

      // Additional metadata
      utcOffset: place.utc_offset || null,
      adrAddress: place.adr_address || null,

      // Status flags
      permanentlyClosed: place.business_status === 'CLOSED_PERMANENTLY',
      temporarilyClosed: place.business_status === 'CLOSED_TEMPORARILY'
    };

    cache.set(cacheKey, detailsData);
    console.log(`✓ Fetched enhanced details for: ${place.name}`);

    res.json(detailsData);
  } catch (error) {
    console.error('Error in /details:', error.message);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

/**
 * GET /api/pharmacy/photo/:photoReference
 * Get photo URL for a place
 */
router.get('/photo/:photoReference', async (req, res) => {
  try {
    const { photoReference } = req.params;
    const { maxwidth = 400 } = req.query;

    if (!photoReference) {
      return res.status(400).json({ error: 'Photo reference is required' });
    }

    const photoUrl = `${PLACES_API_URL}/photo?maxwidth=${maxwidth}&photo_reference=${photoReference}&key=${GOOGLE_API_KEY}`;

    res.json({ url: photoUrl });
  } catch (error) {
    console.error('Error in /photo:', error.message);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

/**
 * POST /api/pharmacy/geocode
 * Convert address to coordinates
 */
router.post('/geocode', async (req, res) => {
  try {
    const { address } = req.body;

    if (!address) {
      return res.status(400).json({ error: 'Address is required' });
    }

    const cacheKey = `geocode_${address}`;
    const cachedData = cache.get(cacheKey);

    if (cachedData) {
      console.log('✓ Cache hit for geocoding');
      return res.json(cachedData);
    }

    const response = await axios.get('https://maps.googleapis.com/maps/api/geocode/json', {
      params: {
        address: address,
        key: GOOGLE_API_KEY
      }
    });

    if (response.data.status !== 'OK') {
      console.error('Geocoding API Error:', response.data.status);
      return res.status(500).json({
        error: 'Failed to geocode address',
        details: response.data.status
      });
    }

    const result = response.data.results[0];
    const geocodeData = {
      address: result.formatted_address,
      location: {
        lat: result.geometry.location.lat,
        lng: result.geometry.location.lng
      }
    };

    cache.set(cacheKey, geocodeData);
    console.log(`✓ Geocoded: ${address}`);

    res.json(geocodeData);
  } catch (error) {
    console.error('Error in /geocode:', error.message);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

/**
 * GET /api/pharmacy/search
 * Search for pharmacies or doctors by name/query
 */
router.get('/search', async (req, res) => {
  try {
    const { query, lat, lng, radius = 10000 } = req.query;

    if (!query) {
      return res.status(400).json({ error: 'Search query is required' });
    }

    if (!lat || !lng) {
      return res.status(400).json({ error: 'Latitude and longitude are required' });
    }

    const cacheKey = `search_${query}_${lat}_${lng}_${radius}`;
    const cachedData = cache.get(cacheKey);

    if (cachedData) {
      console.log('✓ Cache hit for search');
      return res.json(cachedData);
    }

    const response = await axios.get(`${PLACES_API_URL}/textsearch/json`, {
      params: {
        query: query,
        location: `${lat},${lng}`,
        radius: radius,
        key: GOOGLE_API_KEY
      }
    });

    if (response.data.status !== 'OK' && response.data.status !== 'ZERO_RESULTS') {
      console.error('Google Places API Error:', response.data.status);
      return res.status(500).json({
        error: 'Failed to search',
        details: response.data.status
      });
    }

    const results = response.data.results.map(place => {
      const distance = calculateDistance(
        parseFloat(lat),
        parseFloat(lng),
        place.geometry.location.lat,
        place.geometry.location.lng
      );

      return {
        id: place.place_id,
        name: place.name,
        address: place.formatted_address,
        location: {
          lat: place.geometry.location.lat,
          lng: place.geometry.location.lng
        },
        distance: parseFloat(distance.toFixed(2)),
        rating: place.rating || null,
        totalRatings: place.user_ratings_total || 0,
        isOpen: place.opening_hours?.open_now || null,
        types: place.types
      };
    });

    results.sort((a, b) => a.distance - b.distance);

    const searchData = {
      results,
      count: results.length,
      query
    };

    cache.set(cacheKey, searchData);
    console.log(`✓ Search "${query}" found ${results.length} results`);

    res.json(searchData);
  } catch (error) {
    console.error('Error in /search:', error.message);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

/**
 * POST /api/pharmacy/distance-matrix
 * Calculate travel times and distances from user location to multiple destinations
 * Body: { origins: [{lat, lng}], destinations: [{lat, lng}] }
 */
router.post('/distance-matrix', async (req, res) => {
  try {
    const { origins, destinations } = req.body;

    if (!origins || !destinations || !Array.isArray(origins) || !Array.isArray(destinations)) {
      return res.status(400).json({ error: 'Origins and destinations arrays are required' });
    }

    if (origins.length === 0 || destinations.length === 0) {
      return res.status(400).json({ error: 'Origins and destinations cannot be empty' });
    }

    // Limit to 25 destinations per request (Google API limit)
    if (destinations.length > 25) {
      return res.status(400).json({ error: 'Maximum 25 destinations allowed per request' });
    }

    const originsStr = origins.map(o => `${o.lat},${o.lng}`).join('|');
    const destinationsStr = destinations.map(d => `${d.lat},${d.lng}`).join('|');

    const cacheKey = `distance_matrix_${originsStr}_${destinationsStr}`;
    const cachedData = cache.get(cacheKey);

    if (cachedData) {
      console.log('✓ Cache hit for distance matrix');
      return res.json(cachedData);
    }

    const response = await axios.get('https://maps.googleapis.com/maps/api/distancematrix/json', {
      params: {
        origins: originsStr,
        destinations: destinationsStr,
        mode: 'driving',
        units: 'metric',
        key: GOOGLE_API_KEY
      }
    });

    if (response.data.status !== 'OK') {
      console.error('Distance Matrix API Error:', response.data.status);
      return res.status(500).json({
        error: 'Failed to calculate distances',
        details: response.data.status
      });
    }

    const matrixData = {
      origins,
      destinations,
      rows: response.data.rows.map(row => ({
        elements: row.elements.map(element => ({
          distance: element.distance,
          duration: element.duration,
          status: element.status
        }))
      }))
    };

    cache.set(cacheKey, matrixData);
    console.log(`✓ Calculated distances for ${origins.length} origins to ${destinations.length} destinations`);

    res.json(matrixData);
  } catch (error) {
    console.error('Error in /distance-matrix:', error.message);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

/**
 * GET /api/pharmacy/autocomplete
 * Autocomplete place suggestions
 * Query params: input (search text), lat, lng
 */
router.get('/autocomplete', async (req, res) => {
  try {
    const { input, lat, lng } = req.query;

    if (!input || input.length < 2) {
      return res.status(400).json({ error: 'Input must be at least 2 characters' });
    }

    const cacheKey = `autocomplete_${input}_${lat}_${lng}`;
    const cachedData = cache.get(cacheKey);

    if (cachedData) {
      console.log('✓ Cache hit for autocomplete');
      return res.json(cachedData);
    }

    const params = {
      input,
      types: 'pharmacy|doctor|hospital|health',
      key: GOOGLE_API_KEY
    };

    if (lat && lng) {
      params.location = `${lat},${lng}`;
      params.radius = 50000; // 50km
    }

    const response = await axios.get(`${PLACES_API_URL}/autocomplete/json`, {
      params
    });

    if (response.data.status !== 'OK' && response.data.status !== 'ZERO_RESULTS') {
      console.error('Autocomplete API Error:', response.data.status);
      return res.status(500).json({
        error: 'Failed to get autocomplete suggestions',
        details: response.data.status
      });
    }

    const suggestions = (response.data.predictions || []).map(prediction => ({
      placeId: prediction.place_id,
      description: prediction.description,
      mainText: prediction.structured_formatting?.main_text,
      secondaryText: prediction.structured_formatting?.secondary_text,
      types: prediction.types
    }));

    const autocompleteData = {
      input,
      suggestions
    };

    cache.set(cacheKey, autocompleteData);
    console.log(`✓ Found ${suggestions.length} autocomplete suggestions`);

    res.json(autocompleteData);
  } catch (error) {
    console.error('Error in /autocomplete:', error.message);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

/**
 * GET /api/pharmacy/health
 * Health check endpoint
 */
router.get('/health', (req, res) => {
  const cacheStats = cache.getStats();

  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    cache: {
      keys: cacheStats.keys,
      hits: cacheStats.hits,
      misses: cacheStats.misses,
      hitRate: cacheStats.hits / (cacheStats.hits + cacheStats.misses) || 0
    },
    apiKey: GOOGLE_API_KEY ? 'configured' : 'missing'
  });
});

export default router;
