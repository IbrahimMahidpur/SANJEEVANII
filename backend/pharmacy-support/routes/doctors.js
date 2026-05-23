const express = require('express');
const router = express.Router();
const doctorService = require('../services/doctor-service');

/**
 * GET /api/pharmacy-support/doctors
 * Get all doctors or filter by specialization
 */
router.get('/', async (req, res) => {
  try {
    const { specialization } = req.query;

    let doctors;
    if (specialization) {
      doctors = await doctorService.getDoctorsBySpecialization(specialization);
    } else {
      doctors = await doctorService.getAllDoctors();
    }

    res.json({
      success: true,
      count: doctors.length,
      doctors
    });

  } catch (error) {
    console.error('Error fetching doctors:', error);
    res.status(500).json({
      error: 'Failed to fetch doctors',
      message: error.message
    });
  }
});

/**
 * GET /api/pharmacy-support/doctors/:doctorId/availability
 * Get doctor availability for a specific date
 */
router.get('/:doctorId/availability', async (req, res) => {
  try {
    const { doctorId } = req.params;
    const { date } = req.query;

    if (!date) {
      return res.status(400).json({
        error: 'Date is required (YYYY-MM-DD format)'
      });
    }

    const availability = await doctorService.getDoctorAvailability(doctorId, date);

    res.json({
      success: true,
      doctorId,
      date,
      ...availability
    });

  } catch (error) {
    console.error('Error fetching doctor availability:', error);
    res.status(500).json({
      error: 'Failed to fetch doctor availability',
      message: error.message
    });
  }
});

/**
 * POST /api/pharmacy-support/doctors/booking
 * Create a new booking
 */
router.post('/booking', async (req, res) => {
  try {
    const { doctorId, patientName, phone, email, date, time, reason } = req.body;

    if (!doctorId || !patientName || !phone || !date || !time) {
      return res.status(400).json({
        error: 'Doctor ID, patient name, phone, date, and time are required'
      });
    }

    const booking = await doctorService.createBooking({
      doctorId,
      patientName,
      phone,
      email,
      date,
      time,
      reason
    });

    res.json({
      success: true,
      message: 'Booking created successfully',
      booking
    });

  } catch (error) {
    console.error('Error creating booking:', error);
    res.status(500).json({
      error: 'Failed to create booking',
      message: error.message
    });
  }
});

/**
 * GET /api/pharmacy-support/doctors/booking/:bookingId
 * Get booking details
 */
router.get('/booking/:bookingId', async (req, res) => {
  try {
    const { bookingId } = req.params;

    const booking = await doctorService.getBookingById(bookingId);

    if (!booking) {
      return res.status(404).json({
        error: 'Booking not found'
      });
    }

    res.json({
      success: true,
      booking
    });

  } catch (error) {
    console.error('Error fetching booking:', error);
    res.status(500).json({
      error: 'Failed to fetch booking',
      message: error.message
    });
  }
});

/**
 * GET /api/pharmacy-support/doctors/bookings/phone/:phone
 * Get bookings by phone number
 */
router.get('/bookings/phone/:phone', async (req, res) => {
  try {
    const { phone } = req.params;

    const bookings = await doctorService.getBookingsByPhone(phone);

    res.json({
      success: true,
      count: bookings.length,
      bookings
    });

  } catch (error) {
    console.error('Error fetching bookings:', error);
    res.status(500).json({
      error: 'Failed to fetch bookings',
      message: error.message
    });
  }
});

/**
 * DELETE /api/pharmacy-support/doctors/booking/:bookingId
 * Cancel a booking
 */
router.delete('/booking/:bookingId', async (req, res) => {
  try {
    const { bookingId } = req.params;

    const booking = await doctorService.cancelBooking(bookingId);

    res.json({
      success: true,
      message: 'Booking cancelled successfully',
      booking
    });

  } catch (error) {
    console.error('Error cancelling booking:', error);
    res.status(500).json({
      error: 'Failed to cancel booking',
      message: error.message
    });
  }
});

/**
 * POST /api/pharmacy-support/doctors
 * Add new doctor
 */
router.post('/', async (req, res) => {
  try {
    const { name, specialization, hospitalId, hospitalName, phone, email, availability, consultationFee, experience, qualifications } = req.body;

    if (!name || !specialization || !hospitalId || !hospitalName || !phone) {
      return res.status(400).json({
        error: 'Name, specialization, hospital ID, hospital name, and phone are required'
      });
    }

    const doctor = await doctorService.addDoctor({
      name,
      specialization,
      hospitalId,
      hospitalName,
      phone,
      email,
      availability,
      consultationFee,
      experience,
      qualifications
    });

    res.json({
      success: true,
      message: 'Doctor added successfully',
      doctor
    });

  } catch (error) {
    console.error('Error adding doctor:', error);
    res.status(500).json({
      error: 'Failed to add doctor',
      message: error.message
    });
  }
});

module.exports = router;
