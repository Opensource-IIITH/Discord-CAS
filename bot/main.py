import asyncio
from configparser import ConfigParser
from dotenv import load_dotenv
import os

from discord.ext import commands

from pymongo import MongoClient, database

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")
MONGO_PORT = os.getenv("MONGO_PORT")
SERVER_CONFIG = ConfigParser()

bot = commands.Bot(command_prefix=".")
db: database.Database = None  # assigned in main function


def read_and_validate_config():
    global SERVER_CONFIG
    SERVER_CONFIG.read('server_config.ini')

    req_keys = [("setrealname", ("yes", "no")), "grantroles", "serverid"]

    for section in SERVER_CONFIG.sections():
        section_obj = SERVER_CONFIG[section]

        for key in req_keys:
            if isinstance(key, tuple):
                key_name, allowed_values = key
                if key_name not in section_obj:
                    print(f"Missing key: {key_name}")
                    exit(1)
                given_value = section_obj[key_name]
                if given_value not in allowed_values:
                    print(f"Invalid value for key: {key_name}; expected: {allowed_values}; given: {given_value}")
                    exit(1)
            elif key not in section_obj:
                print(f"Missing key: {key}")
                exit(1)


def get_users_from_discordid(user_id):
    users = list(db.users.find({"discordId": str(user_id)}))
    return users


def is_verified(user_id):
    return True if get_realname_from_discordid(user_id) else False  # empty lists are false


async def get_realname_from_discordid(user_id):
    users = get_users_from_discordid(user_id)
    assert users
    return users[0]["name"]


async def send_link(ctx):
    server_link = "https://discord-cas.eastus.cloudapp.azure.com/"
    await ctx.send(f"<{server_link}>\nSign in through our portal, and try again.")


def get_config(server_id: str):
    for section in SERVER_CONFIG.sections():
        section_obj = SERVER_CONFIG[section]
        if section_obj["serverid"] == server_id:
            return section_obj

    return {}


async def create_roles_if_missing(guild, req_guild_roles):
    for role in req_guild_roles:
        roles_present = guild.roles
        role_names = [role.name for role in roles_present]

        if role not in role_names:
            await guild.create_role(name=role)


async def assign_role(ctx, user, server_config):
    req_roles = server_config["grantroles"]

    await create_roles_if_missing(ctx.guild, req_roles)

    assign_roles = [role for role in ctx.guild.roles if role.name in req_roles]

    for role in assign_roles:
        await user.add_roles(role)


async def set_nickname(ctx, user, server_config):
    if server_config["setrealname"] == "no":
        return

    realname = get_realname_from_discordid(user.id)
    user.edit(nick=realname)


async def post_verification(ctx, user):
    server_id = ctx.guild.id
    server_config = get_config(server_id)

    await assign_role(ctx, user, server_config)
    await set_nickname(ctx, user, server_config)

    await ctx.send(f"<@{user.id}> has been CAS-verified!")


@bot.command(name="verify")
async def verify_user(ctx):
    author = ctx.message.author
    user_id = author.id

    for i in range(2):
        verification = is_verified(user_id)

        if verification:
            await post_verification(ctx, author)
            break
        elif i == 0:
            await send_link(ctx)
            await asyncio.sleep(60)
        else:
            await ctx.send(
                f"Sorry <@{user_id}>, could not auto-detect your verification. Please run `.verify` again."
            )


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


def main():
    global db

    read_and_validate_config()
    mongo_client = MongoClient(
        f"mongodb://127.0.0.1:{MONGO_PORT}/{MONGO_DATABASE}?retryWrites=true&w=majority"
    )
    db = mongo_client.get_database(MONGO_DATABASE)

    bot.run(TOKEN)


if __name__ == "__main__":
    main()
