# Discord CAS

Tool for user verification via CAS on Discord server. If your organization uses CAS for authentication, and if you run a Discord server whose private contents should only be accessible to authenticated users, then this bot is the right tool.

## Configuration parameters

The following configuration are possible through `bot/server_config.ini`:

1. `setrealname`: set member nickname (post verification) equal to their real name (obtained from CAS). This configuration is only useful if regular members in your Discord do not have the "Change Nickname" permission.
2. `grantroles`: a comma-separated list of roles you'd like to assign to the member post-verification. If the roles do not exist in the server, they'll be created automatically.
3. `serverid`: ID of the Discord server. See [Discord FAQ](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-). (In Discord lingo, a server is known as a guild.)

## How do I add this bot to my own server?

### IIIT clubs

1. Make a pull request to the server by ediing the `bot/server_config.ini` file as per your server requirements. (configurations are detailed in above section)
2. Invite one of the bot admins to your server and give them Manage Server permission. 
   
The bot admin will then:

1. Merge your pull request 
2. Restart the running bot instance 
3. Add the bot to your server with requisite permission.
4. Leave your server (optional)

### External organizations

1. You need to host the bot in a server first. You can get free subscriptions for Azure, etc. or use your own.
2. Once the bot is hosted, create a new bot in Discord Developer portal and link the secret bot tokens.
3. Repeat all the steps above.

The only instance here is that we are not making available our Discord bot instance as well as the server instance for public use.

## Code architecture

The bot is a reasonably straightforward discord.py implementation.  
The portal is a Express webapp, connecting two authentication services (discord authentication and CAS authentication) with the `express-session` middleware.

## Contributions

Feel free to make a PR/issue for feature implementation/request.

## Hosting history

The current instance of the bot used by IIIT clubs is hosted by:

- Gaurang Tandon (late June 21 - )
- Vidit Jain (April 6, 21 - late June 21)

## License

MIT