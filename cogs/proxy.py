from typing import Optional
import discord
from discord.ext import commands

from gateways.persistence._interface import PersistenceGateway
from gateways.persistence.in_memory import InMemoryPersistenceGatewayImpl
from gateways.persistence.sql_lite import SqlLitePersistenceGatewayImpl
from models.proxy import Proxy as ProxyModel


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

    @discord.slash_command(description='Add the routing rule from your configuration given the webhook id')
    async def add_rule(
        self,
        ctx: discord.ApplicationContext,
        webhook_id,
        destination: discord.Thread,
    ):
        server_id: int = self.get_server_id_from_context(ctx)
        server_proxy: ProxyModel = await self.persistenceGateway.get_proxy(server_id)
        if server_proxy is None:
            return

        server_proxy.add_rule(webhook_id, destination.id)
        await self.persistenceGateway.store_proxy(server_id, server_proxy)

        await ctx.respond(f'Rule created :white_check_mark: \nWebhook {webhook_id} routed to {destination}')

    @discord.slash_command(description='Remove the routing rule from your configuration given the webhook id')
    async def remove_rule(
        self,
        ctx: discord.ApplicationContext,
        webhook_id,
    ):
        server_id: int = self.get_server_id_from_context(ctx)
        server_proxy: ProxyModel = await self.persistenceGateway.get_proxy(server_id)
        if server_proxy is None:
            return

        server_proxy.remove_rule(webhook_id)
        await self.persistenceGateway.store_proxy(server_id, server_proxy)

        await ctx.respond(f'Rule removed :white_check_mark: \nWebhook {webhook_id} won\'t be routed anymore.')

    @discord.slash_command(description='Set the channel where your server is listening to the other servers messages')
    async def set_announce_channel(
        self,
        ctx: discord.ApplicationContext,
        channel: discord.TextChannel,
    ):
        server_id: int = self.get_server_id_from_context(ctx)
        server_proxy: ProxyModel = await self.persistenceGateway.get_proxy(server_id)
        if server_proxy is None:
            return

        server_proxy.set_announce_channel(channel.id)
        await self.persistenceGateway.store_proxy(server_id, server_proxy)

        await ctx.respond(f'Announce channel set as <#{channel.id}>')

    @discord.slash_command(description='Print the whole server configuration')
    async def print_config(
        self,
        ctx: discord.ApplicationContext,
    ):
        server_id: int = self.get_server_id_from_context(ctx)
        server_proxy: ProxyModel = await self.persistenceGateway.get_proxy(server_id)
        if server_proxy is None:
            await ctx.respond('No configuration found!')
            return

        server_webhooks: list[discord.Webhook] = await ctx.guild.webhooks()
        server_listeners: list[discord.Webhook] = [
            webhook for webhook in server_webhooks if webhook.type == discord.WebhookType.channel_follower]

        webhooks_without_rule: list[discord.Webhook] = [
            webhook for webhook in server_listeners if not server_proxy.has_rule(webhook.id)]
        msg = ''
        msg += f'Announcements channel: <#{server_proxy.announce_channel_id}>\n'
        msg += '\n=> Webhooks WITHOUT configuration: \n'

        if len(webhooks_without_rule) == 0:
            msg += 'None\n'
        else:
            for webhook_id in webhooks_without_rule:
                msg += f'Webhook id `{webhook_id.id}` `({webhook_id.name})`\n'

        msg += '\n=> Webhooks WITH configuration: \n'
        current_rules = server_proxy.get_all()
        if len(current_rules) == 0:
            msg += 'None\n'
        else:
            for webhook_id in current_rules:
                webhook_obj = [
                    webhook for webhook in server_listeners if webhook.id == int(webhook_id)][0]
                thread = f'<#{current_rules[webhook_id]}>'
                msg += f'Webhook id `{webhook_id}` `({webhook_obj.name})` being forward to {thread}.'
                msg += '\n'

        await ctx.respond(msg)

    async def handle_message(
        self,
        server_id: int,
        message: discord.Message,
    ):
        author = message.author
        if author == self.bot.user:
            return

        webhook_id = message.webhook_id
        if webhook_id is None:
            return

        server_proxy: ProxyModel = await self.persistenceGateway.get_proxy(server_id)
        if server_proxy is None:
            return

        inputChannel = server_proxy.get_announce_channel()
        if inputChannel is None or message.channel.id != inputChannel:
            return

        # # Forwarding message
        target_channel_id = server_proxy.get_destination(webhook_id)
        target_channel = self.bot.get_channel(target_channel_id)
        message_data = message.to_reference()
        link = f'https://discord.com/channels/{message_data.guild_id}/{message_data.channel_id}/{message_data.message_id}'
        bot_message = f'A new message from {author.mention} arrive! Please check here: {link}'
        await target_channel.send(bot_message)

    def get_server_id_from_context(self, ctx: discord.ApplicationContext) -> int:
        return ctx.guild.id
