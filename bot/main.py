import asyncio
from configparser import ConfigParser
from dotenv import load_dotenv
import os

from discord.ext import commands

from pymongo import MongoClient, database

from .config_verification import read_and_validate_config

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")
MONGO_PORT = os.getenv("MONGO_PORT")
PORTAL_LINK = os.getenv("PORTAL_LINK")
SERVER_CONFIG = ConfigParser()

bot = commands.Bot(command_prefix=".")
db: database.Database = None  # assigned in main function


def get_users_from_discordid(user_id):
    users = list(db.users.find({"discordId": str(user_id)}))
    return users


def is_verified(user_id):
    return True if get_users_from_discordid(user_id) else False


def get_realname_from_discordid(user_id):
    users = get_users_from_discordid(user_id)
    assert users
    return users[0]["name"]


async def send_link(ctx):
    await ctx.send(
        f"<{PORTAL_LINK}>\nSign in through our portal, and try again."
    )


def get_config(server_id: str):
    for section in SERVER_CONFIG.sections():
        section_obj = SERVER_CONFIG[section]
        if section_obj["serverid"] == server_id:
            return section_obj

    print(f"Server id {server_id} not found in server config")
    exit(1)


async def create_roles_if_missing(guild, req_guild_roles):
    for role in req_guild_roles:
        roles_present = guild.roles
        role_names = [role.name for role in roles_present]

        if role not in role_names:
            await guild.create_role(name=role)


async def assign_role(guild, user, server_config):
    req_roles = server_config["grantroles"].strip().split(",")

    await create_roles_if_missing(guild, req_roles)

    assign_roles = [role for role in guild.roles if role.name in req_roles]

    await user.add_roles(*assign_roles)


async def delete_role(guild, user, server_config):
    config_remove_roles = server_config["deleteroles"].strip().split(",")
    to_remove_roles = [
        role for role in guild.roles if role.name in config_remove_roles
    ]

    # if the user does not have that role, this does not crash
    await user.remove_roles(*to_remove_roles)


async def set_nickname(user, server_config):
    if server_config["setrealname"] == "no":
        return

    realname = get_realname_from_discordid(user.id)
    await user.edit(nick=realname)


async def post_verification(ctx, user):
    server_id = str(ctx.guild.id)
    server_config = get_config(server_id)

    await assign_role(ctx.guild, user, server_config)
    await delete_role(ctx.guild, user, server_config)

    try:
        await set_nickname(user, server_config)
    except:
        await ctx.send(
            "Bot should have a role higher than you to change your nickname"
        )

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

    if not read_and_validate_config(SERVER_CONFIG, "server_config.ini"):
        exit(1)

    mongo_client = MongoClient(
        f"mongodb://127.0.0.1:{MONGO_PORT}/{MONGO_DATABASE}?retryWrites=true&w=majority"
    )
    db = mongo_client.get_database(MONGO_DATABASE)

    bot.run(TOKEN)


if __name__ == "__main__":
    main()
