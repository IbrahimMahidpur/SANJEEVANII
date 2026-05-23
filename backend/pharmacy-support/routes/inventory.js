const express = require('express');
const router = express.Router();
const inventoryService = require('../services/inventory-service');

/**
 * GET /api/pharmacy-support/inventory/availability
 * Search medicine availability across pharmacies
 */
router.get('/availability', async (req, res) => {
  try {
    const { medicine, lat, lng, radius = 5000 } = req.query;

    if (!medicine) {
      return res.status(400).json({
        error: 'Medicine name is required'
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

    const availability = await inventoryService.searchMedicineAvailability(
      medicine,
      latitude,
      longitude,
      searchRadius
    );

    res.json({
      success: true,
      medicine,
      count: availability.length,
      availability
    });

  } catch (error) {
    console.error('Error searching medicine availability:', error);
    res.status(500).json({
      error: 'Failed to search medicine availability',
      message: error.message
    });
  }
});

/**
 * GET /api/pharmacy-support/inventory/:pharmacyId
 * Get pharmacy inventory
 */
router.get('/:pharmacyId', async (req, res) => {
  try {
    const { pharmacyId } = req.params;

    const inventory = await inventoryService.getPharmacyInventory(pharmacyId);

    res.json({
      success: true,
      pharmacyId,
      count: inventory.length,
      inventory
    });

  } catch (error) {
    console.error('Error fetching pharmacy inventory:', error);
    res.status(500).json({
      error: 'Failed to fetch pharmacy inventory',
      message: error.message
    });
  }
});

/**
 * POST /api/pharmacy-support/inventory/:pharmacyId
 * Update pharmacy inventory
 */
router.post('/:pharmacyId', async (req, res) => {
  try {
    const { pharmacyId } = req.params;
    const { medicineName, quantity, price, expiryDate } = req.body;

    if (!medicineName || quantity === undefined || !price) {
      return res.status(400).json({
        error: 'Medicine name, quantity, and price are required'
      });
    }

    const inventory = await inventoryService.updateInventory(pharmacyId, {
      medicineName,
      quantity: parseInt(quantity),
      price: parseFloat(price),
      expiryDate
    });

    res.json({
      success: true,
      message: 'Inventory updated successfully',
      inventory
    });

  } catch (error) {
    console.error('Error updating inventory:', error);
    res.status(500).json({
      error: 'Failed to update inventory',
      message: error.message
    });
  }
});

/**
 * POST /api/pharmacy-support/inventory/pharmacy/register
 * Register new pharmacy
 */
router.post('/pharmacy/register', async (req, res) => {
  try {
    const { name, address, location, phone, email, openingHours } = req.body;

    if (!name || !address || !location || !phone) {
      return res.status(400).json({
        error: 'Name, address, location, and phone are required'
      });
    }

    const pharmacy = await inventoryService.addPharmacy({
      name,
      address,
      location,
      phone,
      email,
      openingHours
    });

    res.json({
      success: true,
      message: 'Pharmacy registered successfully',
      pharmacy
    });

  } catch (error) {
    console.error('Error registering pharmacy:', error);
    res.status(500).json({
      error: 'Failed to register pharmacy',
      message: error.message
    });
  }
});

module.exports = router;
