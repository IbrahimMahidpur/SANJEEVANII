import os
import cv2
import numpy as np
import json
import re
from PIL import Image
import torch
import difflib
import spacy
from fuzzywuzzy import fuzz, process
from skimage import exposure, filters
from skimage.filters import unsharp_mask
from skimage.morphology import disk
import pytesseract

try:
    # Try to load spacy model for medical NER
    nlp = spacy.load("en_core_sci_md")
except:
    try:
        # Fall back to standard English model
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = None
        print("Warning: Spacy model not loaded. Using fallback text processing.")

# Medical dictionary for common prescription terms
MEDICATION_DICT = {
    # Common medications - Updated for Indian market
    "amoxicillin": ["amox", "amoxil", "amoxicil", "amoxicilin", "mox", "novamox", "almoxi", "wymox"],
    "paracetamol": ["paracet", "parcetamol", "acetaminophen", "tylenol", "crocin", "panadol", "dolo", "metacin", "calpol", "sumo", "febrex", "acepar", "pacimol"],
    "ibuprofen": ["ibuprofin", "ibu", "ibuprofen", "advil", "motrin", "nurofen", "brufen", "ibugesic", "combiflam"],
    "aspirin": ["asa", "acetylsalicylic", "aspr", "disprin", "ecotrin", "bayer", "loprin", "delisprin", "colsprin"],
    "lisinopril": ["lisin", "prinivil", "zestril", "qbrelis", "listril", "hipril", "zestopril"],
    "metformin": ["metform", "glucophage", "fortamet", "glumetza", "riomet", "glycomet", "obimet", "gluformin", "glyciphage"],
    "atorvastatin": ["lipitor", "atorva", "atorvastat", "lipibec", "atorlip", "atocor", "storvas"],
    "levothyroxine": ["synthroid", "levothy", "levothyrox", "levoxyl", "tirosint", "euthyrox", "thyronorm", "eltroxin"],
    "omeprazole": ["prilosec", "omepraz", "losec", "zegerid", "priosec", "omez", "ocid", "prazole"],
    "amlodipine": ["norvasc", "amlo", "amlod", "katerzia", "norvasc", "amlopress", "amlopres", "amlokind"],
    "metoprolol": ["lopressor", "toprol", "metopro", "toprol-xl", "betaloc", "metolar", "starpress"],
    "sertraline": ["zoloft", "sert", "sertra", "lustral", "serta", "daxid", "serlin"],
    "gabapentin": ["neurontin", "gaba", "gabap", "gralise", "horizant", "gabapin", "gaban", "progaba"],
    "hydrochlorothiazide": ["hctz", "hydrochlor", "microzide", "hydrodiuril", "hydrazide", "aquazide"],
    "simvastatin": ["zocor", "simvast", "simlup", "simcard", "simvotin", "zosta", "simgal"],
    "losartan": ["cozaar", "losart", "lavestra", "repace", "losar", "zaart", "covance"],
    "albuterol": ["proventil", "ventolin", "proair", "salbutamol", "asthalin", "ventofort", "aeromist"],
    "fluoxetine": ["prozac", "sarafem", "rapiflux", "prodep", "fludac", "flunil", "flunat"],
    "citalopram": ["celexa", "cipramil", "citalo", "celepram", "citalex", "citopam"],
    "pantoprazole": ["protonix", "pantoloc", "pantocid", "pantodac", "zipant", "pan"],
    "furosemide": ["lasix", "furos", "frusemide", "frusol", "lasix", "frusenex", "diucontin"],
    "rosuvastatin": ["crestor", "rosuvast", "rosuvas", "rovista", "rostor", "colver"],
    "escitalopram": ["lexapro", "cipralex", "nexito", "feliz", "stalopam", "nexito-forte"],
    "montelukast": ["singulair", "montek", "montair", "monticope", "romilast", "monty-lc"],
    "prednisone": ["deltasone", "predni", "orasone", "predcip", "omnacortil", "wysolone"],
    "warfarin": ["coumadin", "jantoven", "warf", "warfex", "warfrant", "uniwarfin"],
    "tramadol": ["ultram", "tram", "tramahexal", "tramazac", "domadol", "tramacip"],
    "azithromycin": ["zithromax", "azithro", "z-pak", "azith", "azee", "aziwok", "azimax", "zithrocin"],
    "ciprofloxacin": ["cipro", "ciloxan", "ciproxin", "ciplox", "ciprobid", "cifran", "ciprinol"],
    "lamotrigine": ["lamictal", "lamot", "lamotrigin", "lamogard", "lamitor", "lametec"],
    "venlafaxine": ["effexor", "venlaf", "venlor", "veniz", "ventab", "venlift"],
    "insulin": ["lantus", "humulin", "novolin", "humalog", "novolog", "tresiba", "insugen", "wosulin", "basalog", "insuman", "apidra"],
    "metronidazole": ["flagyl", "metro", "metrogel", "metrogyl", "metrozole", "aristogyl"],
    "naproxen": ["aleve", "naprosyn", "anaprox", "xenar", "napra", "napxen"],
    "doxycycline": ["vibramycin", "oracea", "doxy", "doxin", "biodoxi", "doxt"],
    "cetirizine": ["zyrtec", "cetryn", "cetriz", "alerid", "cetcip", "zirtin", "cetzine"],
    "diazepam": ["valium", "valpam", "dizac", "calmpose", "zepose", "sedopam"],
    "alprazolam": ["xanax", "alprax", "tafil", "alp", "alzolam", "zolax", "restyl", "trika"],
    "clonazepam": ["klonopin", "rivotril", "clon", "petril", "clonopam", "lonazep"],
    "carvedilol": ["coreg", "carvedil", "cardivas", "carca", "carvil", "carloc"],
    "fexofenadine": ["allegra", "telfast", "fexofine", "fexova", "agimfast", "allerfast"],
    "ranitidine": ["zantac", "ranit", "rantec", "aciloc", "zinetac", "histac"],
    "diclofenac": ["voltaren", "diclof", "diclomax", "voveran", "diclonac", "reactin"],
    "ceftriaxone": ["rocephin", "ceftri", "cefaxone", "inocef", "trixone", "monotax"],
    "cefixime": ["suprax", "cefi", "taxim", "unice", "cefispan", "omnicef"],
    "esomeprazole": ["nexium", "esotrex", "esopral", "nexpro", "raciper", "sompraz"],
    "clopidogrel": ["plavix", "clopid", "plagerine", "clopilet", "deplatt", "noklot"],
    
    # Adding more Indian medications
    "levocetirizine": ["xyzal", "levocet", "teczine", "levazeo", "xyzra", "uvnil"],
    "febuxostat": ["uloric", "febugat", "febuget", "zylobact", "febustat"],
    "telmisartan": ["micardis", "telma", "telsar", "sartel", "telvas", "cresar"],
    "folic acid": ["folate", "folvite", "folet", "folacin", "folitab", "obifolic"],
    "olmesartan": ["benicar", "olmat", "olmy", "benitec", "olmezest", "olsar"],
    "vildagliptin": ["galvus", "zomelis", "jalra", "vysov", "vildalip", "viladay"],
    "sitagliptin": ["januvia", "sitagen", "istamet", "janumet", "sitaglip", "trevia"],
    "metoprolol": ["lopresor", "metolar", "metocard", "betaloc", "meto-er", "metopro"],
    "glimepiride": ["amaryl", "glimpid", "glymex", "zoryl", "glimer", "diaglip"],
    "gliclazide": ["diamicron", "lycazid", "glizid", "reclide", "odinase", "glynase"],
    "ramipril": ["altace", "cardiopril", "cardace", "ramiril", "celapres", "ramace"],
    "nebivolol": ["bystolic", "nebistar", "nebicard", "nebilong", "nebilet", "nubeta"],
    "cilnidipine": ["cilacar", "cinod", "ciladay", "neudipine", "cilaheart", "cidip"],
    "rabeprazole": ["aciphex", "rablet", "rabicip", "razo", "raboz", "pepcia"],
    "dexamethasone": ["decadron", "dexona", "dexamycin", "dexacort", "decilone", "dexasone"],
    "doxofylline": ["doxolin", "synasma", "doxobid", "doxovent", "doxoril", "doxfree"],
    "deflazacort": ["dezacor", "defcort", "defza", "xenocort", "flacort", "defolet"],
    "ondansetron": ["zofran", "ondem", "emeset", "vomitrol", "zondem", "ondemet"],
    "domperidone": ["motilium", "domstal", "vomistop", "dompan", "dompy", "domcolic"],
    "pantoprazole": ["pantocid", "pantop", "pantodac", "panto", "pan-d", "pantozol"],
    "mefenamic acid": ["ponstan", "meftal", "meflam", "mefkind", "rafen", "mefgesic"],
    "aceclofenac": ["aceclo", "hifenac", "zerodol", "movon", "aceclo-plus", "acebid"],
    "nimesulide": ["nise", "nimulid", "nimek", "nimica", "nimcet", "nimsaid"],
    "hydroxyzine": ["atarax", "anxnil", "hyzox", "hydryllin", "anxipar", "hydrax"],
    "amlodipine + atenolol": ["amlokind-at", "amtas-at", "stamlo-beta", "tenolam", "amlopress-at"],
    "telmisartan + hydrochlorothiazide": ["telma-h", "telsar-h", "telvas-h", "tazloc-h", "telista-h"],
    "sulfamethoxazole + trimethoprim": ["bactrim", "septran", "cotrim", "sepmax", "oriprim"],
    "amoxicillin + clavulanic acid": ["augmentin", "moxclav", "megaclox", "clavam", "hiclav", "clavum"],
    "ofloxacin": ["oflox", "oflin", "tarivid", "zenflox", "oflacin", "exocin"],
    "torsemide": ["demadex", "dytor", "tide", "torlactone", "presage", "tomide"],
    "chlorthalidone": ["thalitone", "clorpres", "cloress", "natrilix", "thaloride"],
    "ivermectin": ["stromectol", "ivermect", "ivecop", "ivepred", "scabo", "ivernex"],
    "rifaximin": ["xifaxan", "rifagut", "rcifax", "rifakem", "rifamide"],
    "nitrofurantoin": ["furadantin", "niftran", "nitrofur", "furadoine", "nidantin"],
    "betahistine": ["serc", "vertin", "betaserc", "vertigo", "beta", "histiwel"],
    "etizolam": ["etilaam", "etizola", "sedekopan", "etizaa", "etzee", "etova"],
    "clotrimazole": ["candid", "clotri", "mycomax", "candiderma", "candifun", "clotop"],
    "ketoconazole": ["nizoral", "sebizole", "ketoz", "fungicide", "ketomac", "ketostar"],
    "fluconazole": ["diflucan", "flucz", "forcan", "syscan", "zocon", "flucos"],
    "pregabalin": ["lyrica", "pregeb", "maxgalin", "nervalin", "pregastar", "pregica"],
    "methylprednisolone": ["medrol", "methylpred", "depo-medrol", "solu-medrol", "depopred", "medrate"],
    "levetiracetam": ["keppra", "levesam", "levroxa", "levipil", "levecetam", "epictal"],
    
    # Additional common Indian medications for better accuracy
    "vitamin b12": ["methylcobalamin", "mecobalamin", "mecoblend", "neurobion", "nervijen"],
    "calcium": ["calcium carbonate", "calcit", "shelcal", "calcimax", "calci", "tums"],
    "iron": ["ferrous sulfate", "ferrous", "fefol", "orofer", "ferium", "hemfer"],
    "vitamin d3": ["cholecalciferol", "calciferol", "vitd3", "uprise", "calcirol", "d-rise"],
    "multivitamin": ["multi-vitamin", "becosules", "revital", "supradyn", "zincovit", "a to z"],
    "diphenhydramine": ["benadryl", "diphen", "dimenhydrinate", "diphenyl", "allergy"],
    "chlorpheniramine": ["chlorphen", "allergex", "chlor-trimeton", "allercet", "chloramine"],
    "pseudoephedrine": ["sudafed", "pseudo", "sudogest", "decongestant"],
    "guaifenesin": ["mucinex", "guai", "expectorant", "robitussin"],
    "codeine": ["codeine phosphate", "coughsyrup", "cough-syrup"],
    "promethazine": ["phenergan", "promed", "phenadoz", "prometh"],
    "clarithromycin": ["biaxin", "klaricid", "clari", "claribid", "klacid"],
    "levofloxacin": ["levaquin", "levoflox", "levo", "levobact", "tavanic"],
    "moxifloxacin": ["avelox", "moxif", "moxiflox", "moxiforce", "vigamox"],
    "linezolid": ["zyvox", "linospan", "linezid", "linezo", "lizolid"],
    "vancomycin": ["vancocin", "vanco", "vancomix"],
    "enalapril": ["vasotec", "enam", "enace", "cardiopril", "envas"],
    "perindopril": ["coversyl", "perigard", "preterax", "perindo"],
    "bisoprolol": ["zebeta", "concor", "biselect", "biso", "bisoheart"],
    "diltiazem": ["cardizem", "dilt", "dilzem", "dilcontin", "diltime"],
    "verapamil": ["calan", "isoptin", "verapress", "verap"],
    "spironolactone": ["aldactone", "spiro", "spiroctan", "aldace", "spiromide"],
    "eplerenone": ["inspra", "planep", "elep"],
    "isosorbide": ["imdur", "monoket", "iso", "isordil", "angised"],
    "nitroglycerin": ["nitrostat", "nitro", "angised", "glyceryl", "nitrate"],
    "warfarin": ["coumadin", "jantoven", "warf", "warfex", "warfrant", "uniwarfin"],
    "dabigatran": ["pradaxa", "dabixa", "dabiga"],
    "rivaroxaban": ["xarelto", "rivarox", "rixar"],
    "apixaban": ["eliquis", "apixab"],
    "enoxaparin": ["lovenox", "clexane", "enoxap"],
    "heparin": ["hep", "heparin sodium", "fluxum"],
    "digoxin": ["lanoxin", "digox", "cardoxin"],
    "ivabradine": ["coralan", "ivabrad", "ivaheart", "ivanode"],
    "sacubitril": ["entresto", "lcz", "sacubit"],
    "insulin glargine": ["lantus", "basalog", "glaritus", "reglaris"],
    "insulin aspart": ["novolog", "novorapid", "fiasp", "aspart"],
    "insulin lispro": ["humalog", "admelog", "lispro"],
    "pioglitazone": ["actos", "pionorm", "pioz", "glustin"],
    "empagliflozin": ["jardiance", "empa", "empaglyn"],
    "dapagliflozin": ["forxiga", "farxiga", "dapa"],
    "canagliflozin": ["invokana", "cana"],
    "linagliptin": ["tradjenta", "lina", "trajenta"],
    "saxagliptin": ["onglyza", "saxa"],
    "alogliptin": ["nesina", "vipidia", "alo"],
    "repaglinide": ["prandin", "rep"],
    "nateglinide": ["starlix", "nate"],
    "acarbose": ["precose", "glucobay", "accarb"],
    "miglitol": ["glyset", "mig"],
    "levothyroxine": ["synthroid", "levothy", "levothyrox", "levoxyl", "tirosint", "euthyrox", "thyronorm", "eltroxin"],
    "thyroxine": ["thyroid", "t4", "thyrox"],
    "propylthiouracil": ["ptu", "propyl"],
    "methimazole": ["tapazole", "methi"],
    "salbutamol": ["albuterol", "ventolin", "proventil", "asthalin", "ventofort"],
    "salmeterol": ["serevent", "salmet"],
    "formoterol": ["foradil", "oxis", "form"],
    "tiotropium": ["spiriva", "tiotrop"],
    "budesonide": ["pulmicort", "budecort", "budes"],
    "fluticasone": ["flonase", "flovent", "fluti"],
    "beclomethasone": ["qvar", "beclo", "becosules"],
    "ipratropium": ["atrovent", "ipra"],
    "theophylline": ["theo", "uniphyl", "deriphylline"],
    "aminophylline": ["amino", "phyllin"],
    "prednisone": ["deltasone", "predni", "orasone", "predcip", "omnacortil", "wysolone"],
    "hydrocortisone": ["cortef", "hydrocort", "solu-cortef"],
    "betamethasone": ["celestone", "beta", "betaderm"],
    "triamcinolone": ["kenalog", "tria"],
    "dexamethasone": ["decadron", "dexona", "dexamycin", "dexacort", "decilone", "dexasone"],
    "cyclosporine": ["neoral", "sandimmune", "cyclo"],
    "tacrolimus": ["prograf", "advagraf", "tacro"],
    "mycophenolate": ["cellcept", "mycophen", "myfortic"],
    "azathioprine": ["imuran", "azoran", "azathio"],
    "rituximab": ["rituxan", "mabthera", "ritux"],
    "infliximab": ["remicade", "infli"],
    "adalimumab": ["humira", "ada"],
    "etanercept": ["enbrel", "eta"],
    "methotrexate": ["rheumatrex", "trexall", "metho"],
    "allopurinol": ["zyloprim", "allop", "purinol", "zyrik"],
    "colchicine": ["colcrys", "colch"],
    "probenecid": ["benemid", "prob"],
    "tamsulosin": ["flomax", "tamsul", "urimax"],
    "finasteride": ["proscar", "propecia", "finas"],
    "dutasteride": ["avodart", "duta"],
    "sildenafil": ["viagra", "revatio", "silagra", "sild"],
    "tadalafil": ["cialis", "adcirca", "tada"],
    "vardenafil": ["levitra", "vard"],
    "baclofen": ["lioresal", "bacl"],
    "tizanidine": ["zanaflex", "tiz"],
    "cyclobenzaprine": ["flexeril", "cyclo"],
    "carisoprodol": ["soma", "caris"],
    "methocarbamol": ["robaxin", "metho"],
    "orphenadrine": ["norflex", "orph"],
    "phenytoin": ["dilantin", "pheny", "eptoin"],
    "carbamazepine": ["tegretol", "carba", "carbatol"],
    "valproic acid": ["depakote", "valproate", "valp", "divalproex"],
    "topiramate": ["topamax", "topira"],
    "zonisamide": ["zonegran", "zon"],
    "oxcarbazepine": ["trileptal", "oxcarb"],
    "lacosamide": ["vimpat", "laco"],
    "perampanel": ["fycompa", "per"],
    "lamotrigine": ["lamictal", "lamot", "lamotrigin", "lamogard", "lamitor", "lametec"],
    "phenobarbital": ["luminal", "pheno", "gardenal"],
    "primidone": ["mysoline", "prim"],
    "clonazepam": ["klonopin", "rivotril", "clon", "petril", "clonopam", "lonazep"],
    "lorazepam": ["ativan", "lora", "loraz"],
    "diazepam": ["valium", "valpam", "dizac", "calmpose", "zepose", "sedopam"],
    "alprazolam": ["xanax", "alprax", "tafil", "alp", "alzolam", "zolax", "restyl", "trika"],
    "bromazepam": ["lexotan", "brom"],
    "oxazepam": ["serax", "oxa"],
    "temazepam": ["restoril", "tema"],
    "zolpidem": ["ambien", "zolp", "zolfresh"],
    "zopiclone": ["imovane", "zopi"],
    "eszopiclone": ["lunesta", "eszo"],
    "suvorexant": ["belsomra", "suvo"],
    "melatonin": ["mel", "circadin", "sleepe"],
    "diphenhydramine": ["benadryl", "diphen", "allergy", "somna"],
    
    # Common dosage units
    "milligram": ["mg", "mgs", "millig", "milligram"],
    "microgram": ["mcg", "µg", "microg"],
    "gram": ["g", "gm", "gms", "gram"],
    "milliliter": ["ml", "mls", "millil"],
    
    # Common frequency terms
    "once daily": ["qd", "od", "daily", "once a day", "1 time a day", "1x day"],
    "twice daily": ["bid", "bd", "twice a day", "2 times a day", "2x day"],
    "three times daily": ["tid", "tds", "3 times a day", "3x day"],
    "four times daily": ["qid", "qds", "4 times a day", "4x day"],
    "every morning": ["qam", "morn", "morning"],
    "every night": ["qhs", "qpm", "noct", "night", "bedtime", "bed time"],
    "every hour": ["q1h", "hourly"],
    "every 4 hours": ["q4h", "4 hourly", "every 4 hrs"],
    "every 6 hours": ["q6h", "6 hourly", "every 6 hrs"],
    "every 8 hours": ["q8h", "8 hourly", "every 8 hrs"],
    "every 12 hours": ["q12h", "12 hourly", "every 12 hrs"],
    "as needed": ["prn", "pro re nata", "as required", "when necessary", "sos"],
    
    # Common routes of administration
    "by mouth": ["po", "oral", "orally", "per os"],
    "intravenous": ["iv", "i.v.", "ivp", "iv push"],
    "intramuscular": ["im", "i.m.", "intramuscul"],
    "subcutaneous": ["sc", "s.c.", "subq", "sub q", "subcu"],
    "sublingual": ["sl", "s.l.", "sublingual"],
    "topical": ["top", "topical", "externally"],
    "inhalation": ["inh", "inhale", "breathing"],
    
    # Common prescription instructions
    "with food": ["w/ food", "with meals", "with meal", "ac", "pc"],
    "before meals": ["ac", "a.c.", "before food"],
    "after meals": ["pc", "p.c.", "after food"],
    "with water": ["w/ water", "with h2o"],
    "do not crush": ["no crush", "donot crush", "do not chew", "swallow whole"],
    "take with plenty of water": ["take w/ plenty of h2o", "take w/ plenty of water"],
    "dissolve in water": ["dissolve", "dissolved in water"],
    "until finished": ["until gone", "to completion", "complete course"],
    "shake well": ["shake bottle", "mix well", "agitate"],
}

