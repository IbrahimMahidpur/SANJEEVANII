// Real Outbreak News Fetcher - Google News RSS + News API Support
import Parser from 'rss-parser';
import axios from 'axios';

const parser = new Parser({
  customFields: {
    item: ['pubDate', 'link', 'title', 'description']
  }
});

// Indian states for location detection
export const INDIAN_STATES = [
  'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Uttar Pradesh',
  'Gujarat', 'Rajasthan', 'West Bengal', 'Madhya Pradesh',
  'Delhi', 'Kerala', 'Punjab', 'Haryana', 'Bihar', 'Odisha',
  'Telangana', 'Andhra Pradesh', 'Assam', 'Jharkhand',
  'Chhattisgarh', 'Uttarakhand', 'Himachal Pradesh', 'Goa'
];

// Disease keywords
export const DISEASES = {
  'Dengue': ['dengue', 'dengue fever'],
  'Cholera': ['cholera'],
  'Influenza': ['influenza', 'flu', 'h1n1', 'h3n2'],
  'COVID-19': ['covid', 'coronavirus', 'covid-19', 'covid19', 'sars-cov-2'],
  'Malaria': ['malaria'],
  'Typhoid': ['typhoid', 'typhoid fever']
};

class NewsOutbreakFetcher {
  constructor() {
    this.newsApiKey = process.env.NEWS_API_KEY || null;
    this.cache = {
      articles: [],
      lastFetch: null
    };
  }

  // Fetch from Google News RSS (Free, No API Key)
  async fetchGoogleNews(disease, location = 'India') {
    try {
      const query = encodeURIComponent(`${disease} outbreak ${location}`);
      const url = `https://news.google.com/rss/search?q=${query}&hl=en-IN&gl=IN&ceid=IN:en`;

      console.log(`📰 Fetching Google News for: ${disease} in ${location}`);
      const feed = await parser.parseURL(url);

      return feed.items.map(item => ({
        title: item.title,
        description: item.contentSnippet || item.description || '',
        url: item.link,
        publishedAt: item.pubDate ? new Date(item.pubDate).toISOString() : new Date().toISOString(),
        source: { name: this.extractSource(item.title) },
        content: item.contentSnippet || ''
      }));
    } catch (error) {
      console.error(`❌ Error fetching Google News for ${disease}:`, error.message);
      return [];
    }
  }

  // Fetch from News API (if key available)
  async fetchNewsAPI(disease) {
    if (!this.newsApiKey) {
      return [];
    }

    try {
      const query = `${disease} outbreak India`;
      const url = 'https://newsapi.org/v2/everything';

      const response = await axios.get(url, {
        params: {
          q: query,
          language: 'en',
          sortBy: 'publishedAt',
          pageSize: 20,
          apiKey: this.newsApiKey
        }
      });

      return response.data.articles;
    } catch (error) {
      console.error(`❌ Error fetching News API for ${disease}:`, error.message);
      return [];
    }
  }

  // Extract source name from Google News title
  extractSource(title) {
    // Google News format: "Title - Source Name"
    const match = title.match(/\s-\s([^-]+)$/);
    return match ? match[1].trim() : 'Google News';
  }

  // Fetch all outbreak news
  async fetchAllOutbreakNews() {
    console.log('🔄 Fetching real outbreak news from multiple sources...');
    const allArticles = [];

    // Fetch for each disease
    for (const [diseaseName, keywords] of Object.entries(DISEASES)) {
      // Google News (always available)
      const googleArticles = await this.fetchGoogleNews(diseaseName);
      allArticles.push(...googleArticles.map(a => ({ ...a, disease: diseaseName })));

      // News API (if key available)
      if (this.newsApiKey) {
        const newsApiArticles = await this.fetchNewsAPI(diseaseName);
        allArticles.push(...newsApiArticles.map(a => ({ ...a, disease: diseaseName })));
      }

      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    console.log(`✅ Fetched ${allArticles.length} articles from news sources`);
    this.cache.articles = allArticles;
    this.cache.lastFetch = new Date();

    return allArticles;
  }

  // Get cached articles (if fresh)
  getCachedArticles() {
    const cacheAge = this.cache.lastFetch
      ? (new Date() - this.cache.lastFetch) / 1000 / 60
      : Infinity;

    // Cache valid for 30 minutes
    if (cacheAge < 30) {
      console.log(`📦 Using cached articles (${Math.round(cacheAge)} mins old)`);
      return this.cache.articles;
    }

    return null;
  }

  // Get articles (cached or fresh)
  async getArticles() {
    const cached = this.getCachedArticles();
    if (cached) {
      return cached;
    }

    return await this.fetchAllOutbreakNews();
  }
}

export default new NewsOutbreakFetcher();
