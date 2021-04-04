import os

import discord
from dotenv import load_dotenv

from discord.ext import commands

from pymongo import MongoClient

mongo_client = MongoClient("mongodb+srv://dev:hidenseek@cluster0.ulzen.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = mongo_client.get_database("discord-cas")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=':')

def is_verified(user_id):
    users = list(db.users.find({"user_id": user_id}))
    return True if len(users) else False
    

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name="verify")
async def verify_user(ctx):
    user_id = ctx.message.author.id
    if is_verified(user_id):
        await ctx.send(f"Yayy verified")
    else:
        await ctx.send(f"Ew not verified {user_id}")


bot.run(TOKEN)