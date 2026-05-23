const express = require('express');
const router = express.Router();
const overpassService = require('../services/overpass-service');
const inventoryService = require('../services/inventory-service');

/**
 * GET /api/pharmacy-support/facilities/nearby
 * Get nearby medical facilities
 */
router.get('/nearby', async (req, res) => {
  try {
    const { lat, lng, radius = 5000, type = 'all' } = req.query;

    if (!lat || !lng) {
      return res.status(400).json({
        error: 'Latitude and longitude are required'
      });
    }

    const latitude = parseFloat(lat);
    const longitude = parseFloat(lng);
    const searchRadius = parseInt(radius);

    let results = [];

    if (type === 'all' || type === 'pharmacy') {
      // Get from both Overpass and local inventory
      const overpassPharmacies = await overpassService.getNearbyPharmacies(latitude, longitude, searchRadius);
      const localPharmacies = await inventoryService.getAllPharmacies();

      // Filter local pharmacies by distance
      const nearbyLocalPharmacies = localPharmacies
        .map(p => ({
          ...p,
          facilityType: 'pharmacy',
          types: ['pharmacy'],
          rating: null,
          totalRatings: 0,
          isOpen: null,
          distance: overpassService.calculateDistance(latitude, longitude, p.location.lat, p.location.lng)
        }))
        .filter(p => p.distance <= searchRadius / 1000);

      results = [...results, ...overpassPharmacies, ...nearbyLocalPharmacies];
    }

    if (type === 'all' || type === 'hospital') {
      const hospitals = await overpassService.getNearbyHospitals(latitude, longitude, searchRadius);
      results = [...results, ...hospitals];
    }

    if (type === 'all' || type === 'doctor') {
      const doctors = await overpassService.getNearbyDoctors(latitude, longitude, searchRadius);
      results = [...results, ...doctors];
    }

    // Remove duplicates based on name and location
    const uniqueResults = results.filter((facility, index, self) =>
      index === self.findIndex(f =>
        f.name === facility.name &&
        Math.abs(f.location.lat - facility.location.lat) < 0.001 &&
        Math.abs(f.location.lng - facility.location.lng) < 0.001
      )
    );

    // Sort by distance
    uniqueResults.sort((a, b) => a.distance - b.distance);

    res.json({
      success: true,
      count: uniqueResults.length,
      results: uniqueResults
    });

  } catch (error) {
    console.error('Error fetching nearby facilities:', error);
    res.status(500).json({
      error: 'Failed to fetch nearby facilities',
      message: error.message
    });
  }
});

/**
 * GET /api/pharmacy-support/facilities/search
 * Search facilities by name
 */
router.get('/search', async (req, res) => {
  try {
    const { query, lat, lng, radius = 5000 } = req.query;

    if (!query) {
      return res.status(400).json({
        error: 'Search query is required'
      });
    }

    if (!lat || !lng) {
      return res.status(400).json({
        error: 'Latitude and longitude are required'
      });
    }

    const latitude = parseFloat(lat);
    const longitude = parseFloat(lng);
    const searchRadius = parseInt(radius);

    const results = await overpassService.searchFacilities(query, latitude, longitude, searchRadius);

    res.json({
      success: true,
      count: results.length,
      results
    });

  } catch (error) {
    console.error('Error searching facilities:', error);
    res.status(500).json({
      error: 'Failed to search facilities',
      message: error.message
    });
  }
});

module.exports = router;
