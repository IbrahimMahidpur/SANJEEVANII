"""
Agent 3: Therapy Response Generator
Generates final therapeutic response using LLM + RAG + Memory
"""

from typing import Dict, Optional
import logging
import requests
import sys
import os

# Add path to prompts directory
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from prompts.hinglish_examples import get_examples_for_language, format_examples_for_prompt


logger = logging.getLogger(__name__)


class TherapyResponseGenerator:
    """Generates therapeutic responses using all context"""
    
    THERAPY_PROMPT_TEMPLATE = """# ROLE
You are a multilingual (English/Hindi/Hinglish) expert Cognitive Behavioural Therapist (CBT) with deep expertise in evidence-based therapeutic techniques, psychological assessment, and cross-cultural mental health support. You embody warmth, empathy, and non-judgment while maintaining professional boundaries.

# TASK
Provide compassionate, structured CBT support to help clients identify and overcome psychological challenges through collaborative exploration of thoughts, feelings, and behaviors. Guide clients toward practical coping strategies and sustainable behavioral change.

# CORE THERAPEUTIC APPROACH
- Begin by establishing safety and rapport, asking open-ended questions to understand the client's primary concern
- Validate the client's feelings and experiences before introducing any CBT concepts
- Gently help clients identify the connection between their thoughts, feelings, and behaviors using concrete examples
- Teach practical CBT techniques progressively—thought records, behavioral experiments, graded exposure, or problem-solving
- Encourage small, achievable steps toward change rather than overwhelming clients with large goals

# BOUNDARIES AND SAFETY
- Never diagnose or prescribe medication; recommend professional evaluation when needed
- Immediately escalate and provide crisis resources if the client expresses suicidal ideation or self-harm intent
- Do not attempt to address trauma-focused work, severe personality disorders, or psychotic symptoms

---

<SESSION_HISTORY>
{session_history}
</SESSION_HISTORY>

<USER_BACKGROUND>
{memory}
</USER_BACKGROUND>

<EMOTIONAL_ANALYSIS>
{analysis}
</EMOTIONAL_ANALYSIS>

<CBT_EVIDENCE>
{evidence}
</CBT_EVIDENCE>

{few_shot_examples}

<OUTPUT_LANGUAGE>{output_language}</OUTPUT_LANGUAGE>

{output_language_instruction}

---

User says: "{user_input}"

# YOUR RESPONSE
Provide a warm, professional, structured CBT response that:
1. Validates their feelings and shows you understand their situation
2. Identifies thought patterns or cognitive distortions gently
3. Offers a balanced perspective using CBT principles
4. Suggests one practical, achievable action step
5. Ends with encouragement and keeps the conversation open

CRITICAL REQUIREMENTS:
✓ Response must be COMPLETE and DETAILED (800-1200 characters minimum)
✓ Address their SPECIFIC situation with personalized guidance
✓ Use their PREFERRED LANGUAGE ({output_language})
✓ Be WARM, EMPATHETIC, and PROFESSIONAL
✓ Provide ACTIONABLE CBT techniques
✓ NO clinical jargon, speak naturally
✓ End with proper CONCLUSION

Therapist:"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434/api/generate"):
        """
        Initialize Therapy Response Generator
        
        Args:
            ollama_url: Ollama API endpoint
        """
        self.ollama_url = ollama_url
        self.model = "gpt-oss:120b-cloud"
    
    def _detect_language(self, user_input: str) -> str:
        """
        Detect language of user input: english, hindi, or hinglish
        
        Args:
            user_input: User's message
        
        Returns:
            'english', 'hindi', or 'hinglish'
        """
        user_lower = user_input.lower()
        
        # Hindi/Devanagari script detection
        has_devanagari = any('\u0900' <= char <= '\u097F' for char in user_input)
        
        # Common Hindi/Hinglish words (romanized)
        hindi_words = [
            'main', 'mujhe', 'hai', 'hoon', 'ka', 'ki', 'ko', 'se', 'mein',
            'aap', 'tum', 'yeh', 'woh', 'kya', 'kaise', 'kyun', 'kab',
            'bahut', 'thoda', 'zyada', 'kam', 'achha', 'bura', 'sahi', 'galat',
            'kar', 'ho', 'tha', 'thi', 'the', 'hoga', 'hogi', 'honge',
            'nahi', 'nahin', 'haan', 'ji', 'yaar', 'bhai', 'dost',
            'kuch', 'sab', 'sabhi', 'koi', 'kaun', 'jab', 'tab',
            'par', 'lekin', 'aur', 'ya', 'toh', 'bhi', 'hi',
            'udaas', 'khush', 'gussa', 'tension', 'pareshan', 'thaka',
            'dukh', 'sukh', 'dar', 'chinta', 'ghabrahat'
        ]
        
        # Count Hindi words
        hindi_word_count = sum(1 for word in hindi_words if word in user_lower)
        
        # English words (common therapy-related)
        english_words = [
            'feeling', 'think', 'thought', 'help', 'need', 'want', 'can',
            'anxious', 'depressed', 'stressed', 'worried', 'scared', 'angry',
            'happy', 'sad', 'tired', 'exhausted', 'overwhelmed'
        ]
        
        # Count English words
        english_word_count = sum(1 for word in english_words if word in user_lower)
        
        # Decision logic
        if has_devanagari:
            return 'hindi'
        elif hindi_word_count >= 3 and english_word_count >= 2:
            return 'hinglish'  # Mix of both
        elif hindi_word_count >= 2:
            return 'hinglish'  # Mostly Hindi with some English
        elif english_word_count >= 2:
            return 'english'
        else:
            # Default based on word count
            if hindi_word_count > english_word_count:
                return 'hinglish'
            else:
                return 'english'

    
    
    
    def _filter_devanagari(self, text: str, language: str) -> str:
        """Filter Devanagari characters for Hindi/Hinglish (Sanjeevani approach)"""
        if language in ['hindi', 'hinglish']:
            # Remove Devanagari range (U+0900 to U+097F)
            filtered = ''.join(char for char in text 
                              if not ('\u0900' <= char <= '\u097F'))
            return filtered
        return text

    def _get_language_specific_instruction(self, language: str) -> str:
        """Get language-specific instruction for system prompt (ULTRA-STRONG for Hindi/Hinglish)"""
        
        if language == 'hinglish':
            return """
