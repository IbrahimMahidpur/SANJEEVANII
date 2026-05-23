"""
This module provides a class for interacting with a Language Model (LLM) using the ollama library.
"""

from typing import Dict, Iterator, List, Optional

from ollama import Client, ResponseError

from .common import BaseModel


class LLM(BaseModel):
    """
    A class for interacting with a Language Model (LLM) using the ollama library.

    This class inherits from the BaseModel class and provides methods for checking if a model exists,
    and generating text from user input using the specified LLM.

    Args:
        **kwargs: Keyword arguments for initializing the LLM, including optional arguments
            like 'system_prompt' and 'disable_chat_history'.

    Attributes:
        messages: A list of dictionaries representing the conversation history,
            with each dictionary containing a 'role' (e.g., 'system', 'user', 'assistant') and 'content' keys.
        system_prompt: An optional system prompt to provide context for the conversation.
        is_chat_history_disabled: A flag indicating whether the chat history should be disabled.
        model: An instance of the ollama.Client for interacting with the LLM.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.messages: List[Dict[str, str]] = []

        self.system_prompt: Optional[str] = kwargs.get("system_prompt")

        if self.system_prompt:
            self.messages.append({"role": "system", "content": self.system_prompt})

        self.is_chat_history_disabled: Optional[bool] = kwargs.get("disable_chat_history")

        self.model = Client()

    def exists(self) -> bool:
        """
        Check if the specified LLM model exists.

        Returns:
            True if the model exists, False otherwise.
        """
        try:
            # Assert ollama model validity
            _ = self.model.show(self.model_id)

            return True
        except ResponseError:
            return False

    def forward(self, message: str) -> Iterator[str]:
        """
        Generate text from user input using the specified LLM.
        Automatically detects language mode and adjusts system prompt.

        Args:
            message: The user input message.

        Returns:
            An iterator that yields the generated text in chunks.
        """
        from june_va.utils import detect_language_mode
        
        # Detect language mode from user input
        lang_mode = detect_language_mode(message)
        
        # Log detected language for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Detected language mode: {lang_mode} from input: '{message[:50]}...'")
        
        # Style guidelines for all languages
        style_guide = """
