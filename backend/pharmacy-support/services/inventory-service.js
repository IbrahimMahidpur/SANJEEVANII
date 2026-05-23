const fs = require('fs').promises;
const path = require('path');

const PHARMACIES_FILE = path.join(__dirname, '../data/pharmacies.json');
const MEDICINES_FILE = path.join(__dirname, '../data/medicines.json');

/**
 * Load pharmacies from JSON file
 */
async function loadPharmacies() {
  try {
    const data = await fs.readFile(PHARMACIES_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.log('ℹ️ No pharmacies file found, initializing...');
    return [];
  }
}

/**
 * Save pharmacies to JSON file
 */
async function savePharmacies(pharmacies) {
  await fs.writeFile(PHARMACIES_FILE, JSON.stringify(pharmacies, null, 2));
}

/**
 * Load medicines database
 */
async function loadMedicines() {
  try {
    const data = await fs.readFile(MEDICINES_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.log('ℹ️ No medicines file found, initializing...');
    return [];
  }
}

/**
 * Save medicines database
 */
async function saveMedicines(medicines) {
  await fs.writeFile(MEDICINES_FILE, JSON.stringify(medicines, null, 2));
}

/**
 * Get pharmacy by ID
 */
async function getPharmacyById(pharmacyId) {
  const pharmacies = await loadPharmacies();
  return pharmacies.find(p => p.id === pharmacyId);
}

/**
 * Get pharmacy inventory
 */
async function getPharmacyInventory(pharmacyId) {
  const pharmacy = await getPharmacyById(pharmacyId);
  return pharmacy ? pharmacy.inventory : [];
}

/**
 * Update pharmacy inventory
 */
async function updateInventory(pharmacyId, medicineData) {
  const pharmacies = await loadPharmacies();
  const pharmacyIndex = pharmacies.findIndex(p => p.id === pharmacyId);

  if (pharmacyIndex === -1) {
    throw new Error('Pharmacy not found');
  }

  const { medicineName, quantity, price, expiryDate } = medicineData;

  // Check if medicine already exists in inventory
  const inventory = pharmacies[pharmacyIndex].inventory || [];
  const medicineIndex = inventory.findIndex(m =>
    m.name.toLowerCase() === medicineName.toLowerCase()
  );

  if (medicineIndex !== -1) {
    // Update existing medicine
    inventory[medicineIndex].quantity = quantity;
    inventory[medicineIndex].price = price;
    inventory[medicineIndex].expiryDate = expiryDate;
    inventory[medicineIndex].lastUpdated = new Date().toISOString();
  } else {
    // Add new medicine
    inventory.push({
      id: `med_${Date.now()}`,
      name: medicineName,
      quantity,
      price,
      expiryDate,
      lastUpdated: new Date().toISOString()
    });
  }

  pharmacies[pharmacyIndex].inventory = inventory;
  await savePharmacies(pharmacies);

  return inventory;
}

/**
 * Search medicine availability across pharmacies
 */
async function searchMedicineAvailability(medicineName, userLat, userLng, radius = 5000) {
  const pharmacies = await loadPharmacies();
  const availability = [];

  const searchTerm = medicineName.toLowerCase().trim();

  for (const pharmacy of pharmacies) {
    // Calculate distance
    const distance = calculateDistance(
      userLat, userLng,
      pharmacy.location.lat, pharmacy.location.lng
    );

    // Skip if outside radius
    if (distance > radius / 1000) continue;

    // Check inventory
    const inventory = pharmacy.inventory || [];
    const medicine = inventory.find(m =>
      m.name.toLowerCase().includes(searchTerm)
    );

    if (medicine && medicine.quantity > 0) {
      availability.push({
        pharmacyId: pharmacy.id,
        pharmacyName: pharmacy.name,
        pharmacyAddress: pharmacy.address,
        location: pharmacy.location,
        distance: distance,
        available: true,
        medicine: {
          name: medicine.name,
          quantity: medicine.quantity,
          price: medicine.price,
          expiryDate: medicine.expiryDate
        },
        estimatedPrice: {
          amount: medicine.price,
          currency: 'INR'
        },
        confidence: 0.95, // High confidence for actual inventory data
        lastUpdated: medicine.lastUpdated
      });
    }
  }

  // Sort by distance
  availability.sort((a, b) => a.distance - b.distance);

  return availability;
}

/**
 * Add new pharmacy
 */
async function addPharmacy(pharmacyData) {
  const pharmacies = await loadPharmacies();

  const newPharmacy = {
    id: `pharmacy_${Date.now()}`,
    name: pharmacyData.name,
    address: pharmacyData.address,
    location: pharmacyData.location,
    phone: pharmacyData.phone,
    email: pharmacyData.email,
    openingHours: pharmacyData.openingHours || {},
    inventory: [],
    verified: false,
    createdAt: new Date().toISOString()
  };

  pharmacies.push(newPharmacy);
  await savePharmacies(pharmacies);

  return newPharmacy;
}

/**
 * Get all pharmacies
 */
async function getAllPharmacies() {
  return await loadPharmacies();
}

/**
 * Calculate distance between two points (Haversine formula)
 */
function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371; // Earth's radius in km
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);

  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;

  return Math.round(distance * 10) / 10;
}

function toRad(degrees) {
  return degrees * (Math.PI / 180);
}

module.exports = {
  getPharmacyById,
  getPharmacyInventory,
  updateInventory,
  searchMedicineAvailability,
  addPharmacy,
  getAllPharmacies
};
