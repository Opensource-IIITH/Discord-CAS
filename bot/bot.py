import configparser
import discord
from discord.ext import bridge, commands, tasks
import discord.utils as utils
from dotenv import load_dotenv
import motor.motor_asyncio
import os
import datetime
import asyncio
import json

from config_verification import read_and_validate_config


class CasBot(commands.Cog):
    def __init__(self, bot, mongo_database, mongo_port, portal_link):
        self.bot: bridge.Bot = bot
        self.config = configparser.ConfigParser()
        read_and_validate_config(self.config, "server_config.ini")
        self.mongo = motor.motor_asyncio.AsyncIOMotorClient(
            f"mongodb://127.0.0.1:{mongo_port}/{mongo_database}?retryWrites=true&w=majority"
        )
        self.db = self.mongo[mongo_database]

        self.portal_link = portal_link

    async def get_user_from_discordid(self, user_id):
        user = await self.db.users.find_one({"discordId": str(user_id)})
        return user

    async def is_verified(self, user_id):
        return True if await self.get_user_from_discordid(user_id) else False

    async def get_realname_from_discordid(self, user_id):
        user = await self.get_user_from_discordid(user_id)
        if not user:
            return None
        return user["name"]

    async def send_link(self, ctx):
        await ctx.respond(
            f"<{self.portal_link}>\nSign in through our portal, and try again."
        )

    def get_config(self, server_id: str):
        for section in self.config.sections():
            section_obj = self.config[section]
            if section_obj["serverid"] == server_id:
                return section_obj

        print(f"Server id {server_id} not found in server config")

    async def create_roles_if_missing(self, guild, req_guild_roles):
        for role in req_guild_roles:
            roles_present = guild.roles
            role_names = [role.name for role in roles_present]

            if role not in role_names:
                await guild.create_role(name=role)

    async def assign_role(self, guild, user, server_config):
        req_roles = server_config["grantroles"].strip().split(",")

        await self.create_roles_if_missing(guild, req_roles)

        assign_roles = [role for role in guild.roles if role.name in req_roles]

        await user.add_roles(*assign_roles)

    async def delete_role(self, guild, user, server_config):
        config_remove_roles = server_config["deleteroles"].strip().split(",")
        to_remove_roles = [
            role for role in guild.roles if role.name in config_remove_roles
        ]

        # if the user does not have that role, this does not crash
        await user.remove_roles(*to_remove_roles)

    async def set_nickname(self, user, server_config):
        if server_config["setrealname"] == "no":
            return

        realname = await self.get_realname_from_discordid(user.id)
        await user.edit(nick=realname)

    async def post_verification(self, ctx, user):
        server_id = str(ctx.guild.id)
        server_config = self.get_config(server_id)

        await self.assign_role(ctx.guild, user, server_config)
        await self.delete_role(ctx.guild, user, server_config)

        try:
            await self.set_nickname(user, server_config)
        except discord.DiscordException:
            await ctx.respond(
                "Bot should have a role higher than you to change your nickname"
            )

        await ctx.respond(f"<@{user.id}> has been CAS-verified!")

    @bridge.bridge_command(name="verify")
    async def verify(self, ctx: bridge.BridgeContext):
        author = ctx.author
        user_id = author.id

        for i in range(2):
            verification = await self.is_verified(user_id)
            if verification:
                await self.post_verification(ctx, author)
                break

            elif i == 0:
                await self.send_link(ctx)
                await asyncio.sleep(60)
            else:
                await ctx.respond("You are not verified. Please try again later.")
                break

    def is_academic(self, ctx: bridge.BridgeContext):
        return self.get_config(str(ctx.guild.id)).get("is_academic", False)

    @bridge.bridge_command(name="query")
    @commands.check(is_academic)
    async def query(self, ctx: bridge.BridgeContext, identifier: discord.User):
        user = await self.db.users.find_one({"discordId": str(identifier.id)})
        if user:
            await ctx.respond(
                f"Name: {user['name']}\nEmail: {user['email']}\nRoll Number: {user['rollno']}"
            )
        else:
            await ctx.respond(f"{identifier} is not registered with Discord-CAS.")

    @query.error
    async def query_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.respond("This server is not for academic purposes.")
        else:
            raise error

    @bridge.bridge_command(name="roll")
    @commands.check(is_academic)
    async def roll(
        self,
        ctx: bridge.BridgeContext,
        identifier: discord.User,
    ):
        user = await self.db.users.find_one({"rollno": str(identifier.id)})
        if user:
            await ctx.respond(
                f"Name: {user['name']}\nEmail: {user['email']}\nRoll Number: {user['rollno']}"
            )
        else:
            await ctx.respond(f"{identifier} is not registered with Discord-CAS.")

    @roll.error
    async def roll_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.respond("This server is not for academic purposes.")
        else:
            raise error

    @tasks.loop(seconds=30)
    async def check_temp_roles(self):
        async for temp_role_doc in self.db.temp_roles.find(
            {"expires": {"$lte": utils.utcnow()}}
        ):
            try:
                print(temp_role_doc)
                guild = await utils.get_or_fetch(self.bot, "guild", temp_role_doc["guildId"])
                member = await utils.get_or_fetch(guild, "member", temp_role_doc["discordId"])
                await member.remove_roles(discord.Object(int(temp_role_doc["roleId"])))
                await self.db.temp_roles.delete_one({"_id": temp_role_doc["_id"]})
            except discord.DiscordException:
                print(f"Could not remove role {temp_role_doc['roleId']} from {member.name}")

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_temp_roles.start()
        print(f"{self.bot.user.name} has connected to Discord!")

    @bridge.bridge_command(name="reveal")
    async def reveal(self, ctx: bridge.BridgeContext, role: discord.Role):
        server_config = self.get_config(str(ctx.guild.id))
        temp_roles = json.loads(server_config["temproles"])
        if role.name not in temp_roles.keys():
            raise commands.CheckFailure

        duration = temp_roles[role.name]

        try:
            await ctx.author.add_roles(role)
            await self.db.temp_roles.insert_one(
                {
                    "discordId": str(ctx.author.id),
                    "guildId": str(ctx.guild.id),
                    "roleId": str(role.id),
                    "expires": utils.utcnow() +
                    + datetime.timedelta(seconds=duration),
                }
            )
            await ctx.respond(f"Role <@&{role.id}> given for {duration} seconds")
        except discord.DiscordException:
            await ctx.respond("Bot should have a role higher than you to assign roles")

    @reveal.error
    async def reveal_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.respond("This role is not a temporary role.")
        else:
            raise error


def run():
    intents = discord.Intents()
    intents.message_content = True

    bot = bridge.Bot(command_prefix=".", intents=intents)

    load_dotenv()
    TOKEN = os.getenv("DISCORD_TOKEN")
    MONGO_DATABASE = os.getenv("MONGO_DATABASE")
    MONGO_PORT = os.getenv("MONGO_PORT")
    PORTAL_LINK = os.getenv("PORTAL_LINK")
    bot.add_cog(CasBot(bot, MONGO_DATABASE, MONGO_PORT, PORTAL_LINK))
    bot.run(TOKEN)


if __name__ == "__main__":
    run()
