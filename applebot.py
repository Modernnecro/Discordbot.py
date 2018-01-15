#!/usr/bin/env python3.6
import logging
import random
import asyncio
import re

import discord
from discord.ext import commands

import discord.utils as utils

def starts_with_word(string, word, case_insensitive=True):
    return re.match(r'^%s\b' % word, string, re.I if case_insensitive else 0)

class Applebot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self._game = None
        self._status = discord.Status.online
        super().__init__(*args, **kwargs)

    async def change_presence(self, **kwargs):
        if 'game' not in kwargs:
            kwargs['game'] = self._game
        else:
            self._game = kwargs['game']

        if 'status' not in kwargs:
            kwargs['status'] = self._status
        else:
            self._status = kwargs['status']

        await super().change_presence(**kwargs)

logging.basicConfig(level='INFO')

bot = Applebot(command_prefix='-', owner_id=182905629516496897)

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

@bot.command(usage='x y (both are numbers)')
async def d(ctx, sides=6, times=1):
    """
    Makes the bot roll a dice of x sides y times
    """
    a = 0
    results = [str(random.randint(1, sides)) for _ in range(0, times)]
    for ans in results:
        a = a + int(ans)
    await ctx.send(f'{", ".join(results)}\nThe resulting score is: {a}.')

@bot.listen()
async def on_ready():
    print('Ready and connected')

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

@bot.command(usage='(game to play here)')
async def game(ctx, *, msg):
    """
    A command that makes the bot "play" a game.
    """
    await bot.change_presence(game = discord.Game(name = msg))

@bot.command()
async def status(ctx, *, status_str):
    available_statuses = {
        'online': discord.Status.online,
        'dnd': discord.Status.dnd,
        'idle': discord.Status.idle,
        'offline': discord.Status.invisible
    }

    if status_str not in available_statuses:
        await ctx.send(f'Valid statuses are: {", ".join(available_statuses.keys())}')
    else:
        await bot.change_presence(status=available_statuses[status_str])

@bot.command(usage='(number or text)', aliases=['flip', 'dice', 'roll', 'choice', 'toss'])
async def spin(ctx, *, num=None):
    """
    Rolls a die of a given value. Defaults to flipping a coin if no value is given.
    If the value is a string, it "spins around" the object, or string.
    """
    if num is None:
        num = 2
    try:
        num = int(num)
        assert num > 1
    except ValueError:
        for character in ('~~', '`', '_', '*'):
            num = num.replace(character, '')
        await ctx.send(f'_Spins {num} around._')
    except AssertionError:
        await ctx.send('Please make the number bigger than 1.')
    else:
        await ctx.send(f'You got {random.randint(1, num)}')

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
    is_hello = any(starts_with_word(message.content, word) for word in triggers)
    print(is_hello)
    # To access global scope, we don't have to add the global line.
    # Yeah... still haven't quite sussed the point of that one xD
    is_on_timeout = timeout_buckets > 0

    if is_hello and not is_on_timeout:
        if random.randint(1, 10) == 5:
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

@bot.command(aliases=['kill', 'stop', 'shutdown', 'bedtime'])
async def die(message):
    if message.author.id == bot.owner_id:
        await message.channel.send('Okay, goodnight everyone! See you soon.')
        await bot.logout()
    else:
        await message.channel.send('NOT LISTENING!! LALALALALALALA')



with open('token.txt') as fp:
    token = fp.read().strip()

bot.run(token)
