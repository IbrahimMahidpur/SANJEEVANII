// Real Outbreak Detector - Integrates News with Alert Generation
import newsFetcher from './news-fetcher.js';
import newsProcessor from './news-processor.js';
import { generateHistoricalAlerts } from './historical-data-generator.js';
import { v4 as uuidv4 } from 'uuid';

import fs from 'fs';

// Region coordinates (for map display)
const REGION_COORDS = {
  'Maharashtra': { lat: 19.7515, lon: 75.7139 },
  'Karnataka': { lat: 15.3173, lon: 75.7139 },
  'Tamil Nadu': { lat: 11.1271, lon: 78.6569 },
  'Uttar Pradesh': { lat: 26.8467, lon: 80.9462 },
  'Gujarat': { lat: 22.2587, lon: 71.1924 },
  'Rajasthan': { lat: 27.0238, lon: 74.2179 },
  'West Bengal': { lat: 22.9868, lon: 87.8550 },
  'Madhya Pradesh': { lat: 22.9734, lon: 78.6569 },
  'Delhi': { lat: 28.7041, lon: 77.1025 },
  'Kerala': { lat: 10.8505, lon: 76.2711 },
  'Punjab': { lat: 31.1471, lon: 75.3412 },
  'Haryana': { lat: 29.0588, lon: 76.0856 },
  'Bihar': { lat: 25.0961, lon: 85.3131 },
  'Odisha': { lat: 20.9517, lon: 85.0985 },
  'Telangana': { lat: 18.1124, lon: 79.0193 }
};

class RealOutbreakDetector {
  constructor() {
    this.alerts = [];
    this.historicalAlerts = this.prepareHistoricalData();
    this.lastUpdate = null;
  }

  // Prepare historical data with coordinates
  prepareHistoricalData() {
    const rawHistory = generateHistoricalAlerts(500); // Generate 500 past alerts for comprehensive coverage
    if (rawHistory.length > 0) {
      try {
        fs.writeFileSync('debug_log.json', JSON.stringify(rawHistory[0], null, 2));
      } catch (err) {
        console.error('Error writing debug log:', err);
      }
    }
    const mappedHistory = rawHistory.map(alert => {
      const coords = REGION_COORDS[alert.region] || { lat: 20.5937, lon: 78.9629 };
      return { ...alert, lat: coords.lat, lon: coords.lon };
    });
    if (mappedHistory.length > 0) {
      console.log('DEBUG: mappedHistory[0] weekly_trend:', mappedHistory[0].weekly_trend ? 'PRESENT' : 'MISSING');
    }
    return mappedHistory;
  }

  // Generate alert from processed news
  createAlertFromNews(newsData) {
    const coords = REGION_COORDS[newsData.location] || { lat: 20.5937, lon: 78.9629 };

    // Simulate realistic weekly trend based on the news trend
    let weekly_trend = [];
    const baseValue = newsData.caseCount > 0 ? newsData.caseCount : (newsData.confidence * 0.5); // Fallback if no case count

    if (newsData.trend === 'increasing') {
      for (let i = 6; i >= 0; i--) weekly_trend.push(Math.max(0, Math.round(baseValue * Math.pow(0.85, i))));
    } else if (newsData.trend === 'decreasing') {
      for (let i = 6; i >= 0; i--) weekly_trend.push(Math.max(0, Math.round(baseValue * Math.pow(1.15, i))));
    } else {
      for (let i = 0; i < 7; i++) weekly_trend.push(Math.max(0, Math.round(baseValue + (Math.random() * baseValue * 0.1 - baseValue * 0.05))));
    }

    return {
      alert_id: uuidv4(),
      created_at: newsData.publishedAt || new Date().toISOString(),
      disease: newsData.disease,
      region: newsData.location,
      lat: coords.lat,
      lon: coords.lon,
      severity: newsData.severity,
      status: 'open',
      case_count: newsData.caseCount || 0,
      trend: newsData.trend,
      confidence: newsData.confidence,
      source: newsData.source,
      source_url: newsData.sourceUrl,
      sources: [{
        name: newsData.source,
        url: newsData.sourceUrl,
        type: 'news',
        published_at: newsData.publishedAt || new Date().toISOString()
      }],
      title: newsData.title,
      description: newsData.description,
      metric: 'news_based',
      value: newsData.confidence / 100 * 5, // Convert confidence to Z-score-like value
      expected: 0,
      weekly_trend: weekly_trend
    };
  }

