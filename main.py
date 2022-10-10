# welcome to too many comments, have fun

import discord                  # self-explanatory
from discord.ext import tasks   # for the status updates
import random as rnd            # for choosing a random status update
import csv                      # for reading in the csv files for the cheeselist and the statuslist
from dotenv import load_dotenv  # for reading the .env file with the bot token (and owner id)
import os                       # for getting the environment variables (which I just wrote, who came up with this shit?)


# loads the .env file with the bot token (and owner id)
load_dotenv()  
token = os.environ.get("bot-token")
userid = os.environ.get("userid")

# setting file locations
datafile = 'cheeselist.csv'
statusfile = 'statuslist.csv'

# setting some basic variables, setting intents and creating basic variables
description = '''A bot telling you the secrets of cheese...'''
intents = discord.Intents.default()
data_dict = {}    # all the data from the datafile
data_key_list = []    # just the ids from the datafile for easier random choosing
status_list = []    # the list for all the status messages

# setting up the bot object
bot = discord.Bot(description=description, intents=intents, owner_id=int(userid))


# class for loading the data from the datafile into the variables
def load_data():
    data_dict.clear()
    data_key_list.clear() # clear both dict and list
    with open(datafile, newline='', encoding="UTF-8") as data_list:   # open the datafile
        data_reader = csv.reader(data_list, delimiter=';', quotechar='"')   # read the csv
        # split all the data up into the dictionary
        for data in data_reader:
            if data[0] == "id":
                continue
            data_dict[data[0]] = [data[1], data[2], data[3], data[4], data[5]]
            data_key_list.append(data[0])  


# class for loading the status entries from the statusfile into the statuslist
def load_status():
    status_list.clear() # clear the list
    with open(statusfile, newline='', encoding="UTF-8") as status_file: # open the statusfile
        status_reader = csv.reader(status_file, delimiter=';', quotechar='"')   # read the csv
        # split all the status entries up and add them to the list
        for status in status_reader:
            status_list.append((status[0], status[1]))


# class for changing the status every 5 minutes
@tasks.loop(minutes=5)  # the 5 minute timer
async def statusChange():
    status_output = rnd.choice(status_list) # chooses a random entry from the status list
    print("changing status to ",status_output)
    # set the status based on the type identifier p, l or w
    if status_output[0] == "p":
        await bot.change_presence(activity=discord.Game(status_output[1]))  # "playing something"
    elif status_output[0] == "l":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=status_output[1]))    # "listening to something"
    elif status_output[0] == "w":
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_output[1])) # "watching something"


# class that runs at startup of the bot
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('Bot owner is:',userid)
    load_data() # load the data into the dictionary
    print("loaded " + str(len(data_dict)) + " kinds of cheese")
    load_status()   # load the status entries into the list
    print("loaded " + str(len(status_list)) + " different status messages")
    statusChange.start()    # IMPORTANT!!! If you don't call the task like shown here it wont run, took me half an hour to realize lol


# reloads both lists, mostly just in here so I don't have to restart the bot on list changes
@bot.command(description="Reloads the cheese-list (dev only)")
# @bot.is_owner()   # why did you have to kill this, discord?!? WHY???
async def reload(ctx):
    await ctx.response.defer()  # Those defer commands are in here because discord shits the bed otherwise and spams my log (while still running normally on the outside)
    # all this if statement shit to check if the calling user is owner instead of the old version on top...
    if (await bot.is_owner(ctx.user)):
        print("manual reload triggered in",ctx.guild)
        load_data() # load the data into the dictionary
        print("loaded " + str(len(data_dict)) + " kinds of cheese")
        load_status()   # load the status entries into the list
        print("loaded " + str(len(status_list)) + " different status messages")
        await ctx.respond("Devbot: loaded " + str(len(data_dict)) + " kinds of cheese and " + str(len(status_list)) + " different status messages.")    # sends the reload status into chat
    else:
        await ctx.respond("You're not a dev.")  # skill issue


# command for everyone stupid enough to want this bot too
@bot.command(description="Get all information on using this Bot for your own server!")
async def invite(ctx):
    await ctx.response.defer()
    print("Called invite in: ",ctx.guild)
    await ctx.respond("You want to use this bot on your own server?\nEither ask Icericus#3141 or get the code on https://github.com/Icericus/CheeseBot")


# command to show a random data entry as a fancy embed
@bot.command(description="Show a random cheese")
async def random(ctx):
    await ctx.response.defer()
    data_entry = data_dict[rnd.choice(list(data_dict.keys()))]  # chooses a random entry from the data keylist and plugs it into the dictionary to get all data on the chosen id
    print("Called random with: ",data_entry[0],"on server:",ctx.guild)
    # create the embed, this syntax sucks but it works
    data_embed = discord.Embed(title=data_entry[0], description=data_entry[4], url=data_entry[3])
    data_embed.set_image(url=data_entry[2])
    data_embed.set_author(name=data_entry[1])
    await ctx.respond(embed=data_embed) # and send the embed


# command to search for a specific entry by its id in the keylist
@bot.command(description="Search for cheese, enter a keyword to find cheese")
async def search(ctx, searchterm):
    await ctx.response.defer()
    print("Called search with: ",searchterm,"on server:",ctx.guild)
    # if there's a 1:1 match it just outputs the found entry (as an embed of course)
    if searchterm in data_key_list:
        data_entry = data_dict[searchterm]
        data_embed = discord.Embed(title=data_entry[0], description=data_entry[4], url=data_entry[3])
        data_embed.set_image(url=data_entry[2])
        data_embed.set_author(name=data_entry[1])
        await ctx.respond(embed=data_embed)
    # if there's more than one key fitting the search term it outputs a list of all the keys/ids
    elif any(searchterm in data for data in data_key_list):
        search_list = []
        for data in data_key_list:
            if searchterm in data:
                search_list.append(data)
        search_out = "\n".join(search_list)
        search_embed = discord.Embed(title="Search:",
                                     description="Choose one of these for more information:\n" + search_out)
        await ctx.respond(embed=search_embed)
    # and of course if it doesn't find anything it tells you that
    else:
        await ctx.respond("Nothing found...")


bot.run(token)  # the one call starting everything else
