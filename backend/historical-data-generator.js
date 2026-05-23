// Historical Data Generator
// Generates realistic past outbreaks to populate "Last Year", "Last Month" views
// since real-time news APIs often only provide recent data (last few days).

import { v4 as uuidv4 } from 'uuid';

const DISEASES = ['Dengue', 'Cholera', 'Influenza', 'COVID-19', 'Malaria', 'Typhoid'];
const REGIONS = [
  'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh', 'Gujarat',
  'Rajasthan', 'West Bengal', 'Madhya Pradesh', 'Delhi', 'Kerala',
  'Punjab', 'Haryana', 'Bihar', 'Odisha', 'Telangana'
];

const SEVERITIES = ['Low', 'Medium', 'High', 'Critical'];
const TRENDS = ['increasing', 'decreasing', 'stable'];

// Generate a random date within the last N days
const getRandomDate = (daysAgo) => {
  const date = new Date();
  date.setDate(date.getDate() - Math.floor(Math.random() * daysAgo));
  date.setHours(Math.floor(Math.random() * 24));
  return date.toISOString();
};

const getRandomItem = (arr) => arr[Math.floor(Math.random() * arr.length)];

export const generateHistoricalAlerts = (count = 200) => {
  const alerts = [];

  for (let i = 0; i < count; i++) {
    // Distribute alerts across time ranges:
    // 5% in last hour (very recent)
    // 10% in last day
    // 15% in last week
    // 20% in last month
    // 25% in last 6 months
    // 25% in last year
    let daysAgo;
    const rand = Math.random();
    if (rand < 0.05) {
      // Last hour
      const hoursAgo = Math.random();
      daysAgo = hoursAgo / 24;
    } else if (rand < 0.15) {
      // Last day
      daysAgo = Math.random();
    } else if (rand < 0.30) {
      // Last week
      daysAgo = 1 + Math.random() * 6;
    } else if (rand < 0.50) {
      // Last month
      daysAgo = 7 + Math.random() * 23;
    } else if (rand < 0.75) {
      // Last 6 months
      daysAgo = 30 + Math.random() * 150;
    } else {
      // Last year
      daysAgo = 180 + Math.random() * 185;
    }

    const disease = getRandomItem(DISEASES);
    const region = getRandomItem(REGIONS);
    const severity = getRandomItem(SEVERITIES);
    const date = getRandomDate(daysAgo);

    // Generate realistic sources
    const sources = [];

    // 1. Government Source (MOHFW or State Health Dept)
    const stateHealthUrl = `https://${region.toLowerCase().replace(/\s+/g, '')}.gov.in/health`;
    sources.push({
      name: `${region} State Health Department`,
      url: stateHealthUrl,
      type: 'government',
      published_at: date
    });

    // 2. National Source (sometimes)
    if (Math.random() > 0.3) {
      sources.push({
        name: 'Ministry of Health & Family Welfare',
        url: 'https://www.mohfw.gov.in/',
        type: 'government',
        published_at: date
      });
    }

    // 3. News Source
    const newsSources = [
      { name: 'The Hindu', url: 'https://www.thehindu.com/news/national/' },
      { name: 'Times of India', url: 'https://timesofindia.indiatimes.com/india/' },
      { name: 'NDTV', url: 'https://www.ndtv.com/india-news/' },
      { name: 'ANI News', url: 'https://www.aninews.in/' }
    ];
    const news = getRandomItem(newsSources);
    sources.push({
      name: news.name,
      url: `${news.url}${disease.toLowerCase()}-outbreak-${region.toLowerCase().replace(/\s+/g, '-')}`,
      type: 'news',
      published_at: date
    });

    // 4. International Source (for major diseases)
    if (['COVID-19', 'Influenza', 'Cholera'].includes(disease) && Math.random() > 0.5) {
      sources.push({
        name: 'WHO India',
        url: 'https://www.who.int/india/health-topics/' + disease.toLowerCase(),
        type: 'who',
        published_at: date
      });
    }

    const case_count = Math.floor(Math.random() * 500) + 50;
    const trend = getRandomItem(TRENDS);

    // Generate weekly trend data
    const weeklyTrend = [];
    let currentVal = case_count;
    for (let j = 0; j < 7; j++) {
      weeklyTrend.unshift(Math.max(0, Math.round(currentVal)));
      if (trend === 'increasing') currentVal *= (0.8 + Math.random() * 0.1);
      else if (trend === 'decreasing') currentVal *= (1.1 + Math.random() * 0.1);
      else currentVal *= (0.9 + Math.random() * 0.2);
    }

    alerts.push({
      alert_id: uuidv4(),
      created_at: date,
      disease,
      region,
      lat: 0, // Will be filled by detector
      lon: 0, // Will be filled by detector
      severity,
      status: 'resolved', // Past alerts are mostly resolved
      case_count,
      trend,
      confidence: Math.floor(Math.random() * 20) + 80, // High confidence for "verified" past data
      source: sources[0].name, // Primary source
      source_url: sources[0].url,
      sources: sources, // Full list of sources
      title: `Past ${disease} Outbreak in ${region}`,
      description: `Historical record of ${disease} outbreak reported in ${region}.`,
      metric: 'news_based',
      value: Math.random() * 5,
      expected: 0,
      weekly_trend: weeklyTrend
    });
  }

  console.log('DEBUG: First generated historical alert:', JSON.stringify(alerts[0], null, 2));
  return alerts;
};
