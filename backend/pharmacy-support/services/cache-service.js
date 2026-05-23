const NodeCache = require('node-cache');
const fs = require('fs').promises;
const path = require('path');

// Cache with 24-hour TTL for geo data
const geoCache = new NodeCache({ stdTTL: 86400, checkperiod: 600 });

// Rate limiting cache (1 second TTL for API calls)
const rateLimitCache = new NodeCache({ stdTTL: 1, checkperiod: 1 });

const CACHE_FILE = path.join(__dirname, '../data/cache.json');

/**
 * Load cache from disk on startup
 */
async function loadCacheFromDisk() {
  try {
    const data = await fs.readFile(CACHE_FILE, 'utf8');
    const cacheData = JSON.parse(data);

    Object.entries(cacheData).forEach(([key, value]) => {
      geoCache.set(key, value);
    });

    console.log('✅ Cache loaded from disk');
  } catch (error) {
    console.log('ℹ️ No existing cache file, starting fresh');
  }
}

/**
 * Save cache to disk periodically
 */
async function saveCacheToDisk() {
  try {
    const keys = geoCache.keys();
    const cacheData = {};

    keys.forEach(key => {
      cacheData[key] = geoCache.get(key);
    });

    await fs.writeFile(CACHE_FILE, JSON.stringify(cacheData, null, 2));
    console.log('💾 Cache saved to disk');
  } catch (error) {
    console.error('❌ Error saving cache:', error.message);
  }
}

/**
 * Generate cache key for geo queries
 */
function generateGeoKey(lat, lng, radius, type) {
  // Round to 2 decimal places for cache grouping
  const roundedLat = Math.round(lat * 100) / 100;
  const roundedLng = Math.round(lng * 100) / 100;
  return `geo_${roundedLat}_${roundedLng}_${radius}_${type}`;
}

/**
 * Get cached geo data
 */
function getCached(key) {
  return geoCache.get(key);
}

/**
 * Set cached geo data
 */
function setCached(key, value) {
  geoCache.set(key, value);

  // Save to disk every 10 cache updates
  if (Math.random() < 0.1) {
    saveCacheToDisk();
  }
}

/**
 * Check rate limit for external API
 */
function checkRateLimit(apiName) {
  const key = `ratelimit_${apiName}`;
  const lastCall = rateLimitCache.get(key);

  if (lastCall) {
    return false; // Rate limited
  }

  rateLimitCache.set(key, Date.now());
  return true; // OK to proceed
}

/**
 * Clear all cache
 */
function clearCache() {
  geoCache.flushAll();
  console.log('🗑️ Cache cleared');
}

/**
 * Get cache stats
 */
function getCacheStats() {
  return {
    keys: geoCache.keys().length,
    hits: geoCache.getStats().hits,
    misses: geoCache.getStats().misses,
    hitRate: geoCache.getStats().hits / (geoCache.getStats().hits + geoCache.getStats().misses) || 0
  };
}

// Auto-save cache every 5 minutes
setInterval(saveCacheToDisk, 5 * 60 * 1000);

// Load cache on startup
loadCacheFromDisk();

module.exports = {
  generateGeoKey,
  getCached,
  setCached,
  checkRateLimit,
  clearCache,
  getCacheStats,
  saveCacheToDisk
};
