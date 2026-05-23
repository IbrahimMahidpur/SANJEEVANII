// Complete Indore Pharmacy Database - 50+ Pharmacies across all major areas
// Each pharmacy has realistic medicine inventory from 25,000+ database

export const INDORE_PHARMACIES = [
  // MG Road & City Center Area
  { id: 'IND_001', name: 'Apollo Pharmacy', address: 'MG Road, Indore 452001', location: { lat: 22.7196, lng: 75.8577 }, phone: '+91 731 2530001', isOpen: true, rating: 4.5, totalRatings: 250, inventorySize: 'large' },
  { id: 'IND_002', name: 'MedPlus Pharmacy', address: 'Sapna Sangeeta Road, Indore 452001', location: { lat: 22.7167, lng: 75.8545 }, phone: '+91 731 2530002', isOpen: true, rating: 4.3, totalRatings: 180, inventorySize: 'medium' },
  { id: 'IND_003', name: 'Wellness Forever', address: 'Treasure Island Mall, Indore 452001', location: { lat: 22.7189, lng: 75.8598 }, phone: '+91 731 2530003', isOpen: true, rating: 4.6, totalRatings: 320, inventorySize: 'large' },
  { id: 'IND_004', name: 'PharmEasy Store', address: 'Manorama Ganj, Indore 452001', location: { lat: 22.7178, lng: 75.8498 }, phone: '+91 731 2530004', isOpen: true, rating: 4.4, totalRatings: 210, inventorySize: 'medium' },
  { id: 'IND_005', name: 'Netmeds Pharmacy', address: 'Palasia Square, Indore 452001', location: { lat: 22.7205, lng: 75.8642 }, phone: '+91 731 2530005', isOpen: true, rating: 4.2, totalRatings: 150, inventorySize: 'small' },

  // AB Road Area
  { id: 'IND_006', name: 'HealthKart Pharmacy', address: 'AB Road, Indore 452008', location: { lat: 22.7244, lng: 75.8721 }, phone: '+91 731 2530006', isOpen: true, rating: 4.7, totalRatings: 380, inventorySize: 'large' },
  { id: 'IND_007', name: 'Guardian Pharmacy', address: 'LIG Square, AB Road, Indore 452008', location: { lat: 22.7267, lng: 75.8789 }, phone: '+91 731 2530007', isOpen: true, rating: 4.5, totalRatings: 290, inventorySize: 'medium' },
  { id: 'IND_008', name: 'Cure Plus Pharmacy', address: 'Geeta Bhawan, AB Road, Indore 452007', location: { lat: 22.7089, lng: 75.8734 }, phone: '+91 731 2530008', isOpen: true, rating: 4.1, totalRatings: 120, inventorySize: 'small' },

  // Vijay Nagar Area
  { id: 'IND_009', name: 'Sanjeevani Pharmacy', address: 'Vijay Nagar Main Road, Indore 452010', location: { lat: 22.7532, lng: 75.8937 }, phone: '+91 731 2530009', isOpen: true, rating: 4.3, totalRatings: 170, inventorySize: 'medium' },
  { id: 'IND_010', name: 'LifeCare Pharmacy', address: 'Scheme 54, Vijay Nagar, Indore 452010', location: { lat: 22.7456, lng: 75.8876 }, phone: '+91 731 2530010', isOpen: true, rating: 4.4, totalRatings: 200, inventorySize: 'medium' },
  { id: 'IND_011', name: 'MediCare Pharmacy', address: 'Meghdoot Garden, Vijay Nagar, Indore 452010', location: { lat: 22.7498, lng: 75.8912 }, phone: '+91 731 2530011', isOpen: true, rating: 4.2, totalRatings: 160, inventorySize: 'small' },
  { id: 'IND_012', name: 'Health Plus Pharmacy', address: 'Annapurna Road, Vijay Nagar, Indore 452009', location: { lat: 22.7312, lng: 75.8623 }, phone: '+91 731 2530012', isOpen: true, rating: 4.6, totalRatings: 310, inventorySize: 'large' },

  // Bhawarkua & Sudama Nagar
  { id: 'IND_013', name: 'City Pharmacy', address: 'Bhawarkua Main Road, Indore 452014', location: { lat: 22.7234, lng: 75.8912 }, phone: '+91 731 2530013', isOpen: true, rating: 4.0, totalRatings: 95, inventorySize: 'small' },
  { id: 'IND_014', name: 'Metro Pharmacy', address: 'Sudama Nagar, Indore 452009', location: { lat: 22.7387, lng: 75.8567 }, phone: '+91 731 2530014', isOpen: true, rating: 4.5, totalRatings: 240, inventorySize: 'medium' },
  { id: 'IND_015', name: 'Star Pharmacy', address: 'Bhawarkua Square, Indore 452014', location: { lat: 22.7256, lng: 75.8934 }, phone: '+91 731 2530015', isOpen: true, rating: 4.3, totalRatings: 185, inventorySize: 'medium' },

  // Rajendra Nagar & Nearby
  { id: 'IND_016', name: 'Prime Pharmacy', address: 'Rajendra Nagar Main, Indore 452012', location: { lat: 22.7123, lng: 75.8456 }, phone: '+91 731 2530016', isOpen: true, rating: 4.4, totalRatings: 220, inventorySize: 'medium' },
  { id: 'IND_017', name: 'Care Pharmacy', address: 'Rajendra Nagar Square, Indore 452012', location: { lat: 22.7145, lng: 75.8478 }, phone: '+91 731 2530017', isOpen: true, rating: 4.1, totalRatings: 130, inventorySize: 'small' },

  // Nipania & Kanadiya Road
  { id: 'IND_018', name: 'Wellness Pharmacy', address: 'Nipania Main Road, Indore 452010', location: { lat: 22.7598, lng: 75.9012 }, phone: '+91 731 2530018', isOpen: true, rating: 4.6, totalRatings: 295, inventorySize: 'large' },
  { id: 'IND_019', name: 'Medico Pharmacy', address: 'Kanadiya Road, Indore 452016', location: { lat: 22.7689, lng: 75.8912 }, phone: '+91 731 2530019', isOpen: true, rating: 4.2, totalRatings: 145, inventorySize: 'medium' },
  { id: 'IND_020', name: 'Remedy Pharmacy', address: 'C21 Mall, Kanadiya Road, Indore 452016', location: { lat: 22.7642, lng: 75.8934 }, phone: '+91 731 2530020', isOpen: true, rating: 4.5, totalRatings: 265, inventorySize: 'large' },

  // Tilak Nagar & Rau
  { id: 'IND_021', name: 'HealthFirst Pharmacy', address: 'Tilak Nagar Main, Indore 452018', location: { lat: 22.6987, lng: 75.8456 }, phone: '+91 731 2530021', isOpen: true, rating: 4.2, totalRatings: 145, inventorySize: 'small' },
  { id: 'IND_022', name: 'Rau Medical Store', address: 'Rau Market, Indore 453331', location: { lat: 22.6543, lng: 75.8123 }, phone: '+91 731 2530022', isOpen: true, rating: 4.1, totalRatings: 120, inventorySize: 'small' },

  // Indore GPO & Old City
  { id: 'IND_023', name: 'Central Pharmacy', address: 'Indore GPO, Indore 452001', location: { lat: 22.7156, lng: 75.8523 }, phone: '+91 731 2530023', isOpen: true, rating: 4.5, totalRatings: 265, inventorySize: 'large' },
  { id: 'IND_024', name: 'Old City Medical', address: 'Sarafa Bazaar, Indore 452002', location: { lat: 22.7198, lng: 75.8512 }, phone: '+91 731 2530024', isOpen: true, rating: 4.0, totalRatings: 180, inventorySize: 'medium' },

  // Super Corridor & New Areas
  { id: 'IND_025', name: 'Super Pharmacy', address: 'Super Corridor, Indore 452010', location: { lat: 22.7723, lng: 75.8945 }, phone: '+91 731 2530025', isOpen: true, rating: 4.7, totalRatings: 340, inventorySize: 'large' },
  { id: 'IND_026', name: 'Modern Medical Store', address: 'Bypass Road, Indore 452016', location: { lat: 22.7812, lng: 75.9023 }, phone: '+91 731 2530026', isOpen: true, rating: 4.4, totalRatings: 210, inventorySize: 'medium' },

  // Bengali Square & Nearby
  { id: 'IND_027', name: 'Bengali Square Pharmacy', address: 'Bengali Square, Indore 452016', location: { lat: 22.7567, lng: 75.9134 }, phone: '+91 731 2530027', isOpen: true, rating: 4.3, totalRatings: 190, inventorySize: 'medium' },
  { id: 'IND_028', name: 'Orbit Medical', address: 'Near Bengali Square, Indore 452016', location: { lat: 22.7589, lng: 75.9156 }, phone: '+91 731 2530028', isOpen: true, rating: 4.2, totalRatings: 165, inventorySize: 'small' },

  // Khajrana & Nearby
  { id: 'IND_029', name: 'Khajrana Pharmacy', address: 'Khajrana Main Road, Indore 452018', location: { lat: 22.6923, lng: 75.8678 }, phone: '+91 731 2530029', isOpen: true, rating: 4.4, totalRatings: 220, inventorySize: 'medium' },
  { id: 'IND_030', name: 'Temple Medical Store', address: 'Near Khajrana Ganesh Temple, Indore 452018', location: { lat: 22.6945, lng: 75.8698 }, phone: '+91 731 2530030', isOpen: true, rating: 4.1, totalRatings: 140, inventorySize: 'small' },

  // Aerodrome & Airport Area
  { id: 'IND_031', name: 'Airport Pharmacy', address: 'Aerodrome Road, Indore 452005', location: { lat: 22.7278, lng: 75.8012 }, phone: '+91 731 2530031', isOpen: true, rating: 4.5, totalRatings: 230, inventorySize: 'medium' },
  { id: 'IND_032', name: 'Aerodrome Medical', address: 'Near Airport, Indore 452005', location: { lat: 22.7298, lng: 75.8034 }, phone: '+91 731 2530032', isOpen: true, rating: 4.3, totalRatings: 175, inventorySize: 'small' },

  // Manik Bagh & Race Course
  { id: 'IND_033', name: 'Manik Bagh Pharmacy', address: 'Manik Bagh Road, Indore 452014', location: { lat: 22.7089, lng: 75.8812 }, phone: '+91 731 2530033', isOpen: true, rating: 4.6, totalRatings: 280, inventorySize: 'large' },
  { id: 'IND_034', name: 'Race Course Medical', address: 'Race Course Road, Indore 452003', location: { lat: 22.7123, lng: 75.8834 }, phone: '+91 731 2530034', isOpen: true, rating: 4.2, totalRatings: 155, inventorySize: 'medium' },

  // Scheme 78 & Nearby
  { id: 'IND_035', name: 'Scheme 78 Pharmacy', address: 'Scheme 78, Indore 452010', location: { lat: 22.7634, lng: 75.8823 }, phone: '+91 731 2530035', isOpen: true, rating: 4.4, totalRatings: 205, inventorySize: 'medium' },
  { id: 'IND_036', name: 'Platinum Medical', address: 'Scheme 78 Part 2, Indore 452010', location: { lat: 22.7656, lng: 75.8845 }, phone: '+91 731 2530036', isOpen: true, rating: 4.3, totalRatings: 185, inventorySize: 'small' },

  // Bhanwarkuan & Nearby
  { id: 'IND_037', name: 'Bhanwarkuan Pharmacy', address: 'Bhanwarkuan Main, Indore 452014', location: { lat: 22.7212, lng: 75.8923 }, phone: '+91 731 2530037', isOpen: true, rating: 4.5, totalRatings: 240, inventorySize: 'medium' },
  { id: 'IND_038', name: 'Sneh Nagar Medical', address: 'Sneh Nagar, Indore 452001', location: { lat: 22.7234, lng: 75.8945 }, phone: '+91 731 2530038', isOpen: true, rating: 4.1, totalRatings: 130, inventorySize: 'small' },

  // Pipliyahana & Nearby
  { id: 'IND_039', name: 'Pipliyahana Pharmacy', address: 'Pipliyahana Square, Indore 452016', location: { lat: 22.7789, lng: 75.9089 }, phone: '+91 731 2530039', isOpen: true, rating: 4.6, totalRatings: 290, inventorySize: 'large' },
  { id: 'IND_040', name: 'New Palasia Medical', address: 'New Palasia, Indore 452001', location: { lat: 22.7223, lng: 75.8667 }, phone: '+91 731 2530040', isOpen: true, rating: 4.4, totalRatings: 215, inventorySize: 'medium' },

  // Mhow Road & Nearby
  { id: 'IND_041', name: 'Mhow Road Pharmacy', address: 'Mhow Road, Indore 452017', location: { lat: 22.6834, lng: 75.8567 }, phone: '+91 731 2530041', isOpen: true, rating: 4.2, totalRatings: 160, inventorySize: 'medium' },
  { id: 'IND_042', name: 'Sanwer Road Medical', address: 'Sanwer Road, Indore 453111', location: { lat: 22.7456, lng: 75.7923 }, phone: '+91 731 2530042', isOpen: true, rating: 4.0, totalRatings: 125, inventorySize: 'small' },

  // Khandwa Road & Nearby
  { id: 'IND_043', name: 'Khandwa Road Pharmacy', address: 'Khandwa Road, Indore 452001', location: { lat: 22.7089, lng: 75.8456 }, phone: '+91 731 2530043', isOpen: true, rating: 4.3, totalRatings: 180, inventorySize: 'medium' },
  { id: 'IND_044', name: 'Dewas Naka Medical', address: 'Dewas Naka, Indore 452010', location: { lat: 22.7512, lng: 75.8234 }, phone: '+91 731 2530044', isOpen: true, rating: 4.1, totalRatings: 140, inventorySize: 'small' },

  // Palda & Industrial Area
  { id: 'IND_045', name: 'Palda Pharmacy', address: 'Palda, Indore 452020', location: { lat: 22.7823, lng: 75.8123 }, phone: '+91 731 2530045', isOpen: true, rating: 4.4, totalRatings: 200, inventorySize: 'medium' },
  { id: 'IND_046', name: 'Industrial Area Medical', address: 'Sanwer Road Industrial, Indore 452015', location: { lat: 22.7567, lng: 75.7845 }, phone: '+91 731 2530046', isOpen: true, rating: 4.2, totalRatings: 155, inventorySize: 'small' },

  // Lasudia & Nearby
  { id: 'IND_047', name: 'Lasudia Pharmacy', address: 'Lasudia Mori, Indore 452011', location: { lat: 22.6789, lng: 75.8912 }, phone: '+91 731 2530047', isOpen: true, rating: 4.5, totalRatings: 235, inventorySize: 'medium' },
  { id: 'IND_048', name: 'Sirpur Medical Store', address: 'Sirpur, Indore 453771', location: { lat: 22.6623, lng: 75.8234 }, phone: '+91 731 2530048', isOpen: true, rating: 4.0, totalRatings: 115, inventorySize: 'small' },

  // Additional Coverage
  { id: 'IND_049', name: 'Bombay Hospital Pharmacy', address: 'Bombay Hospital Campus, Indore 452010', location: { lat: 22.7445, lng: 75.8789 }, phone: '+91 731 2530049', isOpen: true, rating: 4.8, totalRatings: 420, inventorySize: 'large' },
  { id: 'IND_050', name: 'CHL Hospital Pharmacy', address: 'CHL Hospital, AB Road, Indore 452008', location: { lat: 22.7289, lng: 75.8756 }, phone: '+91 731 2530050', isOpen: true, rating: 4.7, totalRatings: 385, inventorySize: 'large' }
];

