import fs from 'fs';
import natural from 'natural';

const TfIdf = natural.TfIdf;
const tokenizer = new natural.WordTokenizer();

class MedicalRAG {
  constructor() {
    this.dataset = [];
    this.tfidf = new TfIdf();
    this.isLoaded = false;
  }

  // Load medical dataset
  loadDataset(filePath) {
    try {
      console.log('Loading medical dataset...');
      const fileContent = fs.readFileSync(filePath, 'utf-8');
      const lines = fileContent.split('\n').filter(line => line.trim());

      this.dataset = lines.map(line => {
        try {
          return JSON.parse(line);
        } catch (e) {
          return null;
        }
      }).filter(item => item !== null);

      console.log(`Loaded ${this.dataset.length} medical entries`);

      // Build TF-IDF index
      this.buildIndex();
      this.isLoaded = true;

      return true;
    } catch (error) {
      console.error('Error loading dataset:', error);
      return false;
    }
  }

  // Build TF-IDF index for fast searching
  buildIndex() {
    console.log('Building search index...');
    this.dataset.forEach(item => {
      const text = `${item.instruction} ${item.response}`;
      this.tfidf.addDocument(text);
    });
    console.log('Index built successfully!');
  }

  // Search for relevant medical information
  search(query, topK = 3) {
    if (!this.isLoaded) {
      return [];
    }

    const results = [];

    this.tfidf.tfidfs(query, (i, measure) => {
      results.push({
        index: i,
        score: measure,
        data: this.dataset[i]
      });
    });

    // Sort by relevance and return top K
    return results
      .sort((a, b) => b.score - a.score)
      .slice(0, topK)
      .filter(r => r.score > 0); // Only return relevant results
  }

  // Get context for the LLM
  getContext(query, topK = 3) {
    const results = this.search(query, topK);

    if (results.length === 0) {
      return null;
    }

    // Format context for the LLM
    let context = "Relevant medical information from database:\n\n";
    results.forEach((result, idx) => {
      context += `${idx + 1}. Q: ${result.data.instruction}\n`;
      context += `   A: ${result.data.response}\n\n`;
    });

    return context;
  }
}

// Create singleton instance
const medicalRAG = new MedicalRAG();

export default medicalRAG;
