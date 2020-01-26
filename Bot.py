import discord
import requests
from config import *
from discord.ext import commands, tasks

prefix = "$"
bot = commands.Bot(command_prefix=prefix, help_command=None)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="$help"))


@bot.command()
async def help(ctx):
    output_message = discord.Embed(
        title="Help"
    )
    output_message.add_field(name="Stats", value="Gets the stats for the given user", inline=False)
    output_message.add_field(name="Submissions", value="Gets the status of the most recent *n*\
    submissions from the given user", inline=False)
    await ctx.channel.send(embed=output_message)


@bot.command()
async def stats(ctx, user=None):
    # No user is given
    if user is None:
        await ctx.channel.send(">>> **Parameters** (User)\n**User**: Name of the user on DMOJ")
        return
    user_submissions = None
    user_info = None
    # Attempts to get user submissions
    try:
        user_submissions = requests.get(f"https://dmoj.ca/api/user/submissions/{user}").json()
        user_info = requests.get(f"https://dmoj.ca/api/user/info/{user}").json()
    except:
        await ctx.channel.send("That user does not exist")
        return
    # Keys of submissions dict
    keys = list(user_submissions.keys())
    results_count = {}
    # Count status of submissions
    for i in range(len(keys)):
        status = user_submissions[keys[i]]["result"]
        if status is None:
            continue
        if status in results_count:
            results_count[status] += 1
        else:
            results_count[status] = 1
    # Embedded output
    output_stats = discord.Embed(
        title=f"AC rate: {round(results_count["AC"]/len(keys), 2)*100}%",
        colour=discord.Colour.gold(),
        description=f"Total submissions: {len(keys)}",
        url=f"https://dmoj.ca/user/{user}"
    )
    output_stats.add_field(name="Rating", value=str(user_info["contests"]["current_rating"]), inline=True)
    output_stats.add_field(name="Points", value=str(int(user_info["performance_points"])), inline=True)
    output_stats.add_field(name="Solved Problems", value=str(len(user_info["solved_problems"])), inline=True)
    for i in sorted(results_count.keys()):
        output_stats.add_field(name=i, value=str(results_count[i]), inline=True)
    output_stats.set_author(name=f"Stats for {user}")
    await ctx.channel.send(embed=output_stats)


@bot.command()
async def submissions(ctx, user=None, num=1):
    # No user is given
    if user is None:
        await ctx.channel.send(">>> **Parameters** (User, Amount)\n" +
                               "**User**: Name of the user on DMOJ\n" +
                               "**Amount: ** Amount of submissions to get")
        return
    user_submissions = None
    # Attempts to get user submissions
    try:
        user_submissions = requests.get(f"https://dmoj.ca/api/user/submissions/{user}").json()
    except:
        await ctx.channel.send("That user does not exist")
        return
    # Keys of submissions dict
    keys = list(user_submissions.keys())
    # No more than 10 submissions is allowed
    if num > 10:
        await ctx.channel.send("You can only get a maximum of 10 problems")
        return
    for i in range(1, num+1):
        status = user_submissions[keys[-i]]['result']
        # Get problem details and convert to dict
        problem = requests.get(f"https://dmoj.ca/api/problem/info/{user_submissions[keys[-i]]['problem']}").json()
        # Get specific info
        problem_name = problem["name"]
        problem_points = problem["points"]
        problem_link = f"https://dmoj.ca/problem/{user_submissions[keys[-i]]['problem']}"
        if status == "AC":
            await ctx.channel.send(f"{user} AC'd on {problem_name} worth {problem_points} points HOLY SHIT <:PogU:594138006999269427>\nLink: {problem_link}")
        else:
            await ctx.channel.send(f"{user} FUCKING {status}'d on {problem_name} worth {problem_points} points LMAOOOOOO <:PepeLaugh:594138680898355200>\nLink: {problem_link}")

bot.run(api_key)
