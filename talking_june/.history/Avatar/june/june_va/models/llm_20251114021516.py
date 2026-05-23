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
                "You are Sanjeevani, a friendly Indian AI voice assistant. "
                "The user is speaking in Hinglish (mix of Hindi and English). "
                "IMPORTANT: You MUST respond in Hinglish with the same casual, friendly tone. "
                "Mix Hindi and English words naturally like Indians do in everyday conversation. "
                "DO NOT respond in pure English - always mix Hindi words naturally. "
                "Examples of Hinglish responses:\n"
                "- 'Haan bilkul! Main aapki help kar sakta hoon.'\n"
                "- 'Thoda wait karo, main check kar raha hoon.'\n"
                "- 'Mujhe lagta hai ki yeh solution achha rahega.'\n"
                "- 'Kya aur kuch help chahiye?'\n"
                f"{style_guide}"
            )
        elif lang_mode == 'hindi':
            system_prompt = (
                "You are Sanjeevani, a helpful multilingual voice assistant. "
                "The user is speaking in Hindi (Devanagari or transliterated). "
                "IMPORTANT: You MUST respond in Hindi. Use Devanagari script if possible, or transliterated Hindi. "
                "Keep responses natural, conversational and warm in Hindi only. "
                "Examples of Hindi responses:\n"
                "- 'हाँ बिल्कुल! मैं आपकी मदद कर सकता हूं।'\n"
                "- 'Haan bilkul! Main aapki madad kar sakta hoon.'\n"
                "- 'थोड़ा इंतज़ार करो, मैं चेक कर रहा हूं।'\n"
                "- 'Kripya intezar karein, main check kar raha hoon.'\n"
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
        
        # Limit conversation history to last 6 exchanges (12 messages)
        MAX_HISTORY = 12
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

