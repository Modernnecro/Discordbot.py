#!/usr/bin/env python3.6
import logging
import random
import asyncio
import requests

import discord
from discord.ext import commands

import discord.utils as utils

logging.basicConfig(level='INFO')

bot = commands.Bot(command_prefix='-', owner_id=182905629516496897)

response = requests.get('https://status.discordapp.com/api/v2/summary.json')
data = response.json()

responses = ['Hiya!', 'Howdy', 'Howcha doin?']

triggers = ['hello', 'hi', 'hiya',  'waves']

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

@bot.command(usage='(your message here)' )
async def talk(ctx, *, msg):
    """
    A simple command that makes the bot leave out the command and repeat all the text it receives.
    """
    await ctx.message.delete()
    await ctx.send(msg)

@bot.command(usage='Used to get a random number, either 1 or 2 OR from a list up to a given number')
async def spin(ctx, *, num: int):
    """
    A command that's there to make a decision based upon a number variable. Either give a number, or make the bot toss a "coin"
    """
    if (num > 0):
        answer = random.randint(1, num)
        ctx.send('You got ' + str(answer))
    elif (num <= 0):
        ctx.send('You need to give a number higher than 0')
    elif (num is None):
        answer = random.randint(1, 2)
        ctx.send('You got ' + str(answer))

@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return

    if 'shut up apple' in message.content.lower():
        print('Whelp, getting shut upped')
        if message.author.id == bot.owner_id:
            await message.channel.send('YOU CANT TELL ME WHAT TO DO!! Wait... You can.')
        else:
            await message.channel.send('NO! You meanie! \N{LOUDLY CRYING FACE}')

@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return


    cont = message.content
    lcont = cont.lower()

    # random.random() returns a number in the range [0, 1].
    is_hello = any(message.content.lower().startswith(t) for t in triggers)
    # To access global scope, we don't have to add the global line.
    # Yeah... still haven't quite sussed the point of that one xD
    is_on_timeout = timeout_buckets > 0

    if is_hello and not is_on_timeout:
        response = random.choice(responses)
        await message.channel.send(response)
        add_bucket()

@bot.listen()
async def on_member_join(member):
    if not member.bot:
        guild = member.guild
        channel = get_general(guild)
        await channel.send(f'Welcome to {guild.name}, {member.name}!, please read the rules first.')

@bot.listen()
async def on_member_remove(member):
    if not member.bot:
        print('Hello darkness my old friend.')
        guild = member.guild
        channel = get_general(guild)
        await channel.send(f'{member.name} just left and will be missed.')

@bot.listen()
async def on_member_ban(guild, user):
    if not user.bot: 
        channel = get_general(guild)
        await channel.send(f'{user} just got banned from the {guild}.')


#ensures the command only works for the owner.
@commands.is_owner()
@bot.command(aliases=['kill', 'stop', 'shutdown', 'bedtime'])
async def die(ctx):
    await ctx.bot.logout()

with open('token.txt') as fp:
    token = fp.read().strip()

bot.run(token)
