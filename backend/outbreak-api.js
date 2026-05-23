// Outbreak Alert API Routes - Real Data Integration
import express from 'express';
import outbreakData from './outbreak-data.js';
import outbreakDetector from './outbreak-detector.js';
import realOutbreakDetector from './real-outbreak-detector.js';

const router = express.Router();

// Toggle between real and mock data via environment variable
const USE_REAL_DATA = process.env.USE_REAL_OUTBREAK_DATA !== 'false'; // Default to REAL data
const detector = USE_REAL_DATA ? realOutbreakDetector : outbreakDetector;

console.log(`📊 Outbreak API Mode: ${USE_REAL_DATA ? '🌍 REAL NEWS DATA' : '🧪 MOCK DATA'}`);

// Start real data fetcher if enabled
if (USE_REAL_DATA) {
  console.log('🚀 Starting real outbreak detector with news integration...');
  realOutbreakDetector.startAutoRefresh();
}

// GET /api/outbreak/alerts - Get all alerts with optional filters
router.get('/alerts', (req, res) => {
  try {
    const { disease, region, severity, status, startDate, endDate } = req.query;

    const filters = {};
    if (disease) filters.disease = disease;
    if (region) filters.region = region;
    if (severity) filters.severity = severity;
    if (status) filters.status = status;
    if (startDate) filters.startDate = startDate;
    if (endDate) filters.endDate = endDate;

    const alerts = detector.getAlerts(filters);

    res.json({
      success: true,
      count: alerts.length,
      alerts,
      dataSource: USE_REAL_DATA ? 'real_news' : 'mock',
      lastUpdate: USE_REAL_DATA ? realOutbreakDetector.lastUpdate : null
    });
  } catch (error) {
    console.error('Error fetching alerts:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/outbreak/daily-counts - Get daily case counts with filters
router.get('/daily-counts', (req, res) => {
  try {
    const { disease, region, startDate, endDate } = req.query;

    const filters = {};
    if (disease) filters.disease = disease;
    if (region) filters.region = region;
    if (startDate) filters.startDate = startDate;
    if (endDate) filters.endDate = endDate;

    const counts = outbreakData.getDailyCounts(filters);

    res.json({
      success: true,
      count: counts.length,
      data: counts,
    });
  } catch (error) {
    console.error('Error fetching daily counts:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/outbreak/regions - Get all monitored regions
router.get('/regions', (req, res) => {
  try {
    const regions = outbreakData.getRegions();

    res.json({
      success: true,
      count: regions.length,
      regions,
    });
  } catch (error) {
    console.error('Error fetching regions:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/outbreak/diseases - Get all tracked diseases
router.get('/diseases', (req, res) => {
  try {
    const diseases = outbreakData.getDiseases();

    res.json({
      success: true,
      count: diseases.length,
      diseases,
    });
  } catch (error) {
    console.error('Error fetching diseases:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// POST /api/outbreak/detect - Trigger anomaly detection (mock data only)
router.post('/detect', (req, res) => {
  try {
    if (USE_REAL_DATA) {
      return res.json({
        success: true,
        message: 'Real data mode - detection runs automatically',
        note: 'News is fetched every 30 minutes'
      });
    }

    const newAlerts = outbreakDetector.runDetection();

    res.json({
      success: true,
      message: 'Detection completed',
      newAlerts: newAlerts.length,
      alerts: newAlerts,
    });
  } catch (error) {
    console.error('Error running detection:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/outbreak/statistics - Get outbreak statistics
router.get('/statistics', (req, res) => {
  try {
    const statistics = USE_REAL_DATA
      ? realOutbreakDetector.getStatistics()
      : outbreakDetector.getStatistics();

    res.json({
      success: true,
      statistics,
      dataSource: USE_REAL_DATA ? 'real_news' : 'mock'
    });
  } catch (error) {
    console.error('Error fetching statistics:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// PATCH /api/outbreak/alerts/:id - Update alert status
router.patch('/alerts/:id', (req, res) => {
  try {
    const { id } = req.params;
    const { status } = req.body;

    if (!status || !['open', 'acknowledged', 'resolved'].includes(status)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid status. Must be: open, acknowledged, or resolved',
      });
    }

    const updatedAlert = detector.updateAlertStatus
      ? detector.updateAlertStatus(id, status)
      : null;

    if (!updatedAlert) {
      return res.status(404).json({
        success: false,
        error: 'Alert not found or update not supported',
      });
    }

    res.json({
      success: true,
      alert: updatedAlert,
    });
  } catch (error) {
    console.error('Error updating alert:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/outbreak/latest - Get latest counts for all disease-region combinations
router.get('/latest', (req, res) => {
  try {
    const latest = outbreakData.getLatestCounts();

    res.json({
      success: true,
      count: latest.length,
      data: latest,
    });
  } catch (error) {
    console.error('Error fetching latest counts:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// GET /api/outbreak/status - Get API status and configuration
router.get('/status', (req, res) => {
  res.json({
    success: true,
    mode: USE_REAL_DATA ? 'real_news' : 'mock',
    features: {
      realData: USE_REAL_DATA,
      autoRefresh: USE_REAL_DATA,
      newsAPI: process.env.NEWS_API_KEY ? 'configured' : 'not_configured',
      googleNews: 'enabled'
    },
    lastUpdate: USE_REAL_DATA ? realOutbreakDetector.lastUpdate : null,
    alertCount: USE_REAL_DATA ? realOutbreakDetector.alerts.length : outbreakDetector.alerts.length
  });
});

export default router;
