// ============================================================================
// GOOGLE PLACES API INTEGRATION
// Using Google Cloud Service Account for authentication
// ============================================================================

import express from 'express';
import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const router = express.Router();
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load Google Cloud service account credentials
const SERVICE_ACCOUNT_PATH = path.join(__dirname, '..', '..', 'vaani-474822-36de07e0981f.json');
let serviceAccount = null;

try {
  serviceAccount = JSON.parse(fs.readFileSync(SERVICE_ACCOUNT_PATH, 'utf8'));
  console.log('✅ Google Cloud service account loaded');
} catch (error) {
  console.warn('⚠️ Google Cloud service account not found, Places API will be unavailable');
}

// Facility type mapping
const FACILITY_TYPE_MAP = {
  pharmacy: 'pharmacy',
  hospital: 'hospital',
  doctor: 'doctor'
};

/**
 * Search for nearby facilities using Google Places API
 */
router.get('/nearby', async (req, res) => {
  try {
    const { lat, lng, radius = 5000, type = 'pharmacy' } = req.query;
    const latitude = parseFloat(lat);
    const longitude = parseFloat(lng);
    const searchRadius = parseInt(radius);

    if (!serviceAccount) {
      return res.json({
        success: false,
        error: 'Google Places API not configured',
        results: []
      });
    }

    console.log(`🔍 [Google Places] Searching for ${type} within ${searchRadius}m of (${latitude}, ${longitude})`);

    // Use Google Places API (New) via REST
    const placeType = FACILITY_TYPE_MAP[type] || 'pharmacy';

    // Get OAuth2 token
    const auth = new google.auth.GoogleAuth({
      credentials: serviceAccount,
      scopes: ['https://www.googleapis.com/auth/cloud-platform']
    });

    const client = await auth.getClient();
    const accessToken = await client.getAccessToken();

    // Call Places API (New) - Nearby Search
    const response = await fetch(
      'https://places.googleapis.com/v1/places:searchNearby',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.token}`,
          'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.location,places.rating,places.userRatingCount,places.internationalPhoneNumber,places.websiteUri,places.regularOpeningHours,places.types,places.id'
        },
        body: JSON.stringify({
          includedTypes: [placeType],
          maxResultCount: 20,
          locationRestriction: {
            circle: {
              center: {
                latitude: latitude,
                longitude: longitude
              },
              radius: searchRadius
            }
          }
        })
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Google Places API error:', errorText);
      return res.json({
        success: false,
        error: 'Places API request failed',
        results: []
      });
    }

    const data = await response.json();
    const places = data.places || [];

    // Format results
    const results = places.map(place => ({
      id: `google_${place.id}`,
      name: place.displayName?.text || 'Unnamed',
      location: {
        lat: place.location?.latitude,
        lng: place.location?.longitude
      },
      address: place.formattedAddress || 'Address unavailable',
      vicinity: place.formattedAddress,
      phone: place.internationalPhoneNumber,
      website: place.websiteUri,
      rating: place.rating,
      userRatingsTotal: place.userRatingCount,
      openingHours: place.regularOpeningHours?.weekdayDescriptions?.join(', '),
      types: place.types || [],
      source: 'google'
    }));

    console.log(`✅ Found ${results.length} facilities from Google Places`);

    res.json({
      success: true,
      count: results.length,
      results,
      source: 'google_places',
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Google Places API error:', error);
    res.json({
      success: false,
      error: error.message,
      results: []
    });
  }
});

/**
 * Get detailed information about a specific place
 */
router.get('/details', async (req, res) => {
  try {
    const { placeId } = req.query;

    if (!serviceAccount) {
      return res.status(503).json({
        success: false,
        error: 'Google Places API not configured'
      });
    }

    console.log(`🔍 [Google Places] Getting details for place: ${placeId}`);

    // Get OAuth2 token
    const auth = new google.auth.GoogleAuth({
      credentials: serviceAccount,
      scopes: ['https://www.googleapis.com/auth/cloud-platform']
    });

    const client = await auth.getClient();
    const accessToken = await client.getAccessToken();

    // Call Places API (New) - Place Details
    const response = await fetch(
      `https://places.googleapis.com/v1/places/${placeId}`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken.token}`,
          'X-Goog-FieldMask': 'displayName,formattedAddress,location,rating,userRatingCount,internationalPhoneNumber,websiteUri,regularOpeningHours,photos,reviews,types'
        }
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Google Places API error:', errorText);
      return res.status(500).json({
        success: false,
        error: 'Failed to get place details'
      });
    }

    const place = await response.json();

    const details = {
      id: place.id,
      name: place.displayName?.text,
      address: place.formattedAddress,
      location: {
        lat: place.location?.latitude,
        lng: place.location?.longitude
      },
      phone: place.internationalPhoneNumber,
      website: place.websiteUri,
      rating: place.rating,
      userRatingsTotal: place.userRatingCount,
      openingHours: place.regularOpeningHours,
      photos: place.photos?.map(photo => photo.name),
      reviews: place.reviews,
      types: place.types
    };

    console.log(`✅ Retrieved details for: ${details.name}`);

    res.json({
      success: true,
      details,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('❌ Place details error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

console.log('✅ Google Places API routes loaded');

export default router;
