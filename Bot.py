import discord
import requests
import Submission
import Problem
import User
from config import *
from discord.ext import commands, tasks

prefix = "$"
bot = commands.Bot(command_prefix=prefix, help_command=None)


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="$help"))
    new_contests.start()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.channel.send(f'This command is on a {error.retry_after:.2f} cooldown')


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def help(ctx):
    output_message = discord.Embed(
        title="Help",
        url="https://github.com/RyanL123/DMOJBot"
    )
    output_message.add_field(name="Stats", value="Gets the stats for the given user", inline=False)
    output_message.add_field(name="Submissions", value="Gets the status of the *nth*\
    most submission from the given user", inline=False)
    output_message.add_field(name="Rank", value="Get the predicted rating for the user after the specified contest", inline=False)
    output_message.add_field(name="More Help", value="For more information, visited my GitHub at https://github.com/RyanL123/DMOJBot", inline=False)
    await ctx.channel.send(embed=output_message)


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def stats(ctx, name=None):
    # No user is given
    if name is None:
        await ctx.channel.send(">>> **Parameters** (User)\n**User**: Name of the user on DMOJ")
        return

    # Catch user does not exist
    try:
        user = User.User(name)
    except:
        await ctx.channel.send("That user does not exist")
        return

    # Embedded output
    output_stats = discord.Embed(
        title=f"AC rate: {user.ac_rate}%",
        colour=discord.Colour.gold(),
        description=f"Total submissions: {len(user.submissions)}",
        url=f"https://dmoj.ca/user/{name}"
    )
    output_stats.add_field(name="Rating", value=user.current_rating, inline=True)
    output_stats.add_field(name="Points", value=user.performance_points, inline=True)
    output_stats.add_field(name="Solved Problems", value=str(len(user.solved_problems)), inline=True)

    # Add all submission statuses to embed output
    for i in sorted(user.results):
        output_stats.add_field(name=i, value=str(user.results[i]), inline=True)
    output_stats.set_author(name=f"Stats for {name}")
    await ctx.channel.send(embed=output_stats)


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def submissions(ctx, name=None, num=1):
    # No user is given
    if name is None:
        await ctx.channel.send(">>> **Parameters** (User, Amount)\n" +
                               "**User**: Name of the user on DMOJ\n" +
                               "**Amount: ** Amount of submissions to get")
        return
    try:
        user = User.User(name)
    except:
        await ctx.channel.send("That user does not exist")
        return

    submission = user.recent_submission(num)

    if submission.verdict == "AC":
        await ctx.channel.send(f"{user.name} AC'd on {submission.problem.name} worth {submission.problem.points} points HOLY SHIT "
                               f"<:PogU:594138006999269427>\nLink: {submission.problem.link}")
    else:
        await ctx.channel.send(f"{user.name} FUCKING {submission.verdict}'d on {submission.problem.name} worth {submission.problem.points} points "
                               f"LMAOOOOOO <:PepeLaugh:594138680898355200>\nLink: {submission.problem.link}")

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


previous_contests = requests.get("https://dmoj.ca/api/contest/list").json()
previous_keys = list(previous_contests.keys())


@tasks.loop(hours=8)
async def new_contests():
    # Channel not configured
    if channel is None:
        return
    global previous_contests
    global previous_keys
    current_contests = None
    try:
        current_contests = requests.get("https://dmoj.ca/api/contest/list").json()
    except:
        await bot.get_channel(channel).send("Error getting contests")
        return
    current_keys = list(current_contests.keys())
    if len(current_keys) - len(previous_keys) != 0:
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


@bot.command()
async def rank(ctx, contest, user):
    try:
        ratings = requests.get(f"https://evanzhang.me/rating/contest/{contest}/api").json()
    except:
        await ctx.channel.send("That contest does not exist")
        return
    all_contests = requests.get("https://dmoj.ca/api/contest/list").json()
    embed_rank = discord.Embed(
        title=all_contests[contest]["name"],
        colour=discord.Colour.gold(),
        url=f"https://dmoj.ca/contest/{contest}"
    )
    embed_rank.add_field(name="User", value=user, inline=False)
    embed_rank.add_field(name="Old Rating", value=ratings["users"][user]["old_rating"], inline=False)
    embed_rank.add_field(name="New Rating", value=ratings["users"][user]["new_rating"], inline=False)
    embed_rank.add_field(name="Rating Change", value=ratings["users"][user]["rating_change"], inline=False)
    await ctx.channel.send(embed=embed_rank)

bot.run(api_key)
