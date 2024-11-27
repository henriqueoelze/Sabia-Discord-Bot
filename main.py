import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

bot_prefix = "/"
bot = commands.Bot(intents=intents)


async def load_cogs():
    bot.load_extension('cogs.proxy')


async def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    await load_cogs()
    await bot.start(BOT_TOKEN)


@bot.event
async def on_connect():
    if bot.auto_sync_commands:
        await bot.sync_commands(guild_ids=[1309197374127607808])
    print(f"{bot.user.name} connected.")


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

load_dotenv()
asyncio.run(main())