def apply_medical_dictionary_correction(text):
    """Apply medical dictionary correction to OCR text with improved fuzzy matching"""
    if not text:
        return text
        
    words = re.findall(r'\b\w+\b', text.lower())
    corrected_text = text
    corrections_made = {}
    
    for word in words:
        # Skip very short words, numbers, or already corrected words
        if len(word) < 3 or word.isdigit() or word in corrections_made:
            continue
            
        # Find the best match in our medication dictionary
        best_match = None
        best_score = 0
        best_key = None
        
        for key, aliases in MEDICATION_DICT.items():
            # Skip non-medication entries
            if key in ["milligram", "microgram", "gram", "milliliter", 
                       "once daily", "twice daily", "three times daily", "four times daily"]:
                continue
            
            # Check the key itself with ratio and partial_ratio
            ratio_score = fuzz.ratio(word, key.lower())
            partial_score = fuzz.partial_ratio(word, key.lower())
            score = max(ratio_score, partial_score)
            
            if score > best_score and score > 70:  # Reduced threshold to 70%
                best_score = score
                best_match = key
                best_key = key
                
            # Check aliases
            for alias in aliases:
                if len(alias) < 3:
                    continue
                    
                ratio_score = fuzz.ratio(word, alias.lower())
                partial_score = fuzz.partial_ratio(word, alias.lower())
                score = max(ratio_score, partial_score)
                
                if score > best_score and score > 70:  # Reduced threshold to 70%
                    best_score = score
                    best_match = key  # Use the standardized term, not the alias
                    best_key = key
        
        if best_match and best_score > 70:
            # Replace the word with the correct spelling
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            corrected_text = pattern.sub(best_match, corrected_text)
            corrections_made[word] = best_match
            print(f"[CORRECTION] '{word}' -> '{best_match}' (score: {best_score})")
    
    return corrected_text

