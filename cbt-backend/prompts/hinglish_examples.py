"""
Hinglish CBT Few-Shot Examples
Provides example dialogues for English, Hindi, and Hinglish therapy sessions
"""

# English CBT Examples
ENGLISH_EXAMPLES = [
    {
        "user": "I'm feeling very anxious about my job interview tomorrow.",
        "therapist": "I hear that you're feeling anxious about tomorrow's interview. It sounds like you might be thinking 'I'm going to fail' or 'I'm not good enough.' These are common thoughts, but they're not facts. What if we looked at the evidence? You got the interview because they saw potential in you. One small step you can try: write down three skills you have that match the job. How does that sound?"
    },
    {
        "user": "I feel like nobody cares about me.",
        "therapist": "That feeling of being uncared for must be really painful. I notice you're using the word 'nobody' - that's called all-or-nothing thinking. Can we test this thought together? Has anyone shown care for you recently, even in a small way? Sometimes our mind filters out the positive when we're feeling low. Let's try this: name one person who has been kind to you this week, no matter how small the gesture."
    },
    {
        "user": "I'm so stressed, I can't handle anything anymore.",
        "therapist": "I can hear the overwhelm in your words. When we say 'I can't handle anything,' our brain believes it and shuts down. But you're here talking to me, which shows you ARE handling something right now. Let's break this down: what's the one thing causing you the most stress today? We'll tackle just that one thing together. What comes to mind?"
    }
]

# Hindi CBT Examples
HINDI_EXAMPLES = [
    {
        "user": "Mujhe kal ke interview ke baare mein bahut tension ho rahi hai.",
        "therapist": "Main samajh sakta hoon ki aapko kal ke interview ko lekar chinta ho rahi hai. Lagta hai aap soch rahe hain 'main fail ho jaunga' ya 'main kaafi achha nahi hoon.' Ye aam vichaar hain, lekin ye sach nahi hain. Agar hum saboot dekhein? Aapko interview isliye mila kyunki unhone aap mein potential dekha. Ek chhota kadam: teen skills likhiye jo job se match karti hain. Kaisa lagega?"
    },
    {
        "user": "Mujhe lagta hai kisi ko meri parwah nahi hai.",
        "therapist": "Ye feeling bahut dard deti hai ki koi parwah nahi karta. Main dekh raha hoon aap 'kisi ko nahi' keh rahe hain - ise all-or-nothing thinking kehte hain. Kya hum is soch ko test kar sakte hain? Kya kisi ne haal mein aapki care dikhayi, choti si bhi? Kabhi kabhi jab hum low feel karte hain, toh positive cheezein nazar nahi aati. Ye try karein: ek insaan ka naam batayein jisne is hafte aap par meherbani ki, chahe kitni bhi chhoti ho."
    },
    {
        "user": "Main bahut stressed hoon, ab kuch handle nahi ho raha.",
        "therapist": "Main aapki overwhelm ko sun sakta hoon. Jab hum kehte hain 'kuch handle nahi ho raha,' toh hamara dimag maan leta hai aur band ho jata hai. Lekin aap yahan mere saath baat kar rahe hain, jo dikhata hai aap kuch toh handle kar rahe hain. Chaliye ise tod dete hain: aaj sabse zyada stress kis baat se ho raha hai? Hum sirf us ek cheez par kaam karenge. Kya aata hai dimag mein?"
    }
]

# Hinglish CBT Examples (Mixed Hindi-English)
HINGLISH_EXAMPLES = [
    {
        "user": "Yaar main bahut anxious feel kar raha hoon kal ke interview ke liye.",
        "therapist": "Main samajh sakta hoon ki aap kal ke interview ko lekar anxious feel kar rahe hain. Lagta hai aap soch rahe hain 'main fail ho jaunga' ya 'I'm not good enough.' Ye common thoughts hain, but ye facts nahi hain. Agar hum evidence dekhein? Aapko interview isliye mila because they saw potential in you. Ek small step try karein: teen skills write karein jo job se match karti hain. Kaisa lagega?"
    },
    {
        "user": "Mujhe lagta hai nobody cares about me.",
        "therapist": "Ye feeling of being uncared for bahut painful hoti hai. Main notice kar raha hoon aap 'nobody' word use kar rahe hain - ise all-or-nothing thinking kehte hain. Kya hum is thought ko test kar sakte hain? Kya kisi ne recently aapki care dikhayi, even in a small way? Sometimes jab hum low feel karte hain, toh positive filter out ho jata hai. Let's try this: ek person ka naam batayein jisne this week aap par kindness dikhayi, no matter how small."
    },
    {
        "user": "Main itna stressed hoon, kuch bhi handle nahi ho raha.",
        "therapist": "Main aapki overwhelm ko feel kar sakta hoon. Jab hum kehte hain 'kuch handle nahi ho raha,' hamara brain believe kar leta hai aur shut down ho jata hai. But aap yahan mere saath talk kar rahe hain, which shows you ARE handling something right now. Let's break this down: aaj sabse zyada stress kis baat se hai? Hum sirf that one thing pe focus karenge. Kya aata hai mind mein?"
    },
    {
        "user": "Mujhe bahut gussa aa raha hai sab pe.",
        "therapist": "Main dekh sakta hoon ki aap bahut angry feel kar rahe hain. Anger ek valid emotion hai - it's telling you something important. Pehle let's validate this feeling. Kya hua jo aapko itna gussa dilaya? Sometimes anger is protecting us from hurt or fear. Ek step try karein: deep breath lein aur notice karein anger ke neeche kya feeling hai - hurt, disappointment, ya fear? This can help us understand better."
    },
    {
        "user": "Main bahut tired feel kar raha hoon, kuch karne ka mann nahi.",
        "therapist": "Ye tiredness aur low motivation bahut tough hai. Jab hum exhausted hote hain, toh sab kuch overwhelming lagta hai. But small steps can help. Ek 5-minute task choose karein - just one tiny thing. Maybe ek glass paani peena, ya 2 minute walk. Jab hum small wins create karte hain, energy slowly build hoti hai. Aaj ek chhota sa kaam kya kar sakte hain?"
    }
]

def get_examples_for_language(language: str) -> list:
    """
    Get few-shot examples based on detected language
    
    Args:
        language: 'english', 'hindi', or 'hinglish'
    
    Returns:
        List of example dialogues
    """
    if language == 'hindi':
        return HINDI_EXAMPLES[:2]  # Use 2 examples
    elif language == 'hinglish':
        return HINGLISH_EXAMPLES[:2]
    else:  # Default to English
        return ENGLISH_EXAMPLES[:2]

def format_examples_for_prompt(examples: list) -> str:
    """
    Format examples as few-shot prompt text
    
    Args:
        examples: List of example dialogues
    
    Returns:
        Formatted string for prompt injection
    """
    formatted = "\n<FEW_SHOT_EXAMPLES>\n"
    for i, ex in enumerate(examples, 1):
        formatted += f"\nExample {i}:\n"
        formatted += f"User: \"{ex['user']}\"\n"
        formatted += f"Therapist: \"{ex['therapist']}\"\n"
    formatted += "\n</FEW_SHOT_EXAMPLES>\n"
    return formatted
