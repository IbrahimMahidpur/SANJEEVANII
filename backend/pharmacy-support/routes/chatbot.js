const express = require('express');
const router = express.Router();
const aiChatbotService = require('../services/ai-chatbot-service');

/**
 * POST /api/pharmacy-support/chatbot/query
 * Query the AI chatbot
 */
router.post('/query', async (req, res) => {
  try {
    const { message, context, sessionId } = req.body;

    if (!message) {
      return res.status(400).json({
        error: 'Message is required'
      });
    }

    const response = await aiChatbotService.queryChatbot(message, context, sessionId);

    res.json({
      success: true,
      ...response
    });

  } catch (error) {
    console.error('Error querying chatbot:', error);
    res.status(500).json({
      error: 'Failed to query chatbot',
      message: error.message
    });
  }
});

/**
 * POST /api/pharmacy-support/chatbot/medicine-info
 * Get medicine information
 */
router.post('/medicine-info', async (req, res) => {
  try {
    const { medicineName } = req.body;

    if (!medicineName) {
      return res.status(400).json({
        error: 'Medicine name is required'
      });
    }

    const response = await aiChatbotService.getMedicineInfo(medicineName);

    res.json({
      success: true,
      ...response
    });

  } catch (error) {
    console.error('Error getting medicine info:', error);
    res.status(500).json({
      error: 'Failed to get medicine information',
      message: error.message
    });
  }
});

/**
 * POST /api/pharmacy-support/chatbot/doctor-recommendation
 * Get doctor recommendation based on symptoms
 */
router.post('/doctor-recommendation', async (req, res) => {
  try {
    const { symptoms } = req.body;

    if (!symptoms) {
      return res.status(400).json({
        error: 'Symptoms are required'
      });
    }

    const response = await aiChatbotService.getDoctorRecommendation(symptoms);

    res.json({
      success: true,
      ...response
    });

  } catch (error) {
    console.error('Error getting doctor recommendation:', error);
    res.status(500).json({
      error: 'Failed to get doctor recommendation',
      message: error.message
    });
  }
});

/**
 * POST /api/pharmacy-support/chatbot/first-aid
 * Get first aid advice
 */
router.post('/first-aid', async (req, res) => {
  try {
    const { situation } = req.body;

    if (!situation) {
      return res.status(400).json({
        error: 'Situation description is required'
      });
    }

    const response = await aiChatbotService.getFirstAidAdvice(situation);

    res.json({
      success: true,
      ...response
    });

  } catch (error) {
    console.error('Error getting first aid advice:', error);
    res.status(500).json({
      error: 'Failed to get first aid advice',
      message: error.message
    });
  }
});

/**
 * POST /api/pharmacy-support/chatbot/interpret-prescription
 * Interpret prescription
 */
router.post('/interpret-prescription', async (req, res) => {
  try {
    const { prescriptionText } = req.body;

    if (!prescriptionText) {
      return res.status(400).json({
        error: 'Prescription text is required'
      });
    }

    const response = await aiChatbotService.interpretPrescription(prescriptionText);

    res.json({
      success: true,
      ...response
    });

  } catch (error) {
    console.error('Error interpreting prescription:', error);
    res.status(500).json({
      error: 'Failed to interpret prescription',
      message: error.message
    });
  }
});

module.exports = router;
