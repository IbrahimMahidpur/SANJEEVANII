# generate_cbt_datasets.py
"""
Comprehensive CBT Dataset Generator
Generates 6 specialized datasets with proper metadata for RAG ingestion
"""
import json
import uuid
import random
import os
from datetime import datetime

OUTPUT_DIR = "generated_datasets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------
# Config — change sizes here
# -------------------------
SIZES = {
    "trauma_cbt": 10000,
    "indian_hinglish_cbt": 50000,
    "relationship_cbt": 20000,
    "panic_disorder_cbt": 15000,
    "depression_worksheets": 50000,
    "synthetic_conversations": 50000
}

# -------------------------
# Helper utilities
# -------------------------
def make_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

def choose_lang_text(eng, hinglish, lang):
    if lang == "hinglish":
        return hinglish
    return eng

def timestamp():
    return datetime.utcnow().isoformat() + "Z"

# -------------------------
# Topic templates
# -------------------------
TRAUMA_PROMPTS = [
    ("safety_creation", 
     ("Create a safety plan: identify triggers, grounding steps, and safe people to contact.",
      "Safety plan banayein: triggers pe dhyaan do, grounding steps, aur kisi bharosemand insaan ka number note karein.")),
    ("window_of_tolerance", 
     ("Explain the 'window of tolerance' and how to widen it with grounding and pacing.",
      "'Window of tolerance' kya hota hai aur grounding/pacing se ise kaise broaden karein.")),
    ("flashback_grounding",
     ("Step-by-step grounding for flashbacks: 1) name 3 objects, 2) deep breath, 3) remind 'I am safe'.",
      "Flashback ke liye grounding: 1) 3 cheezein batao, 2) deep breath, 3) khud ko bolo 'I am safe'.")),
    ("somatic_stabilization",
     ("Simple somatic stabilizers: gentle movement, hands-on-heart, progressive tension-release.",
      "Somatic stabilizers: halka movement, haath dil par, progressive tension-release.")),
    ("trigger_map",
     ("How to build a trigger map and a small exposure plan with therapist guidance.",
      "Trigger map kaise banayein aur therapist guidance ke sath small exposure plan.")),
    ("trauma_narrative",
     ("Gradually building a trauma narrative with pacing and containment strategies.",
      "Trauma narrative dhire dhire banayein pacing aur containment strategies ke saath.")),
    ("body_awareness",
     ("Developing safe body awareness through gentle yoga or progressive muscle relaxation.",
      "Safe body awareness develop karein gentle yoga ya progressive muscle relaxation se.")),
]

INDIAN_HINGLISH_TOPICS = [
    ("family_pressure", 
     ("CBT steps for handling family pressure about studies/career.",
      "Studies/career par family pressure handle karne ke CBT steps.")),
    ("exam_anxiety_culturally",
     ("Exam anxiety techniques tuned for Indian students (rituals, pacing, family boundaries).",
      "Indian students ke liye exam anxiety techniques — rituals, pacing, family boundaries.")),
    ("arranged_marriage_stress",
     ("Coping steps for stress related to arranged marriage dynamics.",
      "Arranged marriage se judi stress ke liye coping steps.")),
    ("religious_guilt",
     ("Balancing religious expectations and self-compassion practices.",
      "Religious expectations aur self-compassion ko balance karne ke tareeke.")),
    ("community_shame",
      ("Addressing shame from small-town/community gossip with cognitive restructuring.",
      "Small-town gossip se aane wali shame ko cognitive restructuring se treat karein.")),
    ("joint_family_boundaries",
     ("Setting healthy boundaries in joint family settings while respecting elders.",
      "Joint family mein healthy boundaries set karein elders ka respect rakhte hue.")),
    ("career_vs_passion",
     ("Balancing parental career expectations with personal passion using CBT framework.",
      "Parents ki career expectations aur apni passion ko balance karein CBT framework se.")),
]

RELATIONSHIP_TOPICS = [
    "communication_reframe", "attachment_triggers", "boundary_setting",
    "interpretation_check", "repair_sequence", "jealousy_mapping", "trust_rebuilding",
    "conflict_de_escalation", "emotional_validation", "needs_expression"
]

PANIC_TOPICS = [
    "panic_step_protocol", "breathing_box", "paced_exhale", "panic_exposure_plan",
    "panic_warning_signs", "panic_recovery_plan", "interoceptive_exposure",
    "catastrophic_thinking_challenge", "safety_behavior_reduction"
]