╔══════════════════════════════════════════════════════════════╗
║ CRITICAL LANGUAGE INSTRUCTION - HINGLISH ONLY               ║
╚══════════════════════════════════════════════════════════════╝

YOU MUST RESPOND IN HINGLISH (MIX OF HINDI AND ENGLISH).
DO NOT RESPOND IN PURE ENGLISH. THIS IS MANDATORY.

HINGLISH RESPONSE FORMAT:
- Mix Hindi and English words NATURALLY
- Use Roman script ONLY (NO Devanagari देवनागरी)
- Sound like a caring Indian therapist talking

MANDATORY HINGLISH WORDS TO USE:
- main (I), aap (you), hain/hai (is/are), hoon (am)
- kya (what), kaise (how), kyun (why), kab (when)
- bahut (very), achha (good), theek (okay), sahi (right)
- samajh (understand), baat (talk), tension (stress)
- lekin (but), aur (and), toh (then), ki (that)

╔══════════════════════════════════════════════════════════════╗
║ CRITICAL RESPONSE LENGTH REQUIREMENT - DO NOT IGNORE!      ║
╚══════════════════════════════════════════════════════════════╝

ABSOLUTE MINIMUM: 800 characters (160 words)
OPTIMAL TARGET: 1000-1200 characters (200-240 words)

⚠️ WARNING: Responses shorter than 800 characters will be REJECTED!

YOU MUST:
1. Provide detailed, conversational responses
2. Ask AT LEAST 3-4 follow-up questions
3. Show deep empathy and understanding
4. Explain CBT concepts in detail
5. Share coping strategies
6. Validate feelings thoroughly
7. Use examples and analogies

EXAMPLE HINGLISH RESPONSES (COPY THIS STYLE AND LENGTH - 800+ CHARS):
"Main samajh sakta hoon ki aap bahut tension feel kar rahe hain. Yeh anxiety bilkul normal hai aur aap akele nahi hain jo yeh feel kar rahe hain. Dekhiye, jab hum stressed feel karte hain, toh humara dimag automatically negative thoughts mein chala jata hai. Yeh ek natural response hai lekin hum isse manage kar sakte hain. 

Pehle mujhe yeh batayein - yeh tension kab se ho raha hai? Kya koi specific event tha jiske baad yeh shuru hua? Aur kya koi particular situation hai jismein aap zyada anxious feel karte hain? Jaise office mein, ghar par, ya kisi aur jagah?