When responding:
- Use natural, polite, emotionally aware language
- Be concise but include meaningful details
- Stay contextually relevant to the conversation
- Never sound robotic or templated
- Show personality and warmth"""
        
        # Prepare dynamic system message based on detected language
        if lang_mode == 'hinglish':
            system_prompt = (
                "# Role\n"
                "You are Sanjeevani, an expert conversational AI assistant fluent in Hinglish (a blend of Hindi and English), "
                "specializing in medical assistance. Your role is to communicate naturally with users by seamlessly "
                "mixing Hindi and English words, phrases, and grammatical structures in a way that feels authentic, "
                "comfortable, and trustworthy. You understand the cultural nuances of Hinglish speakers and can adapt "
                "your tone to match their communication style while maintaining the empathy and clarity essential for "
                "medical guidance.\n\n"
                
                "# Task\n"
                "Respond to all user medical queries in Hinglish with an equal mix of Hindi and English throughout, "
                "maintaining a natural, smooth flow between both languages. The assistant should prioritize clarity, "
                "reassurance, and relatability while preserving the casual, friendly tone that characterizes Hinglish "
                "communication. Medical information should be accessible without sacrificing accuracy.\n\n"
                
                "# Context\n"
                "Hinglish is widely spoken across India and among diaspora communities as a primary mode of informal "
                "communication, particularly in healthcare discussions. Users seeking medical assistance expect responses "
                "that feel native and conversational rather than formally translated or overly clinical. This approach "
                "makes health-related interactions more comfortable, engaging, and easier to understand for Hinglish "
                "speakers, which is especially important when discussing sensitive health topics.\n\n"
                
                "# Instructions\n"
                "- Maintain an equal balance of Hindi and English throughout responses, with English reserved primarily "
                "for technical medical terms, brand names, and scientific concepts that lack natural Hindi equivalents "
                "(e.g., 'diabetes,' 'antibiotics,' 'blood pressure'). This ensures naturalness while preserving medical "
                "accuracy.\n\n"
                
                "- Use smooth, natural code-switching that blends Hindi and English mid-sentence where it feels organic "
                "and conversational (e.g., 'Aapko fever hai toh paracetamol le sakte ho' or 'Yeh symptoms bilkul normal "
                "hain, tension mat lo'). The flow should never feel forced or awkwardly translated.\n\n"
                
                "- Use common Hinglish expressions, colloquialisms, and cultural references that resonate with native "
                "speakers while maintaining a reassuring, knowledgeable tone appropriate for medical guidance.\n\n"
                
                "- Avoid overly formal medical jargon or rigid translation; instead, prioritize conversational authenticity "
                "while ensuring medical information remains accurate and helpful. Explain complex conditions in simple, "
                "relatable terms using everyday language.\n\n"
                
                "- Adapt tone and vocabulary based on context—using warmer, more reassuring language for emotional or "
                "health anxiety topics, while remaining clear and structured when providing medical information or guidance. "
                "Keep both languages present throughout with natural balance and smooth transitions.\n\n"
                
                "# Critical Requirements\n"
                "⚠️ ALWAYS use ROMAN SCRIPT ONLY. NEVER use Devanagari script (Hindi characters like मैं, आप, etc.).\n"
                "✅ Correct: 'Main aapki help kar sakti hoon'\n"
                "❌ Wrong: 'मैं आपकी help कर सकती हूं'\n\n"
                
                "# Example Responses\n"
                "User: 'Mujhe malaria hua hai, kya karu?'\n"
                "Assistant: 'Oh no! Malaria ho gaya hai toh aapko immediately doctor se milna hoga. Proper diagnosis aur "
                "treatment bahut zaroori hai. Aap abhi fever, chills ya body pain feel kar rahe ho? Jaldi se blood test "
                "karwao taaki confirm ho sake. Medications sirf doctor ki prescription par hi lena, self-medication avoid "
                "karo. Rest zyada karo, fluids zyada piyo aur mosquitoes se bachne ki koshish karo.'\n\n"
                
                "User: 'Doctor se kab milna chahiye?'\n"
                "Assistant: 'Jitna jaldi ho sake utna better hai! Agar aapko high fever hai, continuous headache ho raha "
                "hai ya weakness bahut zyada feel ho rahi hai, toh aaj hi visit karo. Malaria serious ho sakta hai agar "
                "treatment delay ho jaye. Emergency mein hospital jaana padega agar symptoms severe hain. Take care!'\n\n"
                
                f"{style_guide}"
            )
        elif lang_mode == 'hindi':
            system_prompt = (
                "You are Sanjeevani, a helpful multilingual voice assistant. "
                "The user is speaking in pure Hindi. "
                "IMPORTANT: You MUST respond ONLY in Roman script transliterated Hindi. "
                "DO NOT use Devanagari script. Use Roman letters only.\n\n"
                "Examples of correct responses:\n"
                "- 'Haan bilkul! Main aapki madad kar sakti hoon.'\n"
                "- 'Aapko doctor se milna chahiye.'\n"
                "- 'Thoda intezar karein, main check kar raha hoon.'\n"
                "- 'Kripya apna khayal rakhein.'\n\n"
                f"{style_guide}"
            )
        else:  # english
            system_prompt = (
                "You are Sanjeevani, an intelligent English-speaking voice assistant. "
                "The user is speaking in English. "
                "Respond in fluent, natural English with a conversational tone. "
                "Be helpful, accurate, and personable.\n"
                f"{style_guide}"
            )
        
        # ⚡ OPTIMIZATION: Limit conversation history for SPEED
        # Shorter history = Less tokens to process = Faster response
        # Old: 12 messages, New: 8 messages (last 4 exchanges)
        MAX_HISTORY = 8
        recent_messages = self.messages[-MAX_HISTORY:] if len(self.messages) > MAX_HISTORY else self.messages
        
        # Prepare messages with dynamic system prompt
        messages_with_system = [{"role": "system", "content": system_prompt}]
        messages_with_system.extend(recent_messages)
        messages_with_system.append({"role": "user", "content": message})
        
        assistant_role = None
        generated_content = ""

        # ⚡ OPTIMIZED for REAL-TIME response (50+ years exp)
        # Reduced temperature, context, and length for SPEED
        stream = self.model.chat(
            model=self.model_id,
            messages=messages_with_system,
            options={
                "temperature": 0.3,          # 0.4→0.3: Faster, more deterministic
                "num_ctx": 4096,             # 8192→4096: HALF the context = 2x faster
                "top_p": 0.9,                # Balanced creativity
                "repeat_penalty": 1.2,       # Avoid repetition
                "presence_penalty": 0.2,     # Encourage topic diversity
                "frequency_penalty": 0.3,    # Reduce word repetition
                "num_predict": 400,          # 800→400: Shorter responses = faster
                "mirostat": 2,               # ⚡ NEW: Smart sampling for speed
                "mirostat_tau": 3.0,         # ⚡ NEW: Perplexity target
                "mirostat_eta": 0.1,         # ⚡ NEW: Learning rate
                # ⚡ CRITICAL: Prevent Devanagari characters
                "stop": ["।", "॥"],         # Stop on Hindi punctuation
            },
            stream=True,
        )

        for chunk in stream:
            # NOTE: `chunk["done"] == True` when ends
            token = chunk["message"]["content"]

            if assistant_role is None:
                assistant_role = chunk["message"]["role"]
            
            # ⚡ FILTER: Remove any Devanagari characters (force Roman script)
            # This ensures Hinglish stays in Roman letters
            if lang_mode in ['hinglish', 'hindi']:
                # Filter out Devanagari range (U+0900 to U+097F)
                token = ''.join(char for char in token 
                              if not ('\u0900' <= char <= '\u097F'))
                
                # Skip if token becomes empty after filtering
                if not token:
                    continue

            generated_content += token

            yield token

        if self.is_chat_history_disabled:
            # Don't add to permanent history, but we already added to temp messages
            pass
        else:
            self.messages.append({"role": "user", "content": message})
            self.messages.append({"role": assistant_role, "content": generated_content})

