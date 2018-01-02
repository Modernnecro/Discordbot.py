#!/usr/bin/env python3.6
import logging
import random
import asyncio
import requests

import discord
from discord.ext import commands

import discord.utils as utils

logging.basicConfig(level='INFO')

bot = commands.Bot(command_prefix='-')

response = requests.get('https://status.discordapp.com/api/v2/summary.json')
data = response.json()

timeout_buckets = 0
def add_bucket():
    # Have to do this to be allowed to mutate it
    global timeout_buckets
    timeout_buckets += 1

    # Async callback to perform in the background
    async def decrement():
        # Sleep 10 minutes
        await asyncio.sleep(10 * 60)
        # Remove the bucket
        global timeout_buckets
        timeout_buckets -= 1

    # Runs the coroutine in the background without
    # waiting for it to finish
    asyncio.ensure_future(decrement())

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
async def on_message(message):
    # random.random() returns a number in the range [0, 1].
    is_hello = message.content.lower().startswith('hello')
    # To access global scope, we don't have to add the global line.
    # Yeah... still haven't quite sussed the point of that one xD
    is_on_timeout = timeout_buckets > 0
    is_permitted = random.random() < 0.25

    if is_hello and is_permitted and not is_on_timeout:    
        await message.channel.send('Hiya!')
        add_bucket()

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
