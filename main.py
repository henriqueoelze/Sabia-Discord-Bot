import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

intents = discord.Intents.default()
intents.message_content = True
intents.webhooks = True

bot_prefix = "/"
bot = commands.Bot(intents=intents)


async def load_cogs():
    bot.load_extension('cogs.proxy')


async def main():
    async with bot:
        BOT_TOKEN = os.getenv('BOT_TOKEN')
        LOG_LEVEL = os.getenv('LOG_LEVEL') if os.getenv(
            'LOG_LEVEL') is not None else 'INFO'

        # Log setup
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('discord')
        logger.setLevel(logging.getLevelName(LOG_LEVEL))
        handler = logging.FileHandler(
            filename='discord.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)

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
