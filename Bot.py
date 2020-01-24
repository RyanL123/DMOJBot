import discord
import json
import requests
from config import *
from discord.ext import commands, tasks

prefix = "$"
bot = commands.Bot(command_prefix=prefix, help_command=None)


@bot.command()
async def submissions(ctx, user="bartpuup", num=1):
    try:
        user_submissions = requests.get("https://dmoj.ca/api/user/submissions/" + user).json()
        keys = user_submissions.keys()
        for i in range(1, num+1):
            status = user_submissions[list(keys)[-i]]['result']
            problem = requests.get("https://dmoj.ca/api/problem/info/" + user_submissions[list(keys)[-i]]['problem']).json()["name"]
            if user == "Davidli3100":
                await ctx.channel.send("David is fucking gay lol <:PepeLaugh:594138680898355200>")
            elif status == 'TLE':
                await ctx.channel.send(user + " FUCKING TLE'd on " + problem + " LMAOOOOOO <:PepeLaugh:594138680898355200>")
            elif status == 'WA':
                await ctx.channel.send(user + " FUCKING WA'd on " + problem + " LMAOOOOOOOOOOOOOOOOOOOO <:PepeLaugh:594138680898355200>")
            elif status == 'AC':
                await ctx.channel.send(user + " AC'D on " + problem + "HOLY SHIT <:PogU:594138006999269427>")
    except:
        await ctx.channel.send("That user does not exist")

bot.run(api_key)