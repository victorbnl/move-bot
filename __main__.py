#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import discord
from discord.ext import commands

# Read token
with open("token.txt", "r") as file_:
    token = file_.read().strip()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Ready message
@bot.event
async def on_ready():
    print("Ready")

# Test say command
@bot.command(enabled=False)
async def say(ctx, arg):
    await ctx.message.delete()
    avatar = await ctx.author.display_avatar.read()
    webhook = await ctx.channel.create_webhook(name="Move bot")
    await webhook.send(arg, username=ctx.author.name, avatar_url=ctx.author.avatar.url)
    await webhook.delete()

# Move command
@bot.command()
@commands.has_permissions(manage_messages=True)
async def move(ctx, number: int, channel: discord.TextChannel):

    # Delete command message
    await ctx.message.delete()

    # List of sent messages
    sent_messages = {}

    # Get messages history
    messages = [message async for message in ctx.channel.history(limit=number)]
    messages.reverse()

    # Delete messages
    def true(m): return True
    await ctx.channel.purge(limit=number, check=true)

    # Create webhook
    webhook = await channel.create_webhook(name="Move Bot")

    # Move each message
    for message in messages:

        # Get attachments
        files = []
        for attachment in message.attachments:
            file_ = await attachment.to_file()
            files.append(file_)
        
        # If reply
        if message.reference:
            if message.reference.message_id in sent_messages.keys():
                ref = "Replying to <{}>".format(sent_messages[message.reference.message_id].jump_url)
            else:
                msg = await ctx.channel.fetch_message(message.reference.message_id)
                ref = "Replying to <{}>".format(msg.jump_url)
            content = "*__{}__*\n{}".format(ref, message.content)
        else:
            content = message.content
        
        # Args of send()
        args = {
            "content": content,
            "embeds": message.embeds,
            "files": files,
        }

        # Send message and delete it from original channel
        sent_messages[message.id] = await webhook.send(
            username=message.author.name,
            avatar_url=message.author.avatar.url,
            wait=True,
            **args
        )

    # Delete webhook
    await webhook.delete()

    # Moved message
    await ctx.send("{} messages moved in {}".format(number, channel.mention), delete_after=30)

bot.run(token)
