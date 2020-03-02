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


def get_submission_info(submission_id):
    problem_name = submission_id["problem"]
    problem_json = requests.get(f"https://dmoj.ca/api/problem/info/{problem_name}").json()
    problem_info = {
        "name": problem_name,
        "points": problem_json["points"],
        "link": f"https://dmoj.ca/problem/{problem_name}",
        "status": submission_id["result"],
        "obtained_points": submission_id["points"]
    }
    return problem_info


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
    output_message.add_field(name="Rank", value="Get the predicted rating for the user after the specified contest")
    output_message.add_field(name="More Help", value="For more information, visited my GitHub")
    await ctx.channel.send(embed=output_message)


@commands.cooldown(1, 5, commands.BucketType.user)
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
    user_submissions = None
    # Attempts to get user submissions
    try:
        user_submissions = get_submissions_json(user)
    except:
        await ctx.channel.send("That user does not exist")
        return
    keys = list(user_submissions.keys())
    problem = user_submissions[keys[-num]]

    problem_info = get_submission_info(problem)
    problem_name = problem_info["name"]
    problem_points = problem_info["points"]
    problem_link = problem_info["link"]
    problem_status = problem_info["status"]

    if problem_status == "AC":
        await ctx.channel.send(f"{user} AC'd on {problem_name} worth {problem_points} points HOLY SHIT "
                               f"<:PogU:594138006999269427>\nLink: {problem_link}")
    else:
        await ctx.channel.send(f"{user} FUCKING {problem_status}'d on {problem_name} worth {problem_points} points "
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

# TODO
# Correctly determine winner based on submission time
# Generate list rankings: 1st, 2nd, etc
"""@bot.command()
async def race(ctx, problem, time, *users):
    users_list = " ".join(users)


async def compare_submissions(problem, users):
    winner = None
    winner_score = 0
    winner_submission_time = None

    for i in range(len(users)):
        user_submissions = get_submissions_json(users[i])
        submissions_keys = list(user_submissions.keys())
        for j in range(1, len(submissions_keys)+1):
            submission_id = user_submissions[submissions_keys[-j]]
            status = submission_id["result"]
            name = submission_id["problem"]
            score = submission_id["points"]
            if problem == name:
                if status == "AC" and winner is None:
                    return winner
                elif score >= winner_score:
                    if winner is None:
                        winner = users[i]
                        winner_submission_time = submission_id
                        winner_score = score
                    elif submission_id < winner_submission_time:
                        winner = users[i]
                        winner_submission_time = submission_id
                        winner_score = score
"""

bot.run(api_key)
