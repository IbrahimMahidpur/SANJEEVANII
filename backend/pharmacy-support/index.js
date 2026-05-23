const express = require('express');
const facilitiesRouter = require('./routes/facilities');
const inventoryRouter = require('./routes/inventory');
const healthCampsRouter = require('./routes/health-camps');
const doctorsRouter = require('./routes/doctors');
const chatbotRouter = require('./routes/chatbot');

const router = express.Router();

// Mount all sub-routes
router.use('/facilities', facilitiesRouter);
router.use('/inventory', inventoryRouter);
router.use('/health-camps', healthCampsRouter);
router.use('/doctors', doctorsRouter);
router.use('/chatbot', chatbotRouter);

module.exports = router;
