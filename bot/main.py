import os

import discord
from dotenv import load_dotenv

from discord.ext import commands

from pymongo import MongoClient

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_DATABASE= os.getenv("MONGO_DATABASE")

mongo_client = MongoClient(f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.lkxfy.mongodb.net/{MONGO_DATABASE}?retryWrites=true&w=majority")
db = mongo_client.get_database(MONGO_DATABASE)

bot = commands.Bot(command_prefix=';')

is_configured = False
configured_role = None
VERIFIED_ROLE_NAME = "cas-verified"


async def is_verified(user_id):
    users = list(db.users.find({"discordId": str(user_id)}))
    return True if len(users) else False


async def send_link(ctx):
    LINK_TEXT = "*link*"
    await ctx.send(f"{LINK_TEXT}\nSign in to CAS and try again.")


async def assign_role(ctx, user):
    if not is_configured:
        roles = ctx.guild.roles
        role_names = [role.name for role in roles]

        if VERIFIED_ROLE_NAME not in role_names:
            await ctx.guild.create_role(name=VERIFIED_ROLE_NAME)

        required_role = [role for role in roles if role.name == VERIFIED_ROLE_NAME][0]

    else:
        required_role = configured_role

    await user.add_roles(required_role)
    await ctx.send(f"<@{user.id}> has been CAS-verified.")


@bot.command(name="verify")
async def verify_user(ctx):
    user_id = ctx.message.author.id
    verification = await is_verified(user_id)

    if verification:
        await assign_role(ctx, ctx.message.author)
        await ctx.send(f"Yayy verified")
    else:
        await send_link(ctx)


@commands.has_permissions(administrator=True)
@bot.command(name="configure")
async def configure_verification_role(ctx, role: discord.Role):
    global configured_role, is_configured
    configured_role = role
    is_configured = True
    await ctx.send(f"Verified role set to {role.name}")    

@configure_verification_role.error
async def configure_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You must be an admin to configure roles")
    elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.RoleNotFound):
        await ctx.send("Please specify a role.")


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

bot.run(TOKEN)
