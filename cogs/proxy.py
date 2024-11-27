from typing import Optional
import discord
from discord.ext import commands

from gateways.persistence._interface import PersistenceGateway
from gateways.persistence.in_memory import InMemoryPersistenceGatewayImpl
from gateways.persistence.sql_lite import SqlLitePersistenceGatewayImpl
from models.proxy import Proxy


def setup(bot):
    persistence_gateway = SqlLitePersistenceGatewayImpl()
    cog = Proxy(bot, persistence_gateway)
    bot.add_cog(cog)


class Proxy(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot,
        persistenceGateway: PersistenceGateway,
    ):
        self.bot: commands.Bot = bot
        self.persistenceGateway: PersistenceGateway = persistenceGateway

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message,
    ):
        server_id: int = message.guild.id
        await self.handle_message(server_id, message)

    async def cog_command_error(
        self,
        ctx: discord.ApplicationContext,
        error: commands.CommandError,
    ):
        await ctx.respond(f'Error processing your message. Details: {error.args[0]}')

    @discord.slash_command()
    async def add_proxy_to_channel(
        self,
        ctx: discord.ApplicationContext,
        target: discord.TextChannel,
        filter: discord.Member,
    ):
        await self.add_proxy(ctx, target, filter)


    @discord.slash_command()
    async def add_proxy_to_forum(
        self,
        ctx: discord.ApplicationContext,
        target: discord.Thread,
        filter: discord.Member,
    ):
        await self.add_proxy(ctx, target, filter)

    async def add_proxy(
        self,
        ctx: discord.ApplicationContext,
        target: Optional[discord.Thread|discord.TextChannel],
        filter: discord.Member,
    ):
        server_id: int = self.get_server_id_from_context(ctx)
        server_proxy: Proxy = self.persistenceGateway.get_proxy(server_id)
        if server_proxy is None:
            return

        server_proxy.add_rule(filter.name, target.id)
        self.persistenceGateway.store_proxy(server_id, server_proxy)

        await ctx.respond(f'Listening from {server_proxy.get_announce_channel()} to {target} from author {filter}...')


    @discord.slash_command()
    async def set_announce_channel(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.TextChannel,
    ):
        server_id: int = self.get_server_id_from_context(ctx)
        server_proxy: Proxy = self.persistenceGateway.get_proxy(server_id)
        if server_proxy is None:
            return

        server_proxy.set_announce_channel(channel.id)
        self.persistenceGateway.store_proxy(server_id, server_proxy)

        await ctx.respond(f'Announce channel set as {server_proxy.get_announce_channel()}')

    @discord.slash_command()
    async def print_proxy(
        self,
        ctx: discord.ApplicationContext,
    ):
        server_id: int = self.get_server_id_from_context(ctx)
        server_proxy: Proxy = self.persistenceGateway.get_proxy(server_id)
        if server_proxy is None:
            return

        msg = ""
        for item in self.server_proxy._rules:
            channel = f'<#{self.proxy.rules[item]}>'
            msg += f"Sending msg to {channel} if message matches with the filter (author) = {item}"
            msg += "\n"

        await ctx.respond(msg)

    async def handle_message(
        self,
        server_id: int,
        message: discord.Message,
    ):
        author = message.author
        if author == self.bot.user:
            return

        server_proxy: Proxy = self.persistenceGateway.get_proxy(server_id)
        if server_proxy is None:
            return

        inputChannel = server_proxy.get_announce_channel()
        if inputChannel is None or message.channel.id != inputChannel:
            return

        # # Forwarding message
        target_channel_id = server_proxy.get_forward_channel(author.name)
        target_channel = self.bot.get_channel(target_channel_id)
        message_data = message.to_reference()
        link = f"https://discord.com/channels/{message_data.guild_id}/{message_data.channel_id}/{message_data.message_id}"
        bot_message = f"A new message from {author.mention} arrive! Please check here: {link}"
        await target_channel.send(bot_message)

    def get_server_id_from_context(self, ctx: discord.ApplicationContext) -> int:
        return ctx.guild.id