  // Update alerts from news sources
  async updateFromNews() {
    try {
      console.log('🔄 Updating outbreak alerts from real news sources...');

      // Fetch articles
      const articles = await newsFetcher.getArticles();

      // Process with NLP
      const processedNews = newsProcessor.processArticles(articles);

      // Deduplicate
      const uniqueNews = newsProcessor.deduplicateAlerts(processedNews);

      // Convert to alerts
      const newAlerts = uniqueNews.map(news => this.createAlertFromNews(news));

      // Merge with existing alerts (update or add)
      for (const newAlert of newAlerts) {
        const existingIndex = this.alerts.findIndex(
          a => a.disease === newAlert.disease && a.region === newAlert.region
        );

        if (existingIndex >= 0) {
          // Update existing alert
          this.alerts[existingIndex] = {
            ...this.alerts[existingIndex],
            ...newAlert,
            alert_id: this.alerts[existingIndex].alert_id // Keep original ID
          };
        } else {
          // Add new alert
          this.alerts.push(newAlert);
        }
      }

      this.lastUpdate = new Date();
      console.log(`✅ Updated ${this.alerts.length} real outbreak alerts`);

      return this.alerts;
    } catch (error) {
      console.error('❌ Error updating from news:', error);
      return this.alerts;
    }
  }

  // Get alerts with filters
  getAlerts(filters = {}) {
    // Merge real and historical alerts
    let results = [...this.alerts, ...this.historicalAlerts];

    if (filters.disease) {
      results = results.filter(a => a.disease === filters.disease);
    }

    if (filters.region) {
      results = results.filter(a => a.region === filters.region);
    }

    if (filters.severity) {
      results = results.filter(a => a.severity === filters.severity);
    }

    if (filters.status) {
      results = results.filter(a => a.status === filters.status);
    }

    if (filters.startDate) {
      const startDate = new Date(filters.startDate);
      // console.log(`🔍 Filtering: ${results.length} alerts >= ${startDate.toISOString()}`);
      results = results.filter(a => new Date(a.created_at) >= startDate);
    }

    if (filters.endDate) {
      const endDate = new Date(filters.endDate);
      results = results.filter(a => new Date(a.created_at) <= endDate);
    }

    // Sort alerts by date (newest first)
    if (filters.startDate || filters.endDate || !filters.status) {
      results.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    }

    if (results.length > 0) {
      console.log('DEBUG: First alert in getAlerts:', JSON.stringify(results[0], null, 2));
    }

    return results;
  }

  // Get statistics
  getStatistics() {
    const allAlerts = [...this.alerts, ...this.historicalAlerts];
    const stats = {
      total: allAlerts.length,
      by_severity: {},
      by_disease: {},
      by_status: {}
    };

    for (const alert of allAlerts) {
      stats.by_severity[alert.severity] = (stats.by_severity[alert.severity] || 0) + 1;
      stats.by_disease[alert.disease] = (stats.by_disease[alert.disease] || 0) + 1;
      stats.by_status[alert.status] = (stats.by_status[alert.status] || 0) + 1;
    }

    return stats;
  }

  // Start auto-refresh (every 15 minutes)
  startAutoRefresh() {
    console.log('🚀 Starting real outbreak detector with auto-refresh...');

    // Initial fetch
    this.updateFromNews();

    // Refresh every 15 minutes
    this.refreshInterval = setInterval(() => {
      this.updateFromNews();
    }, 15 * 60 * 1000);
  }

  stopAutoRefresh() {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
      console.log('⏹️ Stopped auto-refresh');
    }
  }
}

export default new RealOutbreakDetector();
