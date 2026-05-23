const fs = require('fs').promises;
const path = require('path');

const DOCTORS_FILE = path.join(__dirname, '../data/doctors.json');
const BOOKINGS_FILE = path.join(__dirname, '../data/bookings.json');

/**
 * Load doctors from JSON file
 */
async function loadDoctors() {
  try {
    const data = await fs.readFile(DOCTORS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.log('ℹ️ No doctors file found, initializing...');
    return [];
  }
}

/**
 * Save doctors to JSON file
 */
async function saveDoctors(doctors) {
  await fs.writeFile(DOCTORS_FILE, JSON.stringify(doctors, null, 2));
}

/**
 * Load bookings from JSON file
 */
async function loadBookings() {
  try {
    const data = await fs.readFile(BOOKINGS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.log('ℹ️ No bookings file found, initializing...');
    return [];
  }
}

/**
 * Save bookings to JSON file
 */
async function saveBookings(bookings) {
  await fs.writeFile(BOOKINGS_FILE, JSON.stringify(bookings, null, 2));
}

/**
 * Get all doctors
 */
async function getAllDoctors() {
  return await loadDoctors();
}

/**
 * Get doctor by ID
 */
async function getDoctorById(doctorId) {
  const doctors = await loadDoctors();
  return doctors.find(d => d.id === doctorId);
}

/**
 * Get doctors by hospital
 */
async function getDoctorsByHospital(hospitalId) {
  const doctors = await loadDoctors();
  return doctors.filter(d => d.hospitalId === hospitalId);
}

/**
 * Get doctors by specialization
 */
async function getDoctorsBySpecialization(specialization) {
  const doctors = await loadDoctors();
  const searchTerm = specialization.toLowerCase();
  return doctors.filter(d =>
    d.specialization.toLowerCase().includes(searchTerm)
  );
}

/**
 * Get doctor availability for a specific date
 */
async function getDoctorAvailability(doctorId, date) {
  const doctor = await getDoctorById(doctorId);
  if (!doctor) {
    throw new Error('Doctor not found');
  }

  const dayOfWeek = new Date(date).toLocaleDateString('en-US', { weekday: 'long' });
  const dayAvailability = doctor.availability.find(a => a.day === dayOfWeek);

  if (!dayAvailability) {
    return { available: false, slots: [] };
  }

  // Get existing bookings for this date
  const bookings = await loadBookings();
  const dateBookings = bookings.filter(b =>
    b.doctorId === doctorId && b.date === date
  );

  // Mark slots as booked
  const slots = dayAvailability.slots.map(slot => {
    const isBooked = dateBookings.some(b => b.time === slot.startTime);
    return {
      ...slot,
      available: slot.available && !isBooked,
      booked: isBooked
    };
  });

  return {
    available: true,
    day: dayOfWeek,
    slots
  };
}

/**
 * Create a new booking
 */
async function createBooking(bookingData) {
  const { doctorId, patientName, phone, email, date, time, reason } = bookingData;

  // Verify doctor exists
  const doctor = await getDoctorById(doctorId);
  if (!doctor) {
    throw new Error('Doctor not found');
  }

  // Check if slot is available
  const availability = await getDoctorAvailability(doctorId, date);
  const slot = availability.slots.find(s => s.startTime === time);

  if (!slot || !slot.available) {
    throw new Error('Time slot not available');
  }

  // Create booking
  const bookings = await loadBookings();
  const newBooking = {
    id: `booking_${Date.now()}`,
    doctorId,
    doctorName: doctor.name,
    hospitalName: doctor.hospitalName,
    patientName,
    phone,
    email: email || null,
    date,
    time,
    reason: reason || 'General consultation',
    status: 'confirmed',
    consultationFee: doctor.consultationFee,
    createdAt: new Date().toISOString()
  };

  bookings.push(newBooking);
  await saveBookings(bookings);

  return newBooking;
}

/**
 * Get booking by ID
 */
async function getBookingById(bookingId) {
  const bookings = await loadBookings();
  return bookings.find(b => b.id === bookingId);
}

/**
 * Get bookings by patient phone
 */
async function getBookingsByPhone(phone) {
  const bookings = await loadBookings();
  return bookings.filter(b => b.phone === phone);
}

/**
 * Cancel booking
 */
async function cancelBooking(bookingId) {
  const bookings = await loadBookings();
  const bookingIndex = bookings.findIndex(b => b.id === bookingId);

  if (bookingIndex === -1) {
    throw new Error('Booking not found');
  }

  bookings[bookingIndex].status = 'cancelled';
  bookings[bookingIndex].cancelledAt = new Date().toISOString();

  await saveBookings(bookings);
  return bookings[bookingIndex];
}

/**
 * Add new doctor
 */
async function addDoctor(doctorData) {
  const doctors = await loadDoctors();

  const newDoctor = {
    id: `doctor_${Date.now()}`,
    name: doctorData.name,
    specialization: doctorData.specialization,
    hospitalId: doctorData.hospitalId,
    hospitalName: doctorData.hospitalName,
    phone: doctorData.phone,
    email: doctorData.email,
    availability: doctorData.availability || [],
    consultationFee: doctorData.consultationFee,
    experience: doctorData.experience,
    qualifications: doctorData.qualifications || [],
    verified: false,
    createdAt: new Date().toISOString()
  };

  doctors.push(newDoctor);
  await saveDoctors(doctors);

  return newDoctor;
}

/**
 * Update doctor availability
 */
async function updateDoctorAvailability(doctorId, availability) {
  const doctors = await loadDoctors();
  const doctorIndex = doctors.findIndex(d => d.id === doctorId);

  if (doctorIndex === -1) {
    throw new Error('Doctor not found');
  }

  doctors[doctorIndex].availability = availability;
  await saveDoctors(doctors);

  return doctors[doctorIndex];
}

module.exports = {
  getAllDoctors,
  getDoctorById,
  getDoctorsByHospital,
  getDoctorsBySpecialization,
  getDoctorAvailability,
  createBooking,
  getBookingById,
  getBookingsByPhone,
  cancelBooking,
  addDoctor,
  updateDoctorAvailability
};
