import discord
from discord.ext import commands, tasks
import random as rnd
import csv
import os
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("bot-token")
userid = os.environ.get("userid")

description = '''A bot telling you the secrets of cheese...'''

intents = discord.Intents.default()
cheese_dict = {}
cheese_key_list = []

bot = commands.Bot(command_prefix='c!', description=description, intents=intents, owner_id=userid)


def WrongIdError():
    pass


def load_cheese():
    cheese_dict.clear()
    cheese_key_list.clear()
    with open('cheeselist.csv', newline='', encoding="UTF-8") as cheese_list:
        cheese_reader = csv.reader(cheese_list, delimiter=';', quotechar='"')
        for cheese in cheese_reader:
            if cheese[0] == "id":
                continue
            cheese_dict[cheese[0]] = [cheese[1], cheese[2], cheese[3], cheese[4], cheese[5]]
            cheese_key_list.append(cheese[0])


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    load_cheese()
    print("loaded " + str(len(cheese_dict)) + " kinds of cheese")


@bot.command(aliases=['rl'])
@commands.is_owner()
async def reload(ctx):
    """Reloads the cheese-list (dev only)"""
    print("manual reload")
    load_cheese()
    print("loaded " + str(len(cheese_dict)) + " kinds of cheese")
    await ctx.send("Devbot: loaded " + str(len(cheese_dict)) + " kinds of cheese")


@bot.command(description="Cheeeeese!")
async def heese(ctx):
    """Says Cheeeeese!"""
    await ctx.send("Cheeeeese!")


@bot.command(aliases=['r'], description="Show a random cheese!")
async def random(ctx):
    """(c!r) Shows a random cheese!"""
    cheese_entry = cheese_dict[rnd.choice(list(cheese_dict.keys()))]
    print(cheese_entry)
    cheese_embed = discord.Embed(title=cheese_entry[0], description=cheese_entry[4], url=cheese_entry[3])
    cheese_embed.set_image(url=cheese_entry[2])
    cheese_embed.set_author(name=cheese_entry[1])
    await ctx.send(embed=cheese_embed)


@bot.command(aliases=['s'], description="Search for cheese, enter a keyword to find cheese.")
async def search(ctx, *, searchterm):
    """(c!s) Search for cheese, enter a keyword to find cheese."""
    if searchterm in cheese_key_list:
        cheese_entry = cheese_dict[searchterm]
        print(cheese_entry)
        cheese_embed = discord.Embed(title=cheese_entry[0], description=cheese_entry[4], url=cheese_entry[3])
        cheese_embed.set_image(url=cheese_entry[2])
        cheese_embed.set_author(name=cheese_entry[1])
        await ctx.send(embed=cheese_embed)
    elif any(searchterm in cheese for cheese in cheese_key_list):
        search_list = []
        for cheese in cheese_key_list:
            if searchterm in cheese:
                search_list.append(cheese)
                print(cheese)
        search_out = "\n".join(search_list)
        search_embed = discord.Embed(title="Search:",
                                     description="Choose one of these for more information:\n" + search_out)
        await ctx.send(embed=search_embed)
    else:
        await ctx.send("Nothing found...")


bot.run(token)