def preprocess_image(image_path):
    """Advanced image preprocessing for prescription OCR with multiple enhancement techniques."""
    try:
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Step 1: Deskew/Rotation correction
        coords = np.column_stack(np.where(gray > 0))
        if len(coords) > 0:
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            if abs(angle) > 0.5:  # Only rotate if angle is significant
                (h, w) = gray.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
        # Step 2: Increase contrast using histogram equalization
        gray = cv2.equalizeHist(gray)
        
        # Step 3: Apply CLAHE for better local contrast
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Step 4: Bilateral filter for edge-preserving noise reduction
        bilateral = cv2.bilateralFilter(enhanced, 11, 90, 90)
        
        # Step 5: Apply multiple denoising techniques
        # Non-local means denoising
        denoised = cv2.fastNlMeansDenoising(bilateral, h=8, templateWindowSize=7, searchWindowSize=21)
        
        # Step 6: Sharpen the image using unsharp masking
        gaussian = cv2.GaussianBlur(denoised, (0, 0), 2.0)
        sharpened = cv2.addWeighted(denoised, 2.0, gaussian, -1.0, 0)
        
        # Step 7: Apply adaptive thresholding with multiple methods
        # Method 1: Gaussian adaptive threshold
        thresh_gaussian = cv2.adaptiveThreshold(
            sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 21, 4
        )
        
        # Method 2: Otsu's thresholding
        _, thresh_otsu = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Combine both thresholding methods
        combined_thresh = cv2.bitwise_and(thresh_gaussian, thresh_otsu)
        
        # Step 8: Morphological operations to clean up
        # Remove small noise
        kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        opened = cv2.morphologyEx(combined_thresh, cv2.MORPH_OPEN, kernel_open, iterations=1)
        
        # Close small gaps
        kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        processed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel_close, iterations=1)
        
        # Step 9: Dilate slightly to make text more connected
        kernel_dilate = np.ones((1, 1), np.uint8)
        processed = cv2.dilate(processed, kernel_dilate, iterations=1)
        
        # Create filename for enhanced image
        base_name = os.path.basename(image_path)
        dir_name = os.path.dirname(image_path)
        enhanced_name = f"enhanced_{base_name}"
        enhanced_path = os.path.join(dir_name, enhanced_name)
        
        # Save enhanced image
        cv2.imwrite(enhanced_path, processed)
        
        return {
            "original": image_path,
            "enhanced": enhanced_path,
            "processed_image": processed
        }
    except Exception as e:
        print(f"Error in image preprocessing: {str(e)}")
        return None

