const express = require('express');
const router = express.Router();
const healthCampsService = require('../services/health-camps-service');

/**
 * GET /api/pharmacy-support/health-camps
 * Get health camps near location
 */
router.get('/', async (req, res) => {
  try {
    const { lat, lng, radius = 25000, type } = req.query;

    if (!lat || !lng) {
      return res.status(400).json({
        error: 'Latitude and longitude are required'
      });
    }

    const latitude = parseFloat(lat);
    const longitude = parseFloat(lng);
    const searchRadius = parseInt(radius);

    const camps = await healthCampsService.getHealthCampsNearby(
      latitude,
      longitude,
      searchRadius,
      type
    );

    res.json({
      success: true,
      count: camps.length,
      camps
    });

  } catch (error) {
    console.error('Error fetching health camps:', error);
    res.status(500).json({
      error: 'Failed to fetch health camps',
      message: error.message
    });
  }
});

/**
 * POST /api/pharmacy-support/health-camps
 * Add new health camp
 */
router.post('/', async (req, res) => {
  try {
    const { name, type, organizer, location, date, startTime, endTime, services, registrationRequired, contactPhone } = req.body;

    if (!name || !type || !organizer || !location || !date) {
      return res.status(400).json({
        error: 'Name, type, organizer, location, and date are required'
      });
    }

    const camp = await healthCampsService.addHealthCamp({
      name,
      type,
      organizer,
      location,
      date,
      startTime,
      endTime,
      services,
      registrationRequired,
      contactPhone
    });

    res.json({
      success: true,
      message: 'Health camp added successfully',
      camp
    });

  } catch (error) {
    console.error('Error adding health camp:', error);
    res.status(500).json({
      error: 'Failed to add health camp',
      message: error.message
    });
  }
});

/**
 * POST /api/pharmacy-support/health-camps/sync
 * Sync health camps from external sources
 */
router.post('/sync', async (req, res) => {
  try {
    const camps = await healthCampsService.syncHealthCamps();

    res.json({
      success: true,
      message: 'Health camps synced successfully',
      count: camps.length
    });

  } catch (error) {
    console.error('Error syncing health camps:', error);
    res.status(500).json({
      error: 'Failed to sync health camps',
      message: error.message
    });
  }
});

module.exports = router;
