const express = require('express');
const morgan = require('morgan');
const fetch = require('node-fetch');
const btoa = require('btoa');

const config = require('./utils/config');
const logger = require('./utils/logger');

const app = express();

app.use(express.json());
app.use(morgan('dev'));

app.get('/', (req, res) => {
  res.redirect('/discord');
})

app.get('/discord', (req, res) => {
  res.redirect(`https://discordapp.com/api/oauth2/authorize?client_id=${config.DISCORD_CLIENT_ID}&scope=identify&response_type=code&redirect_uri=${config.DISCORD_REDIRECT}`);
})

app.get('/cas', async (req, res) => {
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
  logger.info(user);
  res.json(user);
})

module.exports = app;
