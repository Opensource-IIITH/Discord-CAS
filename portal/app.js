const express = require('express');
const session = require("express-session");
const MongoStore = require("connect-mongo");
const morgan = require('morgan');
const fetch = require('node-fetch');
const btoa = require('btoa');

const config = require('./utils/config');
const logger = require('./utils/logger');

const User = require('./models/User')

const parser = require('./utils/parser')

let server_ids = [];

parser.parseFile('../bot/server_config.ini', (error, data) => {
  if (error) {
    logger.error(error);
    return;
  }
  server_ids = Object.values(data).map(x => x.serverid);
})

const app = express();

app.use(express.json());
app.use(morgan('dev'));
app.use(session({
    secret: config.SECRET, store: MongoStore.create({mongoUrl: config.ATLAS_URL})
}));

app.get('/test', (req, res) => {
    res.send("Hello World!");
});

app.get('/', (req, res) => {
    res.redirect('/discord');
});

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

    req.session.discordId = user.id;

    res.redirect('/cas');
})

const CAS = require('cas')

const cas = new CAS({
    base_url: config.CAS_LINK,
    service: config.BASE_URL,
    version: 2.0,
})

app.get('/cas', async (req, res) => {
    if (!req.session.discordId) {
        res.send("Please first authenticate from Discord :angry:", 500);
        return;
    }

    await cas.authenticate(req, res, async (err, status, username, extended) => {
        if (err) {
            res.send("Some error occured with the CAS server :pensive:", 500);
        } else {
            if (!status) {
                /* TODO: Identify what status false means */
                res.send("Status false?", 500);
            }

            let rollno;
            try {
                rollno =  extended.attributes.rollno[0];
            } catch (e) {
                rollno = "not-existent";
                logger.info("User roll number does not exist");
            }

            let name = extended.attributes.name[0];
            name = name.split(" ").map(val => val[0].toUpperCase() + val.substring(1)).join(" ");

            const user = await User.findOrCreate({"discordId": req.session.discordId}, {
                "discordId": req.session.discordId,
                name, rollno,
                "email": extended.attributes['e-mail'][0],
            });

            if (user) {
                res.send("Success! :smile: You can now wait for the bot to auto-detect your verification, " +
                    "or run `.verify` once again.");
            } else {
                res.send("Some error occured :pensive:");
            }
        }
    }, config.BASE_URL + "/cas");
})

app.get('/bot', async (req, res) => {
  if (!req.query.code || !req.query.guild_id) {
      res.send("You are not discord :angry:", 400);
      return;
  }

  const guild_id = req.query.guild_id;

  if (!server_ids.includes(guild_id)) {
    res.send("Read the instructions to invite the bot here here: " + 
        "https://github.com/Groverkss/Discord-CAS/blob/master/README.md", 400);
    return;
  }

  const code = req.query.code;
  const creds = btoa(`${config.DISCORD_CLIENT_ID}:${config.DISCORD_SECRET}`);

  const data = {
      grant_type: "authorization_code",
      code: code,
      redirect_uri: config.BASE_URL + '/bot',
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

  if (responseJson && responseJson.access_token) {
    res.send("Added successfully!");     
  } else {
    logger.error(responseJson);
    res.send("Unkown error occured");
  }
})

module.exports = app;
