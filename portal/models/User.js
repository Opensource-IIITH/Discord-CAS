const mongoose = require('mongoose')
const findOrCreate = require('mongoose-findorcreate')

const user = mongoose.Schema({
  discordId: {
    type: String,
    required: true,
    unique: true,
  },
  name: {
    type: String,
    required: true,
  },
  email: {
    type: String,
    required: true,
  },
  rollno: {
    type: String,
    required: true,
  },
  view: {
    type: Boolean,
    default: true,
  }
});

user.plugin(findOrCreate);

module.exports = mongoose.model('User', user);
