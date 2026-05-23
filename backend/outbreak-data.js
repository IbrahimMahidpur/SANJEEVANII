// Realistic Outbreak Data Generator - Senior Developer Implementation
import { randomInt, randomFloat } from './utils.js';

// Indian states with coordinates and population
const REGIONS = [
  { name: 'Maharashtra', lat: 19.7515, lon: 75.7139, population: 112374333 },
  { name: 'Karnataka', lat: 15.3173, lon: 75.7139, population: 61095297 },
  { name: 'Tamil Nadu', lat: 11.1271, lon: 78.6569, population: 72147030 },
  { name: 'Uttar Pradesh', lat: 26.8467, lon: 80.9462, population: 199812341 },
  { name: 'Gujarat', lat: 22.2587, lon: 71.1924, population: 60439692 },
  { name: 'Rajasthan', lat: 27.0238, lon: 74.2179, population: 68548437 },
  { name: 'West Bengal', lat: 22.9868, lon: 87.8550, population: 91276115 },
  { name: 'Madhya Pradesh', lat: 22.9734, lon: 78.6569, population: 72626809 },
  { name: 'Delhi', lat: 28.7041, lon: 77.1025, population: 16787941 },
  { name: 'Kerala', lat: 10.8505, lon: 76.2711, population: 33406061 },
  { name: 'Punjab', lat: 31.1471, lon: 75.3412, population: 27743338 },
  { name: 'Haryana', lat: 29.0588, lon: 76.0856, population: 25351462 },
  { name: 'Bihar', lat: 25.0961, lon: 85.3131, population: 104099452 },
  { name: 'Odisha', lat: 20.9517, lon: 85.0985, population: 41974218 },
  { name: 'Telangana', lat: 18.1124, lon: 79.0193, population: 35193978 },
];

// Disease types with seasonal patterns
const DISEASES = [
  {
    name: 'Influenza',
    baseRate: 50,
    seasonalPeak: [11, 12, 1, 2], // Winter
    variance: 20
  },
  {
    name: 'Dengue',
    baseRate: 30,
    seasonalPeak: [7, 8, 9, 10], // Monsoon
    variance: 15
  },
  {
    name: 'Cholera',
    baseRate: 10,
    seasonalPeak: [6, 7, 8], // Rainy season
    variance: 8
  },
  {
    name: 'COVID-19',
    baseRate: 100,
    seasonalPeak: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], // Year-round
    variance: 40
  },
  {
    name: 'Malaria',
    baseRate: 25,
    seasonalPeak: [7, 8, 9], // Monsoon
    variance: 12
  },
  {
    name: 'Typhoid',
    baseRate: 15,
    seasonalPeak: [6, 7, 8, 9], // Summer/Monsoon
    variance: 10
  },
];

// Outbreak lifecycle stages
const OUTBREAK_STAGES = {
  EMERGING: { minMultiplier: 2.0, maxMultiplier: 4.0, severity: 'Medium', trend: 'increasing' },
  ESCALATING: { minMultiplier: 4.0, maxMultiplier: 7.0, severity: 'High', trend: 'increasing' },
  PEAK: { minMultiplier: 7.0, maxMultiplier: 12.0, severity: 'Critical', trend: 'stable' },
  DECLINING: { minMultiplier: 3.0, maxMultiplier: 7.0, severity: 'High', trend: 'decreasing' },
  RESOLVING: { minMultiplier: 1.5, maxMultiplier: 3.0, severity: 'Medium', trend: 'decreasing' },
  RESOLVED: { minMultiplier: 0.5, maxMultiplier: 1.5, severity: 'Low', trend: 'stable' }
};

// Outbreak events (mock data - will be replaced by real news)
const OUTBREAK_EVENTS = [];

class OutbreakDataGenerator {
  constructor() {
    this.dailyCounts = [];
    this.generateHistoricalData();
  }

  getCurrentMonth() {
    return new Date().getMonth() + 1;
  }

  isSeasonalPeak(disease, month) {
    return disease.seasonalPeak.includes(month);
  }

  generateBaseCaseCount(disease, region, date) {
    const month = date.getMonth() + 1;
    const isPeak = this.isSeasonalPeak(disease, month);

    const populationFactor = region.population / 100000000;
    let baseCount = disease.baseRate * populationFactor;

    if (isPeak) {
      baseCount *= 1.5 + Math.random() * 0.5;
    }

    const variance = (Math.random() - 0.5) * disease.variance;
    baseCount += variance;

    return Math.max(0, Math.round(baseCount));
  }

