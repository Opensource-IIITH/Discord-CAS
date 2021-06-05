# Discord CAS

Tool for user verification via CAS on Discord server. If your organization uses CAS for authentication, and if you also run a Discord server whose private contents should only be accessible to CAS authenticated users, then this is the right tool for you.

Once a user are authenticated on any one server, they will not need to repeat the whole signup process on another server.

## Configuration parameters

The following configuration are possible through `bot/server_config.ini`:

1. `setrealname`: set member nickname (post verification) equal to their real name (obtained from CAS). This configuration is only useful if regular members in your Discord do not have the "Change Nickname" permission.
2. `grantroles`: a comma-separated list of roles you'd like to assign to the member post-verification. If the roles do not exist in the server, they'll be created automatically.
3. `serverid`: ID of the Discord server. See [Discord FAQ](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-). (In Discord lingo, a server is known as a guild.)

**Example usage:** you can grant a "Verified" role to users post-verification, keeping private channels hidden for non-Verified users. Moreover, to allow server users to retain their anonymous Discord usernames, set `setrealname` to `no` in the above configuration.

## How do I add this bot to my own server?

### IIIT clubs

1. Make a pull request to the server by ediing the `bot/server_config.ini` file as per your server requirements. (configurations are detailed in above section)
2. Create a new role for the bot, which is *above* the roles of regular members (bot can only verify members lower in role than itself)
3. **After** your PR is merged, navigate to the [this URL](https://discord.com/api/oauth2/authorize?client_id=843107899944861706&permissions=469764096&redirect_uri=https%3A%2F%2Fdiscord-cas.eastus.cloudapp.azure.com%2Fbot&response_type=code&scope=bot%20identify) to authenticate the bot and add it to your server. Note that you must have "Manage Server" permission on this server.

(If you're new to Discord roles, read the FAQ: [link](https://support.discord.com/hc/en-us/articles/214836687-Role-Management-101))

One of the admins will then:

1. Merge your pull request
2. Restart the running bot instance

**Notes**:

1. `.verify` might not work for server-admins. In that case, the role the bot has should be higher than the role of the server admin.
2. We recommend that you create a new channel (like #server-help) where all your users can run the `.verify` command. 

If at any point you face any difficulty, raise a new issue in this GitHub repository.

### External organizations

1. You need to host the bot and the webportal in a server first. You can get free subscriptions for Azure, etc. or use your own.
2. Once the bot is hosted, create a new bot in Discord Developer portal and link the secret bot tokens.
3. Edit the server config file as per your server requirements.
4. Add the bot to to the server with the correct permissions.

The only difference here is that we are not making available our Discord bot instance as well as the server instance for public use.

## Hosting your own instance

The bot is a reasonably straightforward discord.py implementation.  
The portal is a Express webapp, connecting two authentication services (discord authentication and CAS authentication) with the `express-session` middleware.

Stuff should run as is, although the following points need attention:

1. Create a `bot/.env` file following the template `bot/.env.template`.
2. Create a `portal/utils/config.js` file following the template `portal/utils/template.config.js`.

## Contributions

Feel free to make a PR/issue for feature implementation/request.

## Hosting history

The current instance of the bot used by IIIT clubs is hosted by:

- Gaurang Tandon (late June 21 - )
- Vidit Jain (April 6, 21 - late June 21)

## Privacy policy

When a user authenticates with our web portal, we store their following information: 1. Full Name 2. Email 3. Roll number 4. DiscordID. 1,2,3 are obtained from CAS, and 4 is obtained from Discord. All these are obtained after user gives consent through authentication. 

This data is used strictly for authentication only, and not visible publicly. It is only visible to the server host.

The bot does not track any interactions. If a user does not authenticate with our portal, we store no data.

## License

MIT