const express = require('express');
const cookieParser = require('cookie-parser')
const morgan = require('morgan');
const fetch = require('node-fetch');
const btoa = require('btoa');

const config = require('./utils/config');
const logger = require('./utils/logger');

const app = express();

app.use(express.json());
app.use(morgan('dev'));
app.use(cookieParser());

app.get('/', (req, res) => {
  res.redirect('/discord');
})

app.get('/discord', (req, res) => {
  res.redirect(`https://discordapp.com/api/oauth2/authorize?client_id=${config.DISCORD_CLIENT_ID}&scope=identify&response_type=code&redirect_uri=${config.DISCORD_REDIRECT}`);
})

app.get('/discord/callback', async (req, res) => {
  /* Get user from discord */
  if (!req.query.code) {
    res.send("You are not discord :angry:", 400);
    return;
  }

  const code = req.query.code;
  const creds = btoa(`${config.DISCORD_CLIENT_ID}:${config.DISCORD_SECRET}`);

  const data = {
      grant_type: "authorization_code",
      code: code,
      redirect_uri: config.DISCORD_REDIRECT,
   };

  const _encode = obj => {
    let string = "";

    for (const [key, value] of Object.entries(obj)) {
      if (!value) continue;
      string += `&${encodeURIComponent(key)}=${encodeURIComponent(value)}`;
    }
    return string.substring(1);
  }

  params = _encode(data);

  const response = await fetch(`https://discordapp.com/api/oauth2/token`, {
    method: "POST",
    headers: {
      Authorization: `Basic ${creds}`,
      'Content-Type': "application/x-www-form-urlencoded",
    },
    body: params,
  });
  const responseJson = await response.json();
  const accessToken = responseJson.access_token;

  const userResponse = await fetch(`https://discordapp.com/api/users/@me`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });

  const user = await userResponse.json();

  if (!user) {
    res.send("Some error occured while communicating to discord :pensive:", 500);
    return;
  }

  /* Set user id as cookie */
  res.cookie("discordId", user.id);

  res.redirect('/cas');
})

const CAS = require('cas')

const cas = new CAS({
  base_url: 'https://login.iiit.ac.in/cas',
  service: config.BASE_URL,
  version: 2.0,
})

app.get('/cas', async (req, res) => {
  if (!req.cookies.discordId) {
    /* Verify that discord we set this cookie not a malicious user */
    res.send("You are not discord :angry:", 500);
    return;
  }

  cas.authenticate(req, res, (err, status, username, extended) => {
    if (err) {
      res.send("Some error occured with the CAS server :pensive:", 500);
    } else {
      if (!status) {
        /* TODO: Identify what status false means */
        res.send("Status false?", 500);
      }

      const userData = {
        "discordId": req.cookies.discordId,
        "name": extended.attributes.name,
        "rollno": extended.attributes.rollno,
        "email": extended.attributes['e-mail'],
      }
      res.json(userData);
    }
  });
})

module.exports = app;
