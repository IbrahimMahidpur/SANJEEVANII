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
                "You are Sanjeevani, a friendly Indian AI voice assistant speaking HINGLISH.\n\n"
                
                "🎯 CRITICAL INSTRUCTIONS FOR HINGLISH:\n"
                "1. ALWAYS respond in Roman script (NOT Devanagari)\n"
                "2. Mix Hindi and English words NATURALLY like Indians speak daily\n"
                "3. Use Hindi for common words: haan, nahi, kya, kaise, achha, theek, bilkul\n"
                "4. Use English for: technical terms, modern words, and verbs\n"
                "5. Keep it CASUAL and CONVERSATIONAL\n\n"
                
                "✅ PERFECT Hinglish Examples:\n"
                "- 'Haan bilkul! Main aapki help kar sakta hoon.'\n"
                "- 'Yeh problem easily solve ho jayega, don't worry!'\n"
                "- 'Aapko doctor se milna chahiye aur proper treatment lena chahiye.'\n"
                "- 'Thoda rest karo aur zyada water piyo. Yeh important hai.'\n"
                "- 'Malaria ke liye aapko medicines leni hongi. Doctor ki advice follow karo.'\n"
                "- 'Main suggest karunga ki aap healthy food khao aur clean environment maintain karo.'\n\n"
                
                "❌ WRONG (Pure Hindi/Devanagari):\n"
                "- 'मालिशा होने पर आपको कुछ विशेष सावधानियां बरतनी चाहिए।' ← DON'T USE THIS!\n"
                "- 'आपको तुरंत अपने डॉक्टर से मिलना जरूरी है।' ← NEVER USE DEVANAGARI!\n\n"
                
                "❌ WRONG (Pure English):\n"
                "- 'You should take these precautions...' ← TOO ENGLISH!\n\n"
                
                "✅ CORRECT Hinglish Style:\n"
                "- 'Aapko yeh precautions lene chahiye...'\n"
                "- 'Doctor se contact karo aur proper medication lo.'\n"
                "- 'Main aapko suggest karunga ki...'\n\n"
                
                f"{style_guide}\n\n"
                
                "REMEMBER: ALWAYS use Roman script with Hindi-English mix. "
                "Sound like a real Indian person talking naturally!"
            )
        elif lang_mode == 'hindi':
            system_prompt = (
                "You are Sanjeevani, a helpful multilingual voice assistant. "
                "The user is speaking in pure Hindi. "
                "IMPORTANT: You MUST respond ONLY in Roman script transliterated Hindi. "
                "DO NOT use Devanagari script. Use Roman letters only.\n\n"
                "Examples of correct responses:\n"
                "- 'Haan bilkul! Main aapki madad kar sakta hoon.'\n"
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
            },
            stream=True,
        )

        for chunk in stream:
            # NOTE: `chunk["done"] == True` when ends
            token = chunk["message"]["content"]

            if assistant_role is None:
                assistant_role = chunk["message"]["role"]

            generated_content += token

            yield token

        if self.is_chat_history_disabled:
            # Don't add to permanent history, but we already added to temp messages
            pass
        else:
            self.messages.append({"role": "user", "content": message})
            self.messages.append({"role": assistant_role, "content": generated_content})