Main aapki help karunga isko samajhne mein. Hum saath mein kuch coping strategies explore karenge jo aapke liye helpful hongi. Jaise breathing exercises, thought challenging, aur relaxation techniques. Yeh sab bahut effective hain anxiety ko manage karne mein.

Batayein mujhe, aapke physical symptoms kya hain jab aap anxious feel karte hain? Heart racing, sweating, ya kuch aur? Yeh details important hain kyunki hum isse better understand kar sakte hain."

WRONG (Too Short - 50 chars): "Main samajh sakta hoon. Kya problem hai?"
RIGHT (Long - 800+ chars): [See example above with detailed questions, empathy, and strategies]
"""
        elif language == 'hindi':
            return """
╔══════════════════════════════════════════════════════════════╗
║ CRITICAL LANGUAGE INSTRUCTION - HINDI ONLY                  ║
╚══════════════════════════════════════════════════════════════╝

YOU MUST RESPOND IN HINDI (ROMAN SCRIPT).
DO NOT RESPOND IN ENGLISH. THIS IS MANDATORY.

HINDI RESPONSE FORMAT:
- Use ONLY Hindi words in Roman script
- NO Devanagari script (देवनागरी)
- Sound like a caring Hindi-speaking therapist

MANDATORY HINDI WORDS TO USE:
- main, aap, hain, hoon, hai
- kya, kaise, kyun, kab, kahan
- bahut, achha, theek, sahi
- samajh, baat, chinta, pareshani
- lekin, aur, toh, ki, par

EXAMPLE HINDI RESPONSES (COPY THIS STYLE):
1. Emotional Validation

"Main dekh pa raha hoon ki aap kitna bojh mehsoos kar rahe hain. Yeh bilkul samajh mein aata hai."

"Aapka dukh genuine hai, aur main yahaan hoon aapke saath isse samajhne ke liye."

"Jo bhi aap feel kar rahe ho, woh valid hai. Hum milkar isse handle karenge."

"Aap akela nahi mehsoos karein. Main aapki baat dhyaan se sun raha hoon."

2. Supportive Clarification

"Aap kehna chahte ho ki yeh situation aapko mentally exhaust kar rahi hai, sahi samjha maine?"

"Mujhe thoda aur batayein ki aapko sabse zyada pareshaani kis cheez se ho rahi hai."

"Acha, toh problem iss point se shuru hui. Chaliye isko dheere-dheere clear karte hain."

"Aap ne jo share kiya hai, woh bahut important hai. Main is par aapki guide karunga."

3. Gentle Reassurance

"Tension kum ho sakti hai, bas hum ek-ek step mein chalenge."

"Main aapke saath hoon. Aapko yeh sab akela handle nahi karna padega."

"Overthinking normal hai, lekin hum isse manage karna seekh sakte hain."

"Aap thoda relax kijiye, hum is problem ko calmly samjhenge."

4. Empowering Statements

"Aapke andar strength hai. Hum use dhyaan se explore karenge."

"Aapne jo feelings express ki, woh actually improvement ka pehla step hota hai."

"Aap iss situation ko change kar sakte hain. Main aapko direction dunga."

"Aap capable ho — bas emotions ne momentarily overpower kar diya hai."

5. Grounding & Safety Tone

"Ek deep breath lijiye… hum ab safe space mein baat kar rahe hain."

"Jaldi nahi hai. Aap araam se apni baat batayein."

"Main poore shanti se sun raha hoon, aap apna time lijiye."

"Is waqt sirf hum dono baat kar rahe hain, aur main aapke saath hoon."
WRONG (English): "I understand you are worried."
RIGHT (Hindi): "Main samajh sakta hoon ki aap pareshan hain."
"""
        else:  # english
            return """
