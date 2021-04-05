const config = require('./utils/config')
const app = require('./app')
const logger = require('./utils/logger')
const mongoose = require('mongoose');

mongoose.connect( config.ATLAS_URL,
  { useNewUrlParser: true, useUnifiedTopology: true }, () => { 
    logger.info('Database connected successfully.');
});

app.listen(config.PORT, () => {
  logger.info(`Server running on port ${config.PORT}`)
});
