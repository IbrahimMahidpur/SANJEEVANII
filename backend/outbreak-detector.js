// Outbreak anomaly detection engine using Z-score algorithm
import outbreakData from './outbreak-data.js';
import { calculateMean, calculateStdDev, calculateZScore, generateUUID } from './utils.js';
import { generateHistoricalAlerts } from './historical-data-generator.js';

class OutbreakDetector {
  constructor() {
    this.alerts = [];
    this.detectionThreshold = 1.5; // Base threshold
    this.rollingWindowDays = 7;
    this.initializeHistoricalAlerts();
  }

  // Initialize with historical alerts for time range filtering
  initializeHistoricalAlerts() {
    console.log('📊 Generating historical outbreak alerts...');
    const historicalAlerts = generateHistoricalAlerts(250);

    // Add coordinates from regions
    const regions = outbreakData.getRegions();
    const regionMap = new Map(regions.map(r => [r.name, r]));

    this.alerts = historicalAlerts.map(alert => {
      const region = regionMap.get(alert.region);
      return {
        ...alert,
        lat: region?.lat || 20.5937,
        lon: region?.lon || 78.9629
      };
    });

    console.log(`✅ Initialized with ${this.alerts.length} historical alerts`);
    console.log(`   - Last hour: ${this.alerts.filter(a => this.isWithinHours(a.created_at, 1)).length}`);
    console.log(`   - Last day: ${this.alerts.filter(a => this.isWithinHours(a.created_at, 24)).length}`);
    console.log(`   - Last week: ${this.alerts.filter(a => this.isWithinDays(a.created_at, 7)).length}`);
    console.log(`   - Last month: ${this.alerts.filter(a => this.isWithinDays(a.created_at, 30)).length}`);
    console.log(`   - Last year: ${this.alerts.filter(a => this.isWithinDays(a.created_at, 365)).length}`);
  }

  // Helper: Check if date is within N hours
  isWithinHours(dateStr, hours) {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;
    return diff >= 0 && diff <= hours * 60 * 60 * 1000;
  }

  // Helper: Check if date is within N days
  isWithinDays(dateStr, days) {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;
    return diff >= 0 && diff <= days * 24 * 60 * 60 * 1000;
  }

  // Calculate rolling statistics
  calculateRollingStats(disease, region, endDate) {
    const end = new Date(endDate);
    const start = new Date(end);
    start.setDate(start.getDate() - this.rollingWindowDays);

    const historicalData = outbreakData.getDailyCounts({
      disease,
      region,
      startDate: start.toISOString().split('T')[0],
      endDate: end.toISOString().split('T')[0],
    });

    if (historicalData.length === 0) {
      return null;
    }

    const caseCounts = historicalData.map(d => d.confirmed_cases);
    const mean = calculateMean(caseCounts);
    const stdDev = calculateStdDev(caseCounts);

    return { mean, stdDev, historicalData };
  }

  // REALISTIC severity classification (adjusted for Critical alerts)
  classifySeverity(zScore) {
    if (zScore >= 5.0) return 'Critical';  // Extreme anomaly (PEAK stage outbreaks)
    if (zScore >= 3.5) return 'High';      // Significant anomaly (ESCALATING/PEAK)
    if (zScore >= 2.0) return 'Medium';    // Notable anomaly (EMERGING/ESCALATING)
    if (zScore >= 1.5) return 'Low';       // Minor anomaly (EMERGING)
    return 'Normal';
  }

  // Determine trend based on recent data
  determineTrend(historicalData) {
    if (historicalData.length < 3) return 'stable';

    const recent = historicalData.slice(-3).map(d => d.confirmed_cases);
    const older = historicalData.slice(-6, -3).map(d => d.confirmed_cases);

    if (older.length === 0) return 'stable';

    const recentAvg = calculateMean(recent);
    const olderAvg = calculateMean(older);

    const change = (recentAvg - olderAvg) / olderAvg;

    if (change > 0.2) return 'increasing';
    if (change < -0.2) return 'decreasing';
    return 'stable';
  }