def run_multiple_ocr_passes(image_data):
    """Run multiple OCR passes with different preprocessing settings (with debug logging)"""
    try:
        print("[DEBUG] Starting run_multiple_ocr_passes...")
        results = []
        
        # Multiple Tesseract configurations for better results
        configs = [
            '--oem 1 --psm 6 -c preserve_interword_spaces=1',  # LSTM, uniform block
            '--oem 1 --psm 3 -c preserve_interword_spaces=1',  # LSTM, auto page segmentation
            '--oem 1 --psm 11 -c preserve_interword_spaces=1',  # LSTM, sparse text
            '--oem 1 --psm 12 -c preserve_interword_spaces=1',  # LSTM, sparse text with OSD
        ]
        
        def ocr_with_preprocessing(img, conf=0.8, config_idx=0):
            if img is None:
                return None
            # 1. Grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization) - improved parameters
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            # 3. Bilateral filtering for edge-preserving denoising
            bilateral = cv2.bilateralFilter(enhanced, 9, 75, 75)
            # 4. Non-local means denoising with optimized h parameter
            denoised = cv2.fastNlMeansDenoising(bilateral, h=10)
            # 5. Adaptive Threshold with better parameters
            thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 3)
            # 6. OCR with improved config
            tesseract_config = configs[config_idx] if config_idx < len(configs) else configs[0]
            text = pytesseract.image_to_string(thresh, lang='eng', config=tesseract_config)
            if text.strip():
                return [[(None, [text.strip(), conf])]]
            return None

        # Pass 1: Enhanced image with config 0
        if 'enhanced' in image_data and image_data['enhanced']:
            print("[DEBUG] Pass 1: Enhanced image with PSM 6 (uniform block)...")
            img = cv2.imread(image_data['enhanced'])
            result = ocr_with_preprocessing(img, conf=0.92, config_idx=0)
            if result:
                results.append(result)

        # Pass 2: Enhanced image with config 1 (auto page segmentation)
        if 'enhanced' in image_data and image_data['enhanced']:
            print("[DEBUG] Pass 2: Enhanced image with PSM 3 (auto page)...")
            img = cv2.imread(image_data['enhanced'])
            result = ocr_with_preprocessing(img, conf=0.90, config_idx=1)
            if result:
                results.append(result)

        # Pass 3: Original image with config 0
        if 'original' in image_data and image_data['original']:
            print("[DEBUG] Pass 3: Original image with PSM 6...")
            img = cv2.imread(image_data['original'])
            result = ocr_with_preprocessing(img, conf=0.88, config_idx=0)
            if result:
                results.append(result)

        # Pass 4: Original image with config 2 (sparse text)
        if 'original' in image_data and image_data['original']:
            print("[DEBUG] Pass 4: Original image with PSM 11 (sparse text)...")
            img = cv2.imread(image_data['original'])
            result = ocr_with_preprocessing(img, conf=0.86, config_idx=2)
            if result:
                results.append(result)

        # Inverted image pass
        if len(results) == 0 and 'enhanced' in image_data and image_data['enhanced']:
            print("[DEBUG] Trying inverted image OCR with Tesseract (advanced preprocessing)...")
            enhanced_img = cv2.imread(image_data['enhanced'])
            if enhanced_img is not None:
                inverted = cv2.bitwise_not(enhanced_img)
                result = ocr_with_preprocessing(inverted, conf=0.85)
                if result:
                    results.append(result)

        # Raw fallback (no thresholding, just grayscale)
        if len(results) == 0 and 'original' in image_data and image_data['original']:
            print("[DEBUG] Trying raw grayscale OCR fallback...")
            img = cv2.imread(image_data['original'])
            if img is not None:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray, lang='eng', config=tesseract_config)
                if text.strip():
                    results.append([[ (None, [text.strip(), 0.7]) ]])
        # If still no results, return an empty placeholder result that won't break the system
        if len(results) == 0:
            print("[ERROR] No OCR results from any pass.")
            return [{"confidence": 0.0, "empty": True}]
        print("[DEBUG] run_multiple_ocr_passes complete.")
        return results
    except Exception as e:
        print(f"[ERROR] Error in OCR passes: {str(e)}")
        # Return a placeholder empty result that can be safely processed
        return [{"confidence": 0.0, "empty": True}]

