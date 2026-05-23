const express = require('express');
const router = express.Router();
const axios = require('axios');

// Google Maps API Key - store in environment variable
const GOOGLE_MAPS_API_KEY = process.env.GOOGLE_MAPS_API_KEY || 'AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8';

// Proxy endpoint for Google Places Nearby Search
router.post('/nearby-search', async (req, res) => {
  try {
    const { location, radius, type, keyword } = req.body;

    if (!location || !location.lat || !location.lng) {
      return res.status(400).json({ error: 'Location is required' });
    }

    const params = {
      location: `${location.lat},${location.lng}`,
      radius: radius || 5000,
      key: GOOGLE_MAPS_API_KEY
    };

    if (type) params.type = type;
    if (keyword) params.keyword = keyword;

    console.log(`🔍 Searching Google Places: ${type} within ${radius / 1000}km`);

    const response = await axios.get(
      'https://maps.googleapis.com/maps/api/place/nearbysearch/json',
      { params }
    );

    if (response.data.status === 'OK') {
      console.log(`✅ Found ${response.data.results.length} places`);
      res.json({
        status: 'OK',
        results: response.data.results
      });
    } else {
      console.log(`⚠️ Places API returned: ${response.data.status}`);
      res.json({
        status: response.data.status,
        results: []
      });
    }
  } catch (error) {
    console.error('❌ Places API error:', error.message);
    res.status(500).json({
      error: 'Failed to search places',
      message: error.message
    });
  }
});

module.exports = router;
