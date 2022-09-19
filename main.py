from tokenize import String
import discord
# from discord.ext import commands, tasks
import random as rnd
import csv
import os
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("bot-token")
userid = os.environ.get("userid")

datafile = 'cheeselist.csv'

description = '''A bot telling you the secrets of cheese...'''

intents = discord.Intents.default()
cheese_dict = {}
cheese_key_list = []

bot = discord.Bot(description=description, intents=intents, owner_id=int(userid))


def WrongIdError():
    pass


def load_cheese():
    cheese_dict.clear()
    cheese_key_list.clear()
    with open(datafile, newline='', encoding="UTF-8") as cheese_list:
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
    print('Bot owner is:',userid)
    load_cheese()
    print("loaded " + str(len(cheese_dict)) + " kinds of cheese")


@bot.command(description="Reloads the cheese-list (dev only)")
# @bot.is_owner()
async def reload(ctx):
    await ctx.response.defer()
    if (await bot.is_owner(ctx.user)):
        print("manual reload triggered in",ctx.guild)
        load_cheese()
        print("loaded " + str(len(cheese_dict)) + " kinds of cheese")
        await ctx.respond("Devbot: loaded " + str(len(cheese_dict)) + " kinds of cheese")
    else:
        await ctx.respond("You're not a dev.")


@bot.command(description="Get all information on using this Bot for your own server!")
async def invite(ctx):
    await ctx.response.defer()
    print("Called invite in: ",ctx.guild)
    await ctx.respond("You want to use this bot on your own server?\nEither ask Icericus#3141 or get the code on https://github.com/Icericus/CheeseBot")


@bot.command(description="Show a random cheese")
async def random(ctx):
    await ctx.response.defer()
    cheese_entry = cheese_dict[rnd.choice(list(cheese_dict.keys()))]
    print("Called random with: ",cheese_entry[0],"on server:",ctx.guild)
    cheese_embed = discord.Embed(title=cheese_entry[0], description=cheese_entry[4], url=cheese_entry[3])
    cheese_embed.set_image(url=cheese_entry[2])
    cheese_embed.set_author(name=cheese_entry[1])
    await ctx.respond(embed=cheese_embed)


@bot.command(description="Search for cheese, enter a keyword to find cheese")
async def search(ctx, searchterm):
    await ctx.response.defer()
    print("Called search with: ",searchterm,"on server:",ctx.guild)
    if searchterm in cheese_key_list:
        cheese_entry = cheese_dict[searchterm]
        cheese_embed = discord.Embed(title=cheese_entry[0], description=cheese_entry[4], url=cheese_entry[3])
        cheese_embed.set_image(url=cheese_entry[2])
        cheese_embed.set_author(name=cheese_entry[1])
        await ctx.respond(embed=cheese_embed)
        
    elif any(searchterm in cheese for cheese in cheese_key_list):
        search_list = []
        for cheese in cheese_key_list:
            if searchterm in cheese:
                search_list.append(cheese)
                #print(cheese)
        search_out = "\n".join(search_list)
        search_embed = discord.Embed(title="Search:",
                                     description="Choose one of these for more information:\n" + search_out)
        await ctx.respond(embed=search_embed)
    else:
        await ctx.respond("Nothing found...")


bot.run(token)
