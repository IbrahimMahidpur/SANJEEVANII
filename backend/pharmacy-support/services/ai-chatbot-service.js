const axios = require('axios');

const OLLAMA_API = 'http://localhost:11434/api/generate';
const MODEL = 'gpt-oss:120b-cloud';

/**
 * System prompt for medical assistant
 */
const SYSTEM_PROMPT = `You are a helpful medical assistant chatbot for the Sanjeevani healthcare platform. Your role is to:

1. **Explain Medicines**: Provide information about medicines, their uses, side effects, dosage, and interactions.
2. **Recommend Doctors**: Suggest appropriate medical specialists based on symptoms and conditions.
3. **First Aid Advice**: Offer basic first aid guidance for common emergencies.
4. **Prescription Help**: Explain medical terms, dosage instructions, and help interpret prescriptions.

IMPORTANT GUIDELINES:
- Always remind users to consult a qualified doctor for serious medical issues
- Never diagnose conditions definitively
- Provide general information and guidance only
- Be empathetic and professional
- If unsure, advise consulting a healthcare professional
- Focus on Indian healthcare context

Keep responses concise, clear, and helpful.`;

/**
 * Query the AI chatbot
 */
async function queryChatbot(userMessage, context = null, sessionId = null) {
  try {
    // Build the full prompt with context
    let fullPrompt = SYSTEM_PROMPT + '\n\n';

    if (context) {
      fullPrompt += `Context: ${context}\n\n`;
    }

    fullPrompt += `User: ${userMessage}\n\nAssistant:`;

    console.log('🤖 Querying GPT-OSS 120B Cloud...');

    const response = await axios.post(OLLAMA_API, {
      model: MODEL,
      prompt: fullPrompt,
      stream: false,
      options: {
        temperature: 0.7,
        top_p: 0.9,
        max_tokens: 500
      }
    }, {
      timeout: 60000 // 60 second timeout
    });

    const aiResponse = response.data.response.trim();

    console.log('✅ AI response generated');

    return {
      response: aiResponse,
      sessionId: sessionId || `session_${Date.now()}`,
      timestamp: new Date().toISOString(),
      model: MODEL
    };

  } catch (error) {
    console.error('❌ AI chatbot error:', error.message);

    // Fallback response
    return {
      response: "I apologize, but I'm having trouble processing your request right now. Please try again or consult with a healthcare professional for immediate assistance.",
      sessionId: sessionId || `session_${Date.now()}`,
      timestamp: new Date().toISOString(),
      model: MODEL,
      error: true
    };
  }
}

/**
 * Get medicine information
 */
async function getMedicineInfo(medicineName) {
  const prompt = `Tell me about the medicine "${medicineName}". Include its uses, common side effects, typical dosage, and any important precautions.`;
  return await queryChatbot(prompt);
}

/**
 * Get doctor recommendation
 */
async function getDoctorRecommendation(symptoms) {
  const prompt = `Based on these symptoms: "${symptoms}", what type of doctor specialist should I consult? Explain briefly why.`;
  return await queryChatbot(prompt);
}

/**
 * Get first aid advice
 */
async function getFirstAidAdvice(situation) {
  const prompt = `What first aid steps should I take for: "${situation}"? Provide clear, step-by-step instructions.`;
  return await queryChatbot(prompt);
}

/**
 * Interpret prescription
 */
async function interpretPrescription(prescriptionText) {
  const prompt = `Help me understand this prescription: "${prescriptionText}". Explain the medical terms and dosage instructions in simple language.`;
  return await queryChatbot(prompt);
}

/**
 * General health query
 */
async function askHealthQuestion(question) {
  return await queryChatbot(question);
}

/**
 * Get medication alternatives
 */
async function getMedicineAlternatives(medicineName) {
  const prompt = `What are some generic or alternative medicines for "${medicineName}"? Include both generic names and common brands available in India.`;
  return await queryChatbot(prompt);
}

/**
 * Drug interaction check
 */
async function checkDrugInteraction(medicine1, medicine2) {
  const prompt = `Are there any known interactions between "${medicine1}" and "${medicine2}"? Should these be taken together?`;
  return await queryChatbot(prompt);
}

/**
 * Symptom checker
 */
async function checkSymptoms(symptoms) {
  const prompt = `I'm experiencing these symptoms: "${symptoms}". What could be possible causes? When should I see a doctor?`;
  return await queryChatbot(prompt);
}

module.exports = {
  queryChatbot,
  getMedicineInfo,
  getDoctorRecommendation,
  getFirstAidAdvice,
  interpretPrescription,
  askHealthQuestion,
  getMedicineAlternatives,
  checkDrugInteraction,
  checkSymptoms
};