DEPRESSION_TEMPLATES = [
    ("behavioral_activation", "Design a 7-day activity schedule with tiny wins and mood ratings."),
    ("rumination_breaker", "Practical steps to interrupt rumination: writing, timer, physical shift."),
    ("sleep_hygiene", "Sleep routine with wind-down, light exposure and caffeine limits."),
    ("self_compassion", "Short self-compassion scripts and practice plan."),
    ("goal_chunking", "Chunk big tasks into 5-minute microtasks and track completion."),
    ("social_connection", "Small steps to rebuild social connections: one text, one call, one meetup."),
    ("thought_records", "Complete thought record template with situation, mood, automatic thought, evidence, balanced thought."),
    ("pleasure_mastery", "Daily activities rated for pleasure and mastery to identify mood boosters."),
]

# Conversation templates for synthetic dataset (dialogue turns)
USER_PROBLEMS = [
    "I feel very anxious before my exams and can't sleep.",
    "I keep thinking I'm a failure after one mistake at work.",
    "I had a panic attack yesterday and I'm afraid it will happen again.",
    "My parents keep pressuring me about my career and I feel trapped.",
    "I can't sleep and feel hopeless about everything.",
    "My partner doesn't understand me and we keep fighting.",
    "I feel guilty for not meeting my family's expectations.",
    "I'm overwhelmed with work and don't know how to cope.",
]

# -------------------------
# Generators
# -------------------------
def generate_trauma_chunk(i):
    topic, (eng, hing) = random.choice(TRAUMA_PROMPTS)
    lang = "hinglish" if random.random() < 0.35 else "english"
    text = choose_lang_text(eng, hing, lang)
    extras = [
        "Practical exercise: write 3 signs of grounding that work for you.",
        "Example: after a flashback, use 60-second sensory grounding.",
        "Note: encourage clinician involvement for complex trauma.",
        "Remember: healing is not linear, be patient with yourself.",
        "Safety first: if overwhelmed, reach out to your therapist immediately.",
    ]
    text = f"{text} {random.choice(extras)}"
    return {
        "id": make_id("trauma"),
        "category": "trauma_cbt",
        "topic": topic,
        "language": lang,
        "text": text,
        "safety_level": "clinician_guided",
        "created_at": timestamp()
    }

def generate_indian_hinglish_chunk(i):
    topic, (eng, hing) = random.choice(INDIAN_HINGLISH_TOPICS)
    lang = "hinglish" if random.random() < 0.8 else "english"
    text = choose_lang_text(eng, hing, lang)
    tags = ["culture_india", "family", "education"] if "exam" in text.lower() or "study" in text.lower() else ["culture_india"]
    extra = random.choice([
        "Tip: involve respectful boundary-setting with elders.",
        "Exercise: write a short script to practice with family.",
        "Reflection: what is within your control?",
        "Cultural note: balance respect with self-care.",
        "Practice: start with small conversations, build confidence.",
    ])
    return {
        "id": make_id("hinglish"),
        "category": "indian_hinglish_cbt",
        "topic": topic,
        "language": lang,
        "text": f"{text} {extra}",
        "tags": tags,
        "safety_level": "safe",
        "created_at": timestamp()
    }

def generate_relationship_chunk(i):
    topic = random.choice(RELATIONSHIP_TOPICS)
    lang = "english" if random.random() < 0.85 else "hinglish"
    
    if lang == "english":
        text = f"Relationship CBT: {topic}. This covers identifying triggers, understanding your attachment style's role, practicing one dialogue example with 'I feel' statements, and a concrete repair step to try after conflicts."
    else:
        text = f"Relationship CBT: {topic}. Yeh triggers identify karna, attachment style ka role samajhna, 'I feel' statements ke saath dialogue practice, aur conflicts ke baad repair step try karna sikhata hai."
    
    return {
        "id": make_id("relationship"),
        "category": "relationship_cbt",
        "topic": topic,
        "language": lang,
        "text": text,
        "safety_level": "safe",
        "created_at": timestamp()
    }

def generate_panic_chunk(i):
    topic = random.choice(PANIC_TOPICS)
    lang = "english" if random.random() < 0.9 else "hinglish"
    
    if lang == "english":
        text = f"Panic disorder protocol: {topic}. Steps: 1) Recognize early warning signs (heart racing, dizziness), 2) Use 4-7-8 breathing or box breathing, 3) Ground with 5-4-3-2-1 technique, 4) Remind yourself 'This will pass, I am safe', 5) Post-panic review to identify triggers."
    else:
        text = f"Panic disorder protocol: {topic}. Steps: 1) Warning signs pehchano (dil tez, chakkar), 2) 4-7-8 breathing ya box breathing use karo, 3) 5-4-3-2-1 grounding technique, 4) Khud ko yaad dilao 'Yeh guzar jayega, main safe hoon', 5) Panic ke baad triggers identify karo."
    
    return {
        "id": make_id("panic"),
        "category": "panic_disorder_cbt",
        "topic": topic,
        "language": lang,
        "text": text,
        "safety_level": "safe",
        "created_at": timestamp()
    }