def combine_ocr_results(results):
    """Combine text from multiple OCR passes, handling improved empty results and printing raw output for debugging"""
    try:
        print(f"[DEBUG] Raw OCR results: {results}")
        if not results:
            return "", None
        # Handle empty placeholder result
        if len(results) == 1 and isinstance(results[0], dict) and results[0].get("empty", False):
            return "", 0.0
        all_text = []
        confidence_scores = []
        for result_set in results:
            # Defensive: result_set should be a list of lines, but may be empty or malformed
            if result_set and isinstance(result_set, list):
                for line in result_set[0] if result_set and len(result_set) > 0 else []:
                    # Defensive: line should be a tuple/list with at least 2 elements
                    if isinstance(line, (list, tuple)) and len(line) >= 2 and isinstance(line[1], (list, tuple)) and len(line[1]) >= 2:
                        all_text.append(line[1][0])  # text
                        try:
                            confidence_scores.append(float(line[1][1]))  # confidence
                        except Exception:
                            pass
        if not all_text:
            return "", None
        combined_text = "\n".join(all_text)
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.5
        return combined_text.strip(), avg_confidence
    except Exception as e:
        print(f"Error combining OCR results: {str(e)}")
        return "", None

def extract_medical_entities(text):
    """Extract medical entities from the text with enhanced fuzzy matching"""
    medications = []
    dosages = []
    frequencies = []
    routes = []
    
    # Convert text to lowercase for better matching
    text_lower = text.lower()
    
    # Use spaCy for entity recognition if available
    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["CHEMICAL", "DRUG", "MEDICATION"]:
                # Extract only the medication name without dosage or frequency
                med_name = re.sub(r'\s+\d+\s*\w*\b', '', ent.text) # Remove numbers and units
                med_name = re.sub(r'\b(once|twice|three|four)(\s+times)?\s+(daily|a\s+day)\b', '', med_name, flags=re.IGNORECASE)
                med_name = re.sub(r'\b(every|each)\s+(morning|evening|night|day|hour|hourly)\b', '', med_name, flags=re.IGNORECASE)
                med_name = re.sub(r'\b(qd|bid|tid|qid|prn|od|q\d+h)\b', '', med_name, flags=re.IGNORECASE)
                med_name = med_name.strip()
                if med_name and len(med_name) > 2:  # Ensure we have a reasonable name (not just a unit or directive)
                    medications.append(med_name.lower())
    
    # Extract medications using our dictionary with fuzzy matching
    text_words = re.findall(r'\b[a-z]{3,}\b', text_lower)  # Get all words with 3+ characters
    
    for key in MEDICATION_DICT.keys():
        # Skip dosage units, frequency terms, routes, and instructions
        if key in ["milligram", "microgram", "gram", "milliliter", 
                   "once daily", "twice daily", "three times daily", "four times daily",
                   "every morning", "every night", "every hour", "every 4 hours",
                   "every 6 hours", "every 8 hours", "every 12 hours", "as needed",
                   "by mouth", "intravenous", "intramuscular", "subcutaneous",
                   "sublingual", "topical", "inhalation",
                   "with food", "before meals", "after meals", "with water",
                   "do not crush", "take with plenty of water", "dissolve in water",
                   "until finished", "shake well"]:
            continue
        
        # Try exact match first (case-insensitive)
        if key in text_lower:
            medications.append(key)
            continue
            
        # Check all aliases for exact matches
        alias_found = False
        for alias in MEDICATION_DICT[key]:
            if alias in text_lower:
                medications.append(key)  # Add the standardized term
                alias_found = True
                break
        
        if alias_found:
            continue
        
        # Try fuzzy matching for each word in the text
        for word in text_words:
            if len(word) < 4:  # Skip very short words
                continue
                
            # Check medication name fuzzy match (70% threshold)
            if fuzz.ratio(word, key) >= 70:
                medications.append(key)
                break
            
            # Check partial match (substring with good ratio)
            if len(key) >= 5 and (word in key or key in word):
                if fuzz.partial_ratio(word, key) >= 75:
                    medications.append(key)
                    break
            
            # Check aliases with fuzzy matching
            for alias in MEDICATION_DICT[key]:
                if len(alias) < 4:
                    continue
                    
                # Fuzzy match with alias (70% threshold)
                if fuzz.ratio(word, alias) >= 70:
                    medications.append(key)
                    alias_found = True
                    break
                
                # Partial match with alias
                if len(alias) >= 5 and (word in alias or alias in word):
                    if fuzz.partial_ratio(word, alias) >= 75:
                        medications.append(key)
                        alias_found = True
                        break
            
            if alias_found:
                break
    
    # Pattern for dosage (number + unit)
    dosage_pattern = r'\b(\d+[\.\d]*)\s*(mg|mcg|mL|g|mg/mL|mEq|units|tablets?|caps?)\b'
    dosage_matches = re.finditer(dosage_pattern, text, re.IGNORECASE)
    for match in dosage_matches:
        dosages.append(match.group(0))
    
    # Pattern for frequencies
    freq_patterns = [
        r'\b(once|twice|three times|four times)\s+daily\b',
        r'\b(q\.?d|b\.?i\.?d|t\.?i\.?d|q\.?i\.?d)\b',
        r'\b(every|each)\s+(\d+)\s+(hours?|days?)\b',
        r'\b(q)(\d+)(h)\b',
        r'\bprn\b',
        r'\bas needed\b'
    ]
    
    for pattern in freq_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            frequencies.append(match.group(0))
    
    # Pattern for routes of administration
    route_patterns = [
        r'\b(oral(ly)?|by mouth|p\.?o\.)\b',
        r'\b(intravenous|i\.?v\.)\b',
        r'\b(intramuscular|i\.?m\.)\b',
        r'\b(subcutaneous|s\.?c\.|sub-q)\b',
        r'\b(topical(ly)?)\b',
        r'\b(sublingual|s\.?l\.)\b'
    ]
    
    for pattern in route_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            routes.append(match.group(0))
    
    # Clean medication names to remove any residual dosage or frequency info
    clean_medications = []
    for med in medications:
        # Remove dosage and frequency information
        clean_med = re.sub(r'\s+\d+\s*\w*\b', '', med).strip()
        clean_med = re.sub(r'\b(once|twice|three|four)(\s+times)?\s+(daily|a\s+day)\b', '', clean_med, flags=re.IGNORECASE).strip()
        clean_med = re.sub(r'\b(every|each)\s+(morning|evening|night|day|hour|hourly)\b', '', clean_med, flags=re.IGNORECASE).strip()
        clean_med = re.sub(r'\b(qd|bid|tid|qid|prn|od|q\d+h)\b', '', clean_med, flags=re.IGNORECASE).strip()
        
        if clean_med and len(clean_med) > 2:  # Ensure we have a meaningful name
            clean_medications.append(clean_med)
    
    return {
        "medications": list(set(clean_medications)),
        "dosages": list(set(dosages)),
        "frequencies": list(set(frequencies)),
        "routes": list(set(routes))
    }

