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
    # No user is given
    if user is None:
        await ctx.channel.send("No user is given")
        return
    user_submissions = None
    # Attempts to get user submissions
    try:
        user_submissions = requests.get("https://dmoj.ca/api/user/submissions/" + user).json()
    except:
        await ctx.channel.send("That user does not exist")
    # Keys of submissions dict
    keys = list(user_submissions.keys())
    # No more than 10 submissions is allowed
    if num > 10:
        await ctx.channel.send("You can only get a maximum of 10 problems")
        return
    for i in range(1, num+1):
        status = user_submissions[keys[-i]]['result']
        # Get problem details and convert to dict
        problem = requests.get("https://dmoj.ca/api/problem/info/" + user_submissions[keys[-i]]['problem']).json()
        # Get specific info
        problem_name = problem["name"]
        problem_points = problem["points"]
        problem_link = "https://dmoj.ca/problem/" + user_submissions[keys[-i]]['problem']
        if status == "AC":
            await ctx.channel.send(user + " AC'd on " + problem_name + " worth "
            + str(problem_points) + " points HOLY SHIT <:PogU:594138006999269427>\nLink: " + problem_link)
        else:
            await ctx.channel.send(user + " FUCKING " + status + "'d on " + problem_name + " worth "
            + str(problem_points) + " points LMAOOOOOO <:PepeLaugh:594138680898355200>\nLink: " + problem_link)

bot.run(api_key)