def generate_depression_chunk(i):
    topic, desc = random.choice(DEPRESSION_TEMPLATES)
    lang = "english" if random.random() < 0.9 else "hinglish"
    
    if lang == "english":
        text = f"Depression worksheet: {topic}. {desc} Include step-by-step microtasks (5-10 minutes each), mood-tracking instructions (rate 0-10 before and after), and self-compassion reminders when tasks feel hard."
    else:
        text = f"Depression worksheet: {topic}. {desc} Step-by-step microtasks (5-10 minute each), mood-tracking instructions (0-10 rate karo pehle aur baad mein), aur jab mushkil lage toh self-compassion yaad rakho."
    
    return {
        "id": make_id("depression"),
        "category": "depression_worksheets",
        "topic": topic,
        "language": lang,
        "text": text,
        "safety_level": "safe",
        "created_at": timestamp()
    }

# Synthetic human conversation generator (simple multi-turn)
def generate_synthetic_conversation(i):
    user_problem = random.choice(USER_PROBLEMS)
    
    # Generate realistic therapeutic conversation
    follow_q = random.choice([
        "When did this start, and what thoughts come to mind right then?",
        "Can you tell me more about what happens in your body when you feel this way?",
        "What do you notice yourself doing when these feelings come up?",
        "Have you noticed any patterns in when this happens?",
    ])
    
    reframe = random.choice([
        "One balanced thought: 'I did my best on this task; one result doesn't define me.'",
        "Alternative perspective: 'This feeling is temporary and doesn't mean something is wrong with me.'",
        "Balanced view: 'I can handle difficult emotions; they don't last forever.'",
        "Reframe: 'Making mistakes is part of learning, not a sign of failure.'",
    ])
    
    action = random.choice([
        "Try one 5-minute activity (walk or write) and rate anxiety before and after.",
        "Practice 4-7-8 breathing for 2 minutes and notice what changes.",
        "Write down 3 things you can control in this situation.",
        "Schedule one small pleasant activity for tomorrow and track your mood.",
    ])
    
    conv = [
        {"speaker": "user", "text": user_problem},
        {"speaker": "agent", "text": follow_q},
        {"speaker": "agent", "text": reframe},
        {"speaker": "agent", "text": action}
    ]
    
    return {
        "id": make_id("conv"),
        "category": "synthetic_conversations",
        "language": "english",
        "turns": conv,
        "safety_level": "safe",
        "created_at": timestamp()
    }

# -------------------------
# Bulk generation
# -------------------------
def generate_all():
    print("Starting CBT dataset generation...")
    print(f"Total chunks to generate: {sum(SIZES.values()):,}")
    print()
    
    out_files = {}
    
    # Generate each dataset
    print("Generating trauma_cbt...")
    out_files["trauma_cbt.json"] = [generate_trauma_chunk(i) for i in range(SIZES["trauma_cbt"])]
    
    print("Generating indian_hinglish_cbt...")
    out_files["indian_hinglish_cbt.json"] = [generate_indian_hinglish_chunk(i) for i in range(SIZES["indian_hinglish_cbt"])]
    
    print("Generating relationship_cbt...")
    out_files["relationship_cbt.json"] = [generate_relationship_chunk(i) for i in range(SIZES["relationship_cbt"])]
    
    print("Generating panic_disorder_cbt...")
    out_files["panic_disorder_cbt.json"] = [generate_panic_chunk(i) for i in range(SIZES["panic_disorder_cbt"])]
    
    print("Generating depression_worksheets...")
    out_files["depression_worksheets.json"] = [generate_depression_chunk(i) for i in range(SIZES["depression_worksheets"])]
    
    print("Generating synthetic_conversations...")
    out_files["synthetic_conversations.json"] = [generate_synthetic_conversation(i) for i in range(SIZES["synthetic_conversations"])]
    
    # Write to files
    print("\nWriting to files...")
    for fname, data in out_files.items():
        path = os.path.join(OUTPUT_DIR, fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✓ Wrote {len(data):,} items to {path}")
    
    print(f"\n✓ All datasets generated in {OUTPUT_DIR}/")
    print(f"Total chunks: {sum(len(d) for d in out_files.values()):,}")

if __name__ == "__main__":
    generate_all()