// Generate dynamic medicine inventory for each pharmacy based on size
export function generatePharmacyInventory(inventorySize) {
  const allMedicineIds = Array.from({ length: 25000 }, (_, i) => i + 1);

  let inventoryCount;
  switch (inventorySize) {
    case 'large':
      inventoryCount = 5000 + Math.floor(Math.random() * 3000); // 5000-8000 medicines
      break;
    case 'medium':
      inventoryCount = 2000 + Math.floor(Math.random() * 2000); // 2000-4000 medicines
      break;
    case 'small':
      inventoryCount = 500 + Math.floor(Math.random() * 1000); // 500-1500 medicines
      break;
    default:
      inventoryCount = 1000;
  }

  // Randomly select medicines for this pharmacy
  const shuffled = allMedicineIds.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, inventoryCount);
}

// Pre-generate inventory for all pharmacies (cached for performance)
const PHARMACY_INVENTORIES = {};
INDORE_PHARMACIES.forEach(pharmacy => {
  PHARMACY_INVENTORIES[pharmacy.id] = generatePharmacyInventory(pharmacy.inventorySize);
});

export function getPharmacyInventory(pharmacyId) {
  return PHARMACY_INVENTORIES[pharmacyId] || [];
}

export function checkMedicineAvailability(pharmacyId, medicineId) {
  const inventory = PHARMACY_INVENTORIES[pharmacyId] || [];
  return inventory.includes(medicineId);
}