LANGUAGE INSTRUCTION:
- Respond in clear, natural English
- Be warm, professional, and empathetic
"""
    
    def _filter_devanagari(self, text: str, language: str) -> str:
        """Filter Devanagari characters for Hindi/Hinglish (Sanjeevani approach)"""
        if language in ['hindi', 'hinglish']:
            # Remove Devanagari range (U+0900 to U+097F)
            filtered = ''.join(char for char in text 
                              if not ('\u0900' <= char <= '\u097F'))
            return filtered
        return text

    def generate(
        self,
        user_input: str,
        analysis: Dict,
        evidence: Dict,
        session_memory: str = "",
        user_memory: str = "",
        emotion_data: Dict = None  # Visual context from face detection
    ) -> str:
        """
        Generate therapeutic response with emotion-adaptive approach
        
        Args:
            user_input: User's message
            analysis: Analysis from Agent 1
            evidence: Evidence from Agent 2
            session_memory: Formatted session history
            user_memory: Formatted user memory
            emotion_data: Face detection emotion data
        
        Returns:
            Therapeutic response string
        """
        try:
            # Format analysis
            analysis_text = self._format_analysis(analysis)
            
            # Format evidence with proper RAG structure
            evidence_text = ""
            if evidence.get('rag_context'):
                evidence_text = evidence['rag_context']
            elif evidence.get('techniques'):
                # Format retrieved docs properly
                techniques = evidence['techniques'][:3]  # Top 3 most relevant
                rag_parts = []
                for t in techniques:
                    rag_parts.append(f"""<RAG>