def process_prescription_with_enhanced_ocr(image_path, output_dir=None):
    """Process a prescription image with enhanced OCR techniques (with debug logging)"""
    try:
        print(f"[DEBUG] Starting OCR processing for: {image_path}")
        # Prepare output paths
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_name = os.path.basename(image_path)
            base_name_no_ext = os.path.splitext(base_name)[0]
            enhanced_path = os.path.join(output_dir, f"enhanced_{base_name}")
            results_path = os.path.join(output_dir, f"{base_name_no_ext}_results.json")
        else:
            enhanced_path = None
            results_path = None
        print("[DEBUG] Output paths prepared.")
        # STEP 1: Apply simple image preprocessing
        image_data = preprocess_image(image_path)
        print("[DEBUG] Image preprocessing complete.")
        if not image_data:
            print("[ERROR] Failed to preprocess image.")
            return {
                "error": "Failed to preprocess image",
                "raw_text": "",
                "cleaned_text": "",
                "medications": [],
                "dosages": [],
                "frequencies": [],
                "routes": []
            }
        # STEP 2: Run multiple OCR passes with different preprocessing
        print("[DEBUG] Running multiple OCR passes...")
        ocr_results = run_multiple_ocr_passes(image_data)
        print("[DEBUG] OCR passes complete.")
        # STEP 3: Combine text from all OCR passes
        raw_text, confidence = combine_ocr_results(ocr_results)
        print(f"[DEBUG] Combined OCR text: {raw_text[:100]}... (truncated)")
        # Return a basic structure even if text extraction fails
        if not raw_text:
            print("[ERROR] No text extracted from OCR.")
            return {
                "image_path": image_path,
                "preprocessed_image": image_data.get("enhanced", ""),
                "raw_text": "",
                "cleaned_text": "",
                "medications": [],
                "dosages": [],
                "frequencies": [],
                "routes": [],
                "confidence": confidence if confidence is not None else 50.0,
            }
        # STEP 4: Apply medical dictionary correction
        print("[DEBUG] Applying medical dictionary correction...")
        corrected_text = apply_medical_dictionary_correction(raw_text)
        # STEP 5: Extract medical entities
        print("[DEBUG] Extracting medical entities...")
        entities = extract_medical_entities(corrected_text)
        # Build the results
        results = {
            "image_path": image_path,
            "preprocessed_image": image_data["enhanced"],
            "raw_text": raw_text,
            "cleaned_text": corrected_text,
            "medications": entities["medications"],
            "dosages": entities["dosages"],
            "frequencies": entities["frequencies"],
            "routes": entities["routes"],
            "confidence": float(confidence) * 100 if confidence else 90.0,
        }
        # Save results to file if output_dir is provided
        if results_path:
            try:
                with open(results_path, 'w') as f:
                    json.dump(results, f, indent=4)
            except Exception as e:
                print(f"Error saving results: {str(e)}")
        print("[DEBUG] OCR processing complete.")
        return results
    except Exception as e:
        print(f"[ERROR] Error in OCR processing: {str(e)}")
        return {
            "error": f"Processing error: {str(e)}",
            "raw_text": "",
            "cleaned_text": "",
            "medications": [],
            "dosages": [],
            "frequencies": [],
            "routes": []
        }

