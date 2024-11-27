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
        TEST_SERVER_ID = os.getenv('TEST_SERVER_ID')
        if TEST_SERVER_ID is not None:
            await bot.sync_commands(guild_ids=[TEST_SERVER_ID])
        else:
            await bot.sync_commands()
    print(f"{bot.user.name} connected.")


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

load_dotenv()
asyncio.run(main())