  // Run detection for all disease-region combinations
  runDetection() {
    const diseases = outbreakData.getDiseases();
    const regions = outbreakData.getRegions();
    const today = new Date().toISOString().split('T')[0];

    const newAlerts = [];

    for (const disease of diseases) {
      for (const region of regions) {
        const stats = this.calculateRollingStats(disease, region.name, today);

        if (!stats || stats.stdDev === 0) continue;

        // Get today's count
        const todayData = outbreakData.getDailyCounts({
          disease,
          region: region.name,
          startDate: today,
          endDate: today,
        });

        if (todayData.length === 0) continue;

        const todayCount = todayData[0].confirmed_cases;
        const zScore = calculateZScore(todayCount, stats.mean, stats.stdDev);

        // Check if anomaly detected
        if (zScore >= this.detectionThreshold) {
          const severity = this.classifySeverity(zScore);
          const trend = this.determineTrend(stats.historicalData);

          // FIX: Use outbreak start time for realistic time filtering
          const outbreakStartTime = outbreakData.getOutbreakStartTime(disease, region.name);

          // Generate realistic sources
          const sources = [];

          // 1. Government Source (MOHFW or State Health Dept)
          const stateHealthUrl = `https://${region.name.toLowerCase().replace(/\s+/g, '')}.gov.in/health`;
          sources.push({
            name: `${region.name} State Health Department`,
            url: stateHealthUrl,
            type: 'government',
            published_at: outbreakStartTime.toISOString()
          });

          // 2. National Source (sometimes)
          if (Math.random() > 0.3) {
            sources.push({
              name: 'Ministry of Health & Family Welfare',
              url: 'https://www.mohfw.gov.in/',
              type: 'government',
              published_at: outbreakStartTime.toISOString()
            });
          }

          // 3. News Source
          const newsSources = [
            { name: 'The Hindu', url: 'https://www.thehindu.com/news/national/' },
            { name: 'Times of India', url: 'https://timesofindia.indiatimes.com/india/' },
            { name: 'NDTV', url: 'https://www.ndtv.com/india-news/' },
            { name: 'ANI News', url: 'https://www.aninews.in/' }
          ];
          const news = newsSources[Math.floor(Math.random() * newsSources.length)];
          sources.push({
            name: news.name,
            url: `${news.url}${disease.toLowerCase()}-outbreak-${region.name.toLowerCase().replace(/\s+/g, '-')}`,
            type: 'news',
            published_at: outbreakStartTime.toISOString()
          });

          // 4. International Source (for major diseases)
          if (['COVID-19', 'Influenza', 'Cholera'].includes(disease) && Math.random() > 0.5) {
            sources.push({
              name: 'WHO India',
              url: 'https://www.who.int/india/health-topics/' + disease.toLowerCase(),
              type: 'who',
              published_at: outbreakStartTime.toISOString()
            });
          }

          // Generate weekly trend data
          const weeklyTrend = [];
          let currentVal = todayCount;
          for (let i = 0; i < 7; i++) {
            weeklyTrend.unshift(Math.max(0, Math.round(currentVal)));
            if (trend === 'increasing') currentVal *= (0.8 + Math.random() * 0.1);
            else if (trend === 'decreasing') currentVal *= (1.1 + Math.random() * 0.1);
            else currentVal *= (0.9 + Math.random() * 0.2);
          }

          const alert = {
            alert_id: generateUUID(),
            created_at: outbreakStartTime.toISOString(), // Use outbreak start, not detection time
            disease,
            region: region.name,
            lat: region.lat,
            lon: region.lon,
            window_start: stats.historicalData[0].date,
            window_end: today,
            metric: 'zscore',
            value: parseFloat(zScore.toFixed(2)),
            expected: parseFloat(stats.mean.toFixed(2)),
            severity,
            status: 'open',
            case_count: todayCount,
            trend,
            weekly_trend: weeklyTrend,
            sources: sources
          };

          newAlerts.push(alert);
        }
      }
    }

    // Add new alerts to the list
    this.alerts = [...this.alerts, ...newAlerts];

    // Remove duplicates (keep latest)
    const alertMap = new Map();
    for (const alert of this.alerts) {
      const key = `${alert.disease}-${alert.region}`;
      if (!alertMap.has(key) || alert.created_at > alertMap.get(key).created_at) {
        alertMap.set(key, alert);
      }
    }

    this.alerts = Array.from(alertMap.values());

    console.log(`🚨 Detection complete: ${newAlerts.length} new alerts, ${this.alerts.length} total active`);

    return newAlerts;
  }

  // Get all alerts with filters
  getAlerts(filters = {}) {
    let results = [...this.alerts];

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
      results = results.filter(a => a.created_at >= filters.startDate);
    }

    if (filters.endDate) {
      results = results.filter(a => a.created_at <= filters.endDate);
    }

    // Sort by severity and date
    const severityOrder = { 'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1 };
    results.sort((a, b) => {
      const severityDiff = severityOrder[b.severity] - severityOrder[a.severity];
      if (severityDiff !== 0) return severityDiff;
      return new Date(b.created_at) - new Date(a.created_at);
    });

    return results;
  }

  // Update alert status
  updateAlertStatus(alertId, status) {
    const alert = this.alerts.find(a => a.alert_id === alertId);
    if (alert) {
      alert.status = status;
      alert.updated_at = new Date().toISOString();
      return alert;
    }
    return null;
  }

  // Get alert statistics
  getStatistics() {
    const stats = {
      total: this.alerts.length,
      by_severity: {},
      by_disease: {},
      by_status: {},
    };

    for (const alert of this.alerts) {
      // By severity
      stats.by_severity[alert.severity] = (stats.by_severity[alert.severity] || 0) + 1;

      // By disease
      stats.by_disease[alert.disease] = (stats.by_disease[alert.disease] || 0) + 1;

      // By status
      stats.by_status[alert.status] = (stats.by_status[alert.status] || 0) + 1;
    }

    return stats;
  }

  // ========== CONTINUOUS DETECTION ENGINE ==========

  // Start continuous detection (runs every 30 seconds)
  startContinuousDetection() {
    console.log('🔍 Starting Continuous Detection Engine...');
    console.log('⚡ Running detection every 30 seconds');

    // Run detection every 30 seconds
    this.detectionInterval = setInterval(() => {
      this.updateExistingAlerts();
      this.runDetection();
      this.autoResolveAlerts();
    }, 30000); // 30 seconds
  }

  // Update existing alerts with latest data
  updateExistingAlerts() {
    const today = new Date().toISOString().split('T')[0];
    let updated = 0;
    let severityChanged = 0;

    for (const alert of this.alerts) {
      if (alert.status !== 'open') continue;

      // Recalculate stats for this alert
      const stats = this.calculateRollingStats(alert.disease, alert.region, today);

      if (!stats || stats.stdDev === 0) continue;

      // Get today's count
      const todayData = outbreakData.getDailyCounts({
        disease: alert.disease,
        region: alert.region,
        startDate: today,
        endDate: today,
      });

      if (todayData.length === 0) continue;

      const todayCount = todayData[0].confirmed_cases;
      const newZScore = calculateZScore(todayCount, stats.mean, stats.stdDev);
      const newSeverity = this.classifySeverity(newZScore);
      const newTrend = this.determineTrend(stats.historicalData);

      // Check if severity changed
      if (newSeverity !== alert.severity) {
        console.log(`📊 Severity changed: ${alert.disease} in ${alert.region} (${alert.severity} → ${newSeverity})`);
        severityChanged++;
      }

      // Update alert
      alert.value = parseFloat(newZScore.toFixed(2));
      alert.severity = newSeverity;
      alert.trend = newTrend;
      alert.case_count = todayCount;
      alert.expected = parseFloat(stats.mean.toFixed(2));
      alert.cases_per_100k = todayData[0].cases_per_100k;
      alert.updated_at = new Date().toISOString();

      updated++;
    }

    if (updated > 0) {
      console.log(`🔄 Updated ${updated} alert(s), ${severityChanged} severity change(s)`);
    }
  }

  // REALISTIC auto-resolve with multi-factor checking
  autoResolveAlerts() {
    const today = new Date().toISOString().split('T')[0];
    let resolved = 0;

    for (const alert of this.alerts) {
      if (alert.status !== 'open') continue;

      // Multi-factor resolution logic
      const daysSinceCreation = Math.floor(
        (new Date() - new Date(alert.created_at)) / (1000 * 60 * 60 * 24)
      );

      const factors = {
        zScoreNormalized: alert.value < 1.5,
        casesDecreasing: alert.trend === 'decreasing',
        durationExceeded: daysSinceCreation > 14,
        belowBaseline: alert.case_count < alert.expected * 1.2
      };

      const trueCount = Object.values(factors).filter(Boolean).length;

      // Resolve if 2 out of 4 factors are true (more lenient)
      if (trueCount >= 2) {
        alert.status = 'resolved';
        alert.resolved_at = new Date().toISOString();
        console.log(`✅ Auto-resolved: ${alert.disease} in ${alert.region} (${trueCount}/4 factors met)`);
        resolved++;
      }
    }

    if (resolved > 0) {
      console.log(`✅ Auto-resolved ${resolved} alert(s) based on multi-factor analysis`);
    }
  }

  // Stop continuous detection
  stopContinuousDetection() {
    if (this.detectionInterval) {
      clearInterval(this.detectionInterval);
      console.log('⏹️ Continuous Detection Engine stopped');
    }
  }
}

// Singleton instance
const detector = new OutbreakDetector();

// Run initial detection
detector.runDetection();

// Start continuous detection
detector.startContinuousDetection();

export default detector;
