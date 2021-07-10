# Discord CAS

Tool for user verification via CAS on Discord server. If your organization uses
CAS for authentication, and if you also run a Discord server whose private
contents should only be accessible to CAS authenticated users, then this is the
right tool for you.

Once a user are authenticated on any one server, they will not need to repeat
the whole signup process on another server.

## Wiki 

Head over to the [wiki](https://github.com/Groverkss/Discord-CAS/wiki) to 
learn how to add the bot to your server / host it for your own organization.

## Contributions

Feel free to make a PR/issue for feature implementation/request.

Formating for python is done with Black with a 80 character limit.
Formating for javascript isnt strict as long as 80 character limit is followed.

## Privacy policy

When a user authenticates with our web portal, we store their following
information: 
  1. Full Name 
  1. Email 
  1. Roll number 
  1. DiscordID.

1,2,3 are obtained from CAS, and 4 is obtained from Discord OAuth. 

This data is used strictly for authentication only, and not visible publicly.
It is only visible to the server host.

The bot does not track any interactions. If a user does not authenticate with
our portal, we store no data.

## License

MIT
