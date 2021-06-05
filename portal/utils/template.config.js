const PORT = 100;
const BASE_URL = `https://coolwebsite.com`;

const ATLAS_PORT = 100;
const ATLAS_URL = `mongodb://127.0.0.1:${ATLAS_PORT}`;

const DISCORD_CLIENT_ID = "";
const DISCORD_SECRET = "";
const DISCORD_REDIRECT = BASE_URL + "/discord/callback";

// secret for express middleware
const SECRET = "";

// link to authenticate for CAS from
const CAS_LINK = "https://cas.my-org.com/login";

module.exports = {
  SECRET,
  CAS_LINK,
  PORT,
  BASE_URL,
  ATLAS_URL,
  DISCORD_CLIENT_ID,
  DISCORD_SECRET,
  DISCORD_REDIRECT,
}