def extract_prescription_text(image_path):
    """
    Extracts plain text from a prescription image using Tesseract OCR.
    Args:
        image_path (str): Path to the prescription image.
    Returns:
        str: Extracted text from the image.
    """
    print(f"[DEBUG] Extracting text from image with Tesseract: {image_path}")
    img = cv2.imread(image_path)
    if img is None:
        print("[ERROR] Could not read image for Tesseract OCR.")
        return ""
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Optional: Apply thresholding for better results
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Run Tesseract OCR
    text = pytesseract.image_to_string(thresh, lang='eng')
    print(f"[DEBUG] Extracted text: {text[:100]}... (truncated)")
    return text.strip()

# If running as a script
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Prescription OCR with PaddleOCR")
    parser.add_argument("--image", "-i", required=True, help="Path to prescription image")
    parser.add_argument("--output", "-o", default="./output", help="Output directory for results")
    
    args = parser.parse_args()
    
    print("===== Enhanced Prescription OCR Processing =====")
    print(f"Processing image: {args.image}")
    
    # Process the prescription
    results = process_prescription_with_enhanced_ocr(args.image, args.output)
    
    # Print the results
    if "error" in results:
        print(f"Error: {results['error']}")
    else:
        print("\n===== OCR Results =====")
        print(f"Preprocessed image: {results['preprocessed_image']}")
        
        print("\nExtracted text:")
        print(results['raw_text'])
        
        print("\nCleaned text:")
        print(results['cleaned_text'])
        
        print("\nDetected medications:")
        if results['medications']:
            for med in results['medications']:
                print(f"- {med}")
        else:
            print("No medications detected")
            
        print("\nDetected dosages:")
        if results['dosages']:
            for dosage in results['dosages']:
                print(f"- {dosage}")
        else:
            print("No dosages detected")
            
        print("\nDetected frequencies:")
        if results['frequencies']:
            for freq in results['frequencies']:
                print(f"- {freq}")
        else:
            print("No frequencies detected")
            
        print("\nDetected routes:")
        if results['routes']:
            for route in results['routes']:
                print(f"- {route}")
        else:
            print("No routes detected")
        
        print(f"\nConfidence: {results['confidence']:.1f}%")
        
        print("\nProcessing complete!")
