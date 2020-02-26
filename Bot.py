import discord
import requests
from config import *
from discord.ext import commands, tasks

prefix = "$"
bot = commands.Bot(command_prefix=prefix, help_command=None)


def get_submissions_json(user):
    return requests.get(f"https://dmoj.ca/api/user/submissions/{user}").json()


def get_user_stats_json(user):
    return requests.get(f"https://dmoj.ca/api/user/info/{user}").json()


def get_problem_info(problem):
    problem_json = requests.get(f"https://dmoj.ca/api/problem/info/{problem}").json()
    problem_info = {
        "name": problem_json["name"],
        "points": problem_json["points"],
        "link": f"https://dmoj.ca/problem/{problem}"
    }
    return problem_info


# def error_handler(function):



@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="$help"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.channel.send(f'This command is on a {error.retry_after:.2f} cooldown')


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def help(ctx):
    output_message = discord.Embed(
        title="Help"
    )
    output_message.add_field(name="Stats", value="Gets the stats for the given user", inline=False)
    output_message.add_field(name="Submissions", value="Gets the status of the *nth*\
    most submission from the given user", inline=False)
    await ctx.channel.send(embed=output_message)


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def stats(ctx, user=None):
    # No user is given
    if user is None:
        await ctx.channel.send(">>> **Parameters** (User)\n**User**: Name of the user on DMOJ")
        return
    if user == "Bartpuup" or user == "bartpuup":
        await ctx.channel.send("Bert got 75% on a grade 11 math test lmaoooooo")
        return
    user_submissions = None
    user_info = None
    # Attempts to get user submissions
    try:
        user_submissions = get_submissions_json(user)
        user_info = get_user_stats_json(user)
    except:
        await ctx.channel.send("That user does not exist")
        return
    keys = list(user_submissions.keys())
    results_count = {}
    # Count status of submissions
    for i in range(len(keys)):
        status = user_submissions[keys[i]]["result"]
        if status is not None:
            if status in results_count:
                results_count[status] += 1
            else:
                results_count[status] = 1
    # Embedded output
    output_stats = discord.Embed(
        title=f"AC rate: {round(results_count['AC'] / len(keys), 2) * 100}%",
        colour=discord.Colour.gold(),
        description=f"Total submissions: {len(keys)}",
        url=f"https://dmoj.ca/user/{user}"
    )
    output_stats.add_field(name="Rating", value=str(user_info["contests"]["current_rating"]), inline=True)
    output_stats.add_field(name="Points", value=str(int(user_info["performance_points"])), inline=True)
    output_stats.add_field(name="Solved Problems", value=str(len(user_info["solved_problems"])), inline=True)
    # Add all submission statuses to embed output
    for i in sorted(results_count.keys()):
        output_stats.add_field(name=i, value=str(results_count[i]), inline=True)
    output_stats.set_author(name=f"Stats for {user}")
    await ctx.channel.send(embed=output_stats)


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def submissions(ctx, user=None, num=1):
    # No user is given
    if user is None:
        await ctx.channel.send(">>> **Parameters** (User, Amount)\n" +
                               "**User**: Name of the user on DMOJ\n" +
                               "**Amount: ** Amount of submissions to get")
        return
    if user == "Bartpuup" or user == "bartpuup":
        await ctx.channel.send("Bert got 75% on a grade 11 math test lmaoooooo")
        return
    user_submissions = None
    # Attempts to get user submissions
    try:
        user_submissions = get_submissions_json(user)
    except:
        await ctx.channel.send("That user does not exist")
        return
    keys = list(user_submissions.keys())
    problem = user_submissions[keys[-num]]
    status = problem['result']

    problem_info = get_problem_info(problem['problem'])
    problem_name = problem_info["name"]
    problem_points = problem_info["points"]
    problem_link = problem_info["link"]

    if status == "AC":
        await ctx.channel.send(f"{user} AC'd on {problem_name} worth {problem_points} points HOLY SHIT "
                               f"<:PogU:594138006999269427>\nLink: {problem_link}")
    else:
        await ctx.channel.send(f"{user} FUCKING {status}'d on {problem_name} worth {problem_points} points "
                               f"LMAOOOOOO <:PepeLaugh:594138680898355200>\nLink: {problem_link}")

channel = None
@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def contests(ctx, channel_id=""):
    if channel_id == "":
        await ctx.channel.send(">>> **Parameters** (Channel)\n**Channel**: Channel ID of the channel where you want" +
                               "the reminders to be sent")
        return
    global channel
    try:
        channel = int(channel_id[2:-1])
        await ctx.channel.send("Reminders of DMOJ contests will now be sent in " + channel_id)
    except:
        await ctx.channel.send("Sorry, that channel does not exist")


# Passively get contests, right now implemented as a command
previous_contests = requests.get("https://dmoj.ca/api/contest/list").json()
previous_keys = list(previous_contests.keys())
@bot.command()
async def new_contests(ctx):
    # Channel not configured
    if channel is None:
        return
    global previous_contests
    global previous_keys
    current_contests = None
    try:
        current_contests = requests.get("https://dmoj.ca/api/contest/list").json()
    except:
        await ctx.channel.send("Error getting contests")
        return
    current_keys = list(current_contests.keys())
    # Compares updated contests with previous contests
    if len(current_keys)-len(previous_keys) == 0:
        await bot.get_channel(channel).send("No new contests")
    else:
        for i in range(1, len(current_keys)-len(previous_keys)):
            embed_contests = discord.Embed(
                title=current_contests[current_keys[-i]]["name"],
                colour=discord.Colour.gold(),
                url="https://dmoj.ca/contest/" + current_keys[-i]
            )
            embed_contests.add_field(name="Start Time", value=current_contests[current_keys[-i]]["start_time"], inline=False)
            embed_contests.add_field(name="End Time", value=current_contests[current_keys[-i]]["end_time"], inline=False)
            embed_contests.add_field(name="Time Limit", value=current_contests[current_keys[-i]]["time_limit"], inline=False)
            embed_contests.set_author(name="New contest")
            await bot.get_channel(channel).send(embed=embed_contests)
        previous_contests = current_contests
        previous_keys = current_keys


bot.run(api_key)
