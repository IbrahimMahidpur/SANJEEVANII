// NLP Processor for Outbreak News Articles
import { INDIAN_STATES, DISEASES } from './news-fetcher.js';

class NewsProcessor {
  constructor() {
    this.statePatterns = INDIAN_STATES.map(state => ({
      name: state,
      pattern: new RegExp(`\\b${state}\\b`, 'i')
    }));

    this.diseasePatterns = Object.entries(DISEASES).map(([name, keywords]) => ({
      name,
      pattern: new RegExp(`\\b(${keywords.join('|')})\\b`, 'i')
    }));
  }

  // Extract disease from text
  extractDisease(text) {
    for (const { name, pattern } of this.diseasePatterns) {
      if (pattern.test(text)) {
        return name;
      }
    }
    return null;
  }

  // Extract Indian state from text
  extractLocation(text) {
    for (const { name, pattern } of this.statePatterns) {
      if (pattern.test(text)) {
        return name;
      }
    }
    return null;
  }

  // Extract case count from text
  extractCaseCount(text) {
    // Patterns: "1500 cases", "over 2000 infected", "3,500 patients"
    const patterns = [
      /(\d+(?:,\d+)?)\s*(?:cases?|infections?|patients?|deaths?)/i,
      /(?:over|more than|around|about)\s*(\d+(?:,\d+)?)/i,
      /(\d+(?:,\d+)?)\s*(?:people|persons)\s*(?:infected|affected)/i
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        return parseInt(match[1].replace(/,/g, ''));
      }
    }

    return null;
  }

  // Determine severity from text and case count
  determineSeverity(text, caseCount) {
    const lowerText = text.toLowerCase();

    // Critical keywords
    if (/pandemic|catastrophic|emergency|crisis|severe outbreak|widespread/i.test(text)) {
      return 'Critical';
    }

    // High severity keywords
    if (/serious|alarming|surge|spike|rising|escalating|major outbreak/i.test(text)) {
      return 'High';
    }

    // Case count based severity
    if (caseCount) {
      if (caseCount > 5000) return 'Critical';
      if (caseCount > 1000) return 'High';
      if (caseCount > 100) return 'Medium';
    }

    // Default
    return 'Medium';
  }

  // Determine trend from text
  determineTrend(text) {
    const lowerText = text.toLowerCase();

    if (/increasing|rising|surge|spike|escalating|growing|spreading/i.test(text)) {
      return 'increasing';
    }

    if (/decreasing|declining|falling|dropping|subsiding|contained/i.test(text)) {
      return 'decreasing';
    }

    return 'stable';
  }

  // Calculate confidence score
  calculateConfidence(disease, location, caseCount, hasSource) {
    let score = 0;

    if (disease) score += 30;
    if (location) score += 40;
    if (caseCount) score += 20;
    if (hasSource) score += 10;

    return score;
  }

  // Process single article
  processArticle(article) {
    const text = `${article.title} ${article.description} ${article.content || ''}`;

    // Extract information
    const disease = article.disease || this.extractDisease(text);
    const location = this.extractLocation(text);
    const caseCount = this.extractCaseCount(text);
    const severity = this.determineSeverity(text, caseCount);
    const trend = this.determineTrend(text);
    const confidence = this.calculateConfidence(
      disease,
      location,
      caseCount,
      article.source?.name
    );

    // Only return if we have disease and location
    if (!disease || !location) {
      return null;
    }

    return {
      disease,
      location,
      caseCount,
      severity,
      trend,
      confidence,
      publishedAt: article.publishedAt,
      source: article.source?.name || 'Unknown',
      sourceUrl: article.url,
      title: article.title,
      description: article.description
    };
  }

  // Process multiple articles
  processArticles(articles) {
    console.log(`🔍 Processing ${articles.length} articles with NLP...`);

    const processed = articles
      .map(article => this.processArticle(article))
      .filter(result => result !== null && result.confidence >= 60);

    console.log(`✅ Extracted ${processed.length} valid outbreak alerts`);
    return processed;
  }

  // Deduplicate alerts (same disease + location)
  deduplicateAlerts(alerts) {
    const uniqueMap = new Map();

    for (const alert of alerts) {
      const key = `${alert.disease}-${alert.location}`;
      const existing = uniqueMap.get(key);

      if (!existing || alert.confidence > existing.confidence) {
        uniqueMap.set(key, alert);
      }
    }

    return Array.from(uniqueMap.values());
  }
}

export default new NewsProcessor();

// Export constants for use in other files
export { INDIAN_STATES, DISEASES };
