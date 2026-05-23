// scripts/downloadModels.js
/**
 * Download face-api.js models
 * Run: node scripts/downloadModels.js
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

const MODEL_BASE_URL = 'https://raw.githubusercontent.com/justadudewhohacks/face-api.js/master/weights';
const MODELS_DIR = path.join(__dirname, '..', 'public', 'models');

// Models we need
const MODELS = [
  // Tiny Face Detector (fast, lightweight)
  'tiny_face_detector_model-weights_manifest.json',
  'tiny_face_detector_model-shard1',

  // Face Expression Model (emotion recognition)
  'face_expression_model-weights_manifest.json',
  'face_expression_model-shard1'
];

// Ensure models directory exists
if (!fs.existsSync(MODELS_DIR)) {
  fs.mkdirSync(MODELS_DIR, { recursive: true });
}

console.log('📦 Downloading face-api.js models...\n');

// Download function
function downloadFile(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);

    https.get(url, (response) => {
      if (response.statusCode !== 200) {
        reject(new Error(`Failed to download: ${response.statusCode}`));
        return;
      }

      response.pipe(file);

      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', (err) => {
      fs.unlink(dest, () => { });
      reject(err);
    });
  });
}

// Download all models
async function downloadModels() {
  for (const model of MODELS) {
    const url = `${MODEL_BASE_URL}/${model}`;
    const dest = path.join(MODELS_DIR, model);

    // Skip if already exists
    if (fs.existsSync(dest)) {
      console.log(`✓ ${model} (already exists)`);
      continue;
    }

    try {
      console.log(`⬇️  Downloading ${model}...`);
      await downloadFile(url, dest);
      console.log(`✓ ${model} downloaded`);
    } catch (error) {
      console.error(`✗ Failed to download ${model}:`, error.message);
    }
  }

  console.log('\n✅ All models downloaded!');
  console.log(`📁 Location: ${MODELS_DIR}`);
}

downloadModels().catch(console.error);