Source: {t.get('source', 'Unknown')}
Content: {t.get('content', '')[:400]}
</RAG>""")
                evidence_text = "\n".join(rag_parts)
            
            if not evidence_text:
                evidence_text = "<RAG>No specific CBT evidence retrieved for this query.</RAG>"
            
            # Add visual context if available (with user_input for mismatch detection)
            visual_context = self._format_visual_context(emotion_data, user_input)
            
            # Detect user's language
            detected_language = self._detect_language(user_input)
            
            # Get language-specific instruction (Sanjeevani approach)
            lang_instruction = self._get_language_specific_instruction(detected_language)
            
            # Base template
            prompt_template = self.THERAPY_PROMPT_TEMPLATE
            
            if visual_context:
                # Insert visual context before user input
                prompt_template = prompt_template.replace(
                    'User says: "{user_input}"',
                    visual_context + '\n\nUser says: "{user_input}"'
                )
            
            
            # Detect user's language
            detected_language = self._detect_language(user_input)
            
            # Get few-shot examples for detected language
            examples = get_examples_for_language(detected_language)
            few_shot_text = format_examples_for_prompt(examples)
            
            # Set output language instruction using Sanjeevani logic
            # This puts the strong instruction RIGHT into the CRITICAL section
            output_lang_instruction = lang_instruction
            
            logger.info(f"Detected language: {detected_language}")
            
            prompt = prompt_template.format(
                user_input=user_input,
                analysis=analysis_text,
                evidence=evidence_text,
                memory=user_memory if user_memory else "<USER_PATTERNS>No user history available yet.</USER_PATTERNS>",
                session_history=session_memory if session_memory else "<SESSION_MEMORY>This is the start of the conversation.</SESSION_MEMORY>",
                few_shot_examples=few_shot_text,
                output_language=detected_language.upper(),
                output_language_instruction=output_lang_instruction
            )
            
            # DEBUG: Log what we're sending to the model
            logger.info("=== DEBUGGING GPT-OSS 120B PIPELINE ===")
            logger.info(f"User Input: {user_input[:100]}")
            logger.info(f"Retrieved Docs Count: {len(evidence.get('techniques', []))}")
            if evidence.get('techniques'):
                for i, t in enumerate(evidence['techniques'][:2]):
                    logger.info(f"  Doc {i+1}: {t.get('source', 'Unknown')} - {t.get('content', '')[:100]}...")
            logger.info(f"Final Prompt Length: {len(prompt)} chars")
            logger.info(f"Prompt Preview: {prompt[:500]}...")
            
            # Call Ollama with optimized transformer settings for CBT therapy
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    # OPTIMIZED FOR CBT THERAPY (Sanjeevani approach)
                    "temperature": 0.6,          # Slightly higher for natural flow
                    "top_p": 0.95,               # Higher for better quality
                    "top_k": 50,                 # Balanced exploration
                    "num_ctx": 8192,             # Larger context for 120B model
                    "repeat_penalty": 1.1,       # Slightly reduced penalty
                    "presence_penalty": 0.0,     # Default (Sanjeevani uses 0.0)
                    "frequency_penalty": 0.0,    # Default (Sanjeevani uses 0.0)
                    "num_predict": 3072,         # INCREASED for complete, detailed responses
                    "mirostat": 2,               # Enable Mirostat v2 for quality
                    "mirostat_tau": 5.0,         # Target entropy
                    "mirostat_eta": 0.1,         # Learning rate
                    "stop": ["User:", "\n\nUser:", "Therapist:", "।", "॥"]  # Include Hindi punctuation
                }
            }
            
            logger.info("Generating therapy response...")
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            response.raise_for_status()
            
            
            result = response.json()
            therapy_response = result.get("response", "").strip()
            
            # SANJEEVANI-STYLE POST-PROCESSING
            # Apply Hinglish processor for natural flow (ellipsis, caring tone)
            if detected_language in ['hindi', 'hinglish']:
                from agents.hinglish_processor import HinglishProcessor
                therapy_response = HinglishProcessor.process(therapy_response)
                logger.info(f"Applied Hinglish post-processing (ellipsis, caring tone)")
            
            # Filter Devanagari for Hindi/Hinglish (Sanjeevani approach)
            therapy_response = self._filter_devanagari(therapy_response, detected_language)
            
            logger.info(f"Response generated ({len(therapy_response)} chars) in {detected_language}")
            return therapy_response
            
        except Exception as e:
            logger.error(f"Therapy generation error: {e}")
            return self._fallback_response()
    
    def _format_analysis(self, analysis: Dict) -> str:
        """Format analysis for prompt"""
        parts = ["<ANALYSIS>"]
        
        if analysis.get('emotions'):
            parts.append(f"Emotions: {', '.join(analysis['emotions'])}")
        
        if analysis.get('intensity'):
            parts.append(f"Intensity: {analysis['intensity']}/10")
        
        if analysis.get('distortions'):
            parts.append(f"Cognitive Distortions: {', '.join(analysis['distortions'])}")
        
        if analysis.get('negative_thoughts'):
            parts.append(f"Negative Thoughts: {', '.join(analysis['negative_thoughts'][:2])}")
        
        parts.append("</ANALYSIS>")
        return "\n".join(parts)
    
    def _detect_emotion_mismatch(self, emotion_data: Dict, user_input: str) -> Dict:
        """
        Detect if facial emotion contradicts verbal query (Multilingual: English/Hindi/Hinglish)
        Returns mismatch info if significant contradiction detected
        """
        if not emotion_data or not emotion_data.get('face_detected'):
            return None
        
        face_emotion = emotion_data.get('emotion', 'neutral')
        confidence = emotion_data.get('confidence', 0)
        
        # Only check if confidence is high enough
        if confidence < 0.5:
            return None
        
        user_input_lower = user_input.lower()
        
        # Define emotion keywords (English + Hindi + Hinglish)
        emotion_keywords = {
            'happy': [
                # English
                'happy', 'great', 'wonderful', 'excited', 'joyful', 'good', 'better',
                # Hindi
                'khush', 'achha', 'mast', 'badiya',
                # Hinglish
                'bahut achha', 'ekdum mast', 'sahi hai'
            ],
            'sad': [
                # English
                'sad', 'depressed', 'down', 'unhappy', 'miserable', 'hopeless',
                # Hindi
                'udaas', 'dukhi', 'pareshan', 'rona',
                # Hinglish
                'bahut dukh', 'ro raha', 'dil toot gaya'
            ],
            'angry': [
                # English
                'angry', 'mad', 'furious', 'frustrated', 'irritated', 'annoyed',
                # Hindi
                'gussa', 'krodh', 'chidh', 'naraz',
                # Hinglish
                'bahut gussa', 'chidh gayi', 'gussa aa raha'
            ],
            'anxious': [
                # English
                'anxious', 'worried', 'nervous', 'stressed', 'scared', 'afraid',
                # Hindi
                'chinta', 'ghabrahat', 'dar', 'tension',
                # Hinglish
                'bahut tension', 'dar lag raha', 'ghabra gaya'
            ],
            'tired': [
                # English
                'tired', 'exhausted', 'fatigued', 'drained', 'sleepy',
                # Hindi
                'thaka', 'kamzor', 'neend', 'susti',
                # Hinglish
                'bahut thaka', 'neend aa rahi', 'bilkul thak gaya'
            ]
        }
        
        # Detect verbal emotion from query
        detected_verbal_emotion = None
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                detected_verbal_emotion = emotion
                break
        
        # No verbal emotion detected - no mismatch
        if not detected_verbal_emotion:
            return None
        
        # Check for contradictions (intelligent rules)
        contradictions = {
            'happy': ['sad', 'angry', 'anxious'],
            'sad': ['happy'],
            'angry': ['happy'],
            'anxious': ['happy'],
        }
        
        # Neutral is acceptable with any verbal emotion
        if face_emotion == 'neutral':
            return None
        
        # Check if there's a contradiction
        if face_emotion in contradictions:
            if detected_verbal_emotion in contradictions[face_emotion]:
                return {
                    'face_emotion': face_emotion,
                    'verbal_emotion': detected_verbal_emotion,
                    'confidence': confidence,
                    'mismatch_type': f"{face_emotion}_face_but_{detected_verbal_emotion}_words"
                }
        
        return None
    
    def _format_visual_context(self, emotion_data: Dict, user_input: str = "") -> str:
        """
        Format visual context from face detection for LLM prompt
        Includes mismatch detection if applicable
        """
        if not emotion_data:
            return ""
        
        face_detected = emotion_data.get('face_detected', False)
        emotion = emotion_data.get('emotion', 'neutral')
        confidence = emotion_data.get('confidence', 0)
        crying_score = emotion_data.get('crying_score', 0)
        avoidance = emotion_data.get('avoidance_detected', False)
        
        # Detect emotion-query mismatch
        mismatch = self._detect_emotion_mismatch(emotion_data, user_input) if user_input else None
        
        # Build visual context block
        visual_parts = []
        visual_parts.append("<VISUAL_CONTEXT>")
        visual_parts.append(f"Face Detection: {'Yes' if face_detected else 'No'}")
        
        if face_detected:
            visual_parts.append(f"Observed Emotion: {emotion.upper()} (confidence: {confidence:.0%})")
            
            if crying_score > 0.5:
                visual_parts.append(f"Crying Likelihood: HIGH ({crying_score:.0%})")
            
            if avoidance:
                visual_parts.append("Camera Avoidance: DETECTED (possible discomfort/shame)")
            
            # Add mismatch warning if detected
            if mismatch:
                visual_parts.append(f"\n⚠️ EMOTION MISMATCH DETECTED:")
                visual_parts.append(f"  - Facial Expression: {mismatch['face_emotion'].upper()}")
                visual_parts.append(f"  - Verbal Expression: {mismatch['verbal_emotion'].upper()}")
                visual_parts.append(f"  - Confidence: {mismatch['confidence']:.0%}")
                visual_parts.append(f"\n  INSTRUCTION: Gently ask user to clarify their actual emotional state.")
                visual_parts.append(f"  Example: 'I notice you're saying you feel {mismatch['verbal_emotion']}, but you seem {mismatch['face_emotion']}. How are you really feeling right now?'")
            
            # Add therapy adaptation guidance (only if no mismatch)
            if not mismatch:
                adaptation = self._get_emotion_adaptation(emotion, crying_score, avoidance)
                if adaptation:
                    visual_parts.append(f"\nTherapy Adaptation: {adaptation}")
        
        visual_parts.append("</VISUAL_CONTEXT>")
        return "\n".join(visual_parts)
    
    def _get_emotion_adaptation(self, emotion: str, crying_score: float, avoidance: bool) -> str:
        """Get emotion-specific therapy adaptation guidance"""
        
        # Handle crying first (highest priority)
        if crying_score > 0.7:
            return "User appears to be crying - provide extra emotional support, validate distress, check safety, use compassionate tone"
        
        # Handle avoidance
        if avoidance:
            return "User avoiding eye contact - may indicate shame, fear, or overwhelm. Use gentle engagement, non-confrontational questions"
        
        # Emotion-specific adaptations
        adaptations = {
            'sad': "User appears sad - validate feelings, explore underlying thoughts, assess for depression symptoms, provide hope",
            'angry': "User appears angry - acknowledge frustration, explore triggers, teach emotional regulation, stay calm and non-defensive",
            'anxious': "User appears anxious - provide grounding, normalize anxiety, teach breathing techniques, explore worry patterns",
            'fearful': "User appears fearful - establish safety, validate concerns, explore specific fears, provide reassurance",
            'surprised': "User appears surprised - acknowledge unexpected reaction, explore what triggered surprise, provide context",
            'disgusted': "User appears disgusted - validate reaction, explore source of disgust, address underlying values/beliefs",
            'neutral': None  # No special adaptation needed
        }
        
        return adaptations.get(emotion)
    
    def _fallback_response(self) -> str:
        """Fallback response if generation fails"""
        return "I'm here to listen and support you. Could you tell me more about what's on your mind right now?"


# Factory function for easy import
def get_therapy_generator(ollama_url: str = "http://localhost:11434/api/generate") -> TherapyResponseGenerator:
    """Get therapy response generator instance"""
    return TherapyResponseGenerator(ollama_url=ollama_url)
