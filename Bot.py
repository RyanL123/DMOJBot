import discord
import requests
from config import *
from discord.ext import commands, tasks

prefix = "$"
bot = commands.Bot(command_prefix=prefix, help_command=None)

@bot.event
async def on_read():
    await bot.change_presence(activity=discord.Game(name="%submissions"))

@bot.command()
async def submissions(ctx, user=None, num=1):
    if user is None:
        await ctx.channel.send("No user is given")
        return
    try:
        user_submissions = requests.get("https://dmoj.ca/api/user/submissions/" + user).json()
        keys = list(user_submissions.keys())
        if num > 10:
            await ctx.channel.send("You can only get a maximum of 10 problems")
            return
        for i in range(1, num+1):
            status = user_submissions[keys[-i]]['result']
            problem = requests.get("https://dmoj.ca/api/problem/info/" + user_submissions[keys[-i]]['problem']).json()["name"]
            if status == "AC":
                await ctx.channel.send(user + " AC'd on " + problem + " HOLY SHIT <:PogU:594138006999269427>")
            else:
                await ctx.channel.send(user + " FUCKING " + status + "'d on " + problem + " LMAOOOOOO <:PepeLaugh:594138680898355200>")
    except:
        await ctx.channel.send("That user does not exist")

bot.run(api_key)