  // REALISTIC outbreak event application with lifecycle stages
  applyOutbreakEvent(caseCount, disease, region, date) {
    const now = new Date();

    for (const outbreak of OUTBREAK_EVENTS) {
      if (outbreak.disease === disease.name && outbreak.region === region.name) {
        // Calculate outbreak start time
        let outbreakStartTime;
        if (outbreak.startHours !== undefined) {
          outbreakStartTime = new Date(now.getTime() - (outbreak.startHours * -1 * 60 * 60 * 1000));
        } else if (outbreak.startDays !== undefined) {
          outbreakStartTime = new Date(now.getTime() - (outbreak.startDays * -1 * 24 * 60 * 60 * 1000));
        } else {
          continue;
        }

        const outbreakEndTime = new Date(outbreakStartTime.getTime() + (outbreak.duration * 24 * 60 * 60 * 1000));

        if (date >= outbreakStartTime && date <= outbreakEndTime) {
          // Calculate progress through outbreak (0 to 1)
          const totalDuration = outbreakEndTime - outbreakStartTime;
          const elapsed = date - outbreakStartTime;
          const progress = elapsed / totalDuration;

          // Apply bell curve for realistic progression
          const bellCurve = Math.sin(progress * Math.PI);
          const multiplier = 1 + (outbreak.multiplier - 1) * bellCurve;

          return Math.round(caseCount * multiplier);
        }
      }
    }

    return caseCount;
  }

  generateHistoricalData() {
    const today = new Date();
    const daysToGenerate = 90;

    for (let i = daysToGenerate; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);

      for (const disease of DISEASES) {
        for (const region of REGIONS) {
          let confirmedCases = this.generateBaseCaseCount(disease, region, date);
          confirmedCases = this.applyOutbreakEvent(confirmedCases, disease, region, date);

          const suspectedCases = Math.round(confirmedCases * (1.5 + Math.random() * 0.5));
          const tests = Math.round(suspectedCases * (2 + Math.random()));
          const casesPer100k = (confirmedCases / region.population) * 100000;

          this.dailyCounts.push({
            date: date.toISOString().split('T')[0],
            disease: disease.name,
            region: region.name,
            confirmed_cases: confirmedCases,
            suspected_cases: suspectedCases,
            tests: tests,
            population: region.population,
            cases_per_100k: parseFloat(casesPer100k.toFixed(2)),
          });
        }
      }
    }

    console.log(`✅ Generated ${this.dailyCounts.length} historical data points with realistic time distribution`);
  }

  getDailyCounts(filters = {}) {
    let results = [...this.dailyCounts];

    if (filters.disease) {
      results = results.filter(d => d.disease === filters.disease);
    }

    if (filters.region) {
      results = results.filter(d => d.region === filters.region);
    }

    if (filters.startDate) {
      results = results.filter(d => d.date >= filters.startDate);
    }

    if (filters.endDate) {
      results = results.filter(d => d.date <= filters.endDate);
    }

    return results;
  }

  getRegions() {
    return REGIONS;
  }

  getDiseases() {
    return DISEASES.map(d => d.name);
  }

  getLatestCounts() {
    const latest = {};

    for (const count of this.dailyCounts) {
      const key = `${count.disease}-${count.region}`;
      if (!latest[key] || count.date > latest[key].date) {
        latest[key] = count;
      }
    }

    return Object.values(latest);
  }

  // Get outbreak start time for alert timestamp
  getOutbreakStartTime(disease, region) {
    const now = new Date();

    for (const outbreak of OUTBREAK_EVENTS) {
      if (outbreak.disease === disease && outbreak.region === region) {
        // Prefer explicit start time if available
        if (outbreak.startTime) {
          return new Date(outbreak.startTime);
        }

        // Fallback to relative time (fixed calculation)
        if (outbreak.startHours !== undefined) {
          return new Date(now.getTime() - (outbreak.startHours * 60 * 60 * 1000));
        } else if (outbreak.startDays !== undefined) {
          return new Date(now.getTime() - (outbreak.startDays * 24 * 60 * 60 * 1000));
        }
      }
    }

    return now; // Default to now if no outbreak found
  }

  // ========== DYNAMIC DATA ENGINE ==========

  startDynamicEngine() {
    console.log('🚀 Starting Realistic Dynamic Data Engine...');
    console.log('📊 Generating new data every 30 seconds with lifecycle progression');

    this.dataInterval = setInterval(() => {
      this.generateLiveDataPoint();
      this.evolveOutbreaks();
      this.trySpawnNewOutbreak();
      this.cleanupOldData();
    }, 30000);
  }

  generateLiveDataPoint() {
    const now = new Date();
    const today = now.toISOString().split('T')[0];

    console.log(`🔄 Generating live data point for ${today} ${now.toLocaleTimeString('en-IN')}`);

    let newPointsCount = 0;

    for (const disease of DISEASES) {
      for (const region of REGIONS) {
        const existingToday = this.dailyCounts.find(
          d => d.date === today && d.disease === disease.name && d.region === region.name
        );

        if (!existingToday) {
          const caseCount = this.generateBaseCaseCount(disease, region, now);
          const outbreakAffected = this.applyOutbreakEvent(caseCount, disease, region, now);

          const variation = 0.85 + Math.random() * 0.3;
          const finalCount = Math.round(outbreakAffected * variation);

          this.dailyCounts.push({
            date: today,
            disease: disease.name,
            region: region.name,
            confirmed_cases: finalCount,
            lat: region.lat,
            lon: region.lon,
            population: region.population,
            cases_per_100k: (finalCount / region.population) * 100000,
          });

          newPointsCount++;
        }
      }
    }

    console.log(`✅ Generated ${newPointsCount} new data points`);
  }

  evolveOutbreaks() {
    let evolved = 0;

    for (const outbreak of OUTBREAK_EVENTS) {
      // Realistic evolution based on stage
      const stage = OUTBREAK_STAGES[outbreak.stage];
      if (!stage) continue;

      const change = 0.85 + Math.random() * 0.3; // ±15%
      outbreak.multiplier *= change;

      // Keep within stage bounds
      if (outbreak.multiplier > stage.maxMultiplier) {
        outbreak.multiplier = stage.maxMultiplier;
      }
      if (outbreak.multiplier < stage.minMultiplier) {
        outbreak.multiplier = stage.minMultiplier;
      }

      // Progress to next stage if appropriate
      if (outbreak.multiplier >= OUTBREAK_STAGES.PEAK.minMultiplier && outbreak.stage === 'ESCALATING') {
        outbreak.stage = 'PEAK';
        console.log(`📈 Outbreak escalated to PEAK: ${outbreak.disease} in ${outbreak.region}`);
      } else if (outbreak.multiplier < OUTBREAK_STAGES.DECLINING.maxMultiplier && outbreak.stage === 'PEAK') {
        outbreak.stage = 'DECLINING';
        console.log(`📉 Outbreak declining: ${outbreak.disease} in ${outbreak.region}`);
      } else if (outbreak.multiplier < OUTBREAK_STAGES.RESOLVING.maxMultiplier && outbreak.stage === 'DECLINING') {
        outbreak.stage = 'RESOLVING';
        console.log(`🔽 Outbreak resolving: ${outbreak.disease} in ${outbreak.region}`);
      } else if (outbreak.multiplier < OUTBREAK_STAGES.RESOLVED.maxMultiplier && outbreak.stage === 'RESOLVING') {
        outbreak.stage = 'RESOLVED';
        outbreak.resolving = true;
        console.log(`✅ Outbreak resolved: ${outbreak.disease} in ${outbreak.region}`);
      }

      evolved++;
    }

    const beforeCount = OUTBREAK_EVENTS.length;
    OUTBREAK_EVENTS.splice(0, OUTBREAK_EVENTS.length,
      ...OUTBREAK_EVENTS.filter(o => !o.resolving)
    );
    const resolved = beforeCount - OUTBREAK_EVENTS.length;

    if (resolved > 0) {
      console.log(`✅ ${resolved} outbreak(s) fully resolved and removed`);
    }
  }

  trySpawnNewOutbreak() {
    if (Math.random() < 0.05) {
      const randomDisease = DISEASES[Math.floor(Math.random() * DISEASES.length)].name;
      const randomRegion = REGIONS[Math.floor(Math.random() * REGIONS.length)].name;

      const exists = OUTBREAK_EVENTS.find(
        o => o.disease === randomDisease && o.region === randomRegion
      );

      if (!exists) {
        const newOutbreak = {
          disease: randomDisease,
          region: randomRegion,
          startHours: 0,
          duration: 7 + Math.floor(Math.random() * 8),
          multiplier: 2.5 + Math.random() * 1.5,
          stage: 'EMERGING',
          startTime: new Date() // Store precise start time
        };

        OUTBREAK_EVENTS.push(newOutbreak);
        console.log(`🆕 New outbreak emerging: ${randomDisease} in ${randomRegion} (${newOutbreak.multiplier.toFixed(1)}x)`);
      }
    }
  }

  cleanupOldData() {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 90);
    const cutoff = cutoffDate.toISOString().split('T')[0];

    const beforeCount = this.dailyCounts.length;
    this.dailyCounts = this.dailyCounts.filter(d => d.date >= cutoff);
    const removed = beforeCount - this.dailyCounts.length;

    if (removed > 0) {
      console.log(`🗑️ Cleaned up ${removed} old data points`);
    }
  }

  stopDynamicEngine() {
    if (this.dataInterval) {
      clearInterval(this.dataInterval);
      console.log('⏹️ Dynamic Data Engine stopped');
    }
  }
}

const outbreakData = new OutbreakDataGenerator();
outbreakData.startDynamicEngine();

export default outbreakData;
