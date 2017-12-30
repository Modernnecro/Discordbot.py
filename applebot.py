#!/usr/bin/env python3.6
import logging

import discord
from discord.ext import commands

import discord.utils as utils

logging.basicConfig(level='INFO')

bot = commands.Bot(command_prefix='-')

def get_general(guild):
    chan = utils.find(lambda c: c.name =='general', guild.channels)
    return chan if chan else guild.channels[0]

@bot.command( )
async def hello(ctx):
    await ctx.send('Hello')

@bot.command(usage='(your message here)' )
async def talk(ctx, *, msg):
    """
    A simple command that makes the bot leave out the command and repeat all the text it receives.
    """
    await ctx.message.delete()
    await ctx.send(msg)

@bot.listen()
async def on_member_join(member):
    guild = member.guild
    channel = get_general(guild)
    await channel.send(f'Welcome to {guild.name}, {member.name}!, please read the rules first.')

@bot.listen()
async def on_member_leave(member):
    guild = member.guild
    channel = get_general(guild)
    await channel.send(f'{member.name} just left. He will be missed.')

with open('token.txt') as fp:
    token = fp.read().strip()

bot.run(token)
