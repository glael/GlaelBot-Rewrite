import threading

import discord
from discord.ext.commands import Bot
from EconomyBot import EconomyBot
from GalgjeBot import GalgjeBot
from GeneralBot import GeneralBot
from BattleshipBot import BattleshipBot
from RedditBot import RedditBot
from MinesweeperBot import MinesweeperBot
import asyncio
import random
import urllib.request
import json
import sqlite3
import datetime

bot = Bot(command_prefix="")
economy_bot = EconomyBot(bot)
galgje_bot = GalgjeBot(bot)
general_bot = GeneralBot(bot)
battleship_bot = BattleshipBot(bot)
reddit_bot = RedditBot(bot, economy_bot)
minesweeper_bot = MinesweeperBot(bot)

conn = sqlite3.connect('/home/glael/glaelbot/stats.db')

# -----------------------------------GENERAL STUFF----------------------------------------------------------------------
@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name="glael.ddns.net"))
    battleship_bot.generateEmoji()
    minesweeper_bot.generateEmoji()
    print("starting...")

def update_db(message):
    cursor = conn.cursor()
    now = datetime.datetime.now()
    dateString = now.replace(microsecond=0, second=0, minute=now.minute-now.minute%5, hour=(now.hour+1)%24).isoformat()
    cursor.execute('SELECT * FROM stats WHERE time==\'' + dateString + '\'')
    if (cursor.fetchone() != None):
        cursor.execute('UPDATE stats set amount = amount + 1 WHERE time == \'' + dateString + '\'')
    else:
        cursor.execute('INSERT INTO stats VALUES (\'' + dateString + '\', 1)')
    conn.commit()

@bot.event
async def on_message(message):
    if bot._skip_check(message.author, bot.user):  											# don't check on yourself
        if message.content.lower()[0:4] == "echo":
            if message.content.lower()[0:24] != "echo echo echo echo echo":
                await bot.send_message(message.channel, message.content[4:])
            else:
                await bot.send_message(message.channel, "<@" + str(message.author.id) + ">" + " nee, ga dood.")
        print("selfcheck")
        return
    if message.channel.id == "433179719471726602":											# ignore discordrpg channel
        return
    if message.channel.id in ["418130378243440645", "367274120930394112", "231823001912475648"] and len(message.content) > 0:		# process battleship commands
        await battleship_bot.evalMessage(message)
    if message.content == "XD" or " XD" in message.content or "XD " in message.content:
        await bot.send_message(message.channel, "*ECKSDEE")
    if "plop" in message.content.lower() or "kabouter" in message.content.lower():							# "plop" or "kabouter" => react with plopworst emoji
        await general_bot.add_reaction(message, "plopworst", "223911633682956290")
    if "(╯°□°）╯︵ ┻━┻" in message.content:												# tableflip => put table back
        await bot.send_message(message.channel, "┬─┬ノ( º _ ºノ)")
    if message.content.lower() == ">:(" or message.content.lower() == ">:c":  											# "mekker" => reply with goat image
        await general_bot.add_reaction(message, "angery", "223911633682956290")
    if "mekker".lower() in message.content.lower():  											# "mekker" => reply with goat image
        await bot.send_file(message.channel, "/home/glael/glaelbot/goat.jpg")
    if "filii" in message.content.lower():  												# "filii" => reply with poop emoji
        await bot.add_reaction(message, "💩")
    if ("linux" in message.content.lower()) and not ("gnu" in message.content.lower()):							# "linux" without "gnu" => reply with stallman emoji
        await general_bot.add_reaction(message, "stallman", "231823001912475648")
    if "pxl" in message.content.lower():												# "pxl" => reply with planb emoji
        await general_bot.add_reaction(message, "planb", "231823001912475648")
    if "triggered" in message.content.lower():												# "triggered" => reply with reee emoji
        await general_bot.add_reaction(message, "reee", "231823001912475648")
    if "jojo" in message.content.lower():
        await general_bot.add_reaction(message, "joshit", "231823001912475648")
    if "wifi" in message.content.lower():												# "wifi" => reply with feelsUhasseltMan emoji
        await general_bot.add_reaction(message, "FeelsUhasseltMan", "231823001912475648")
    if "arch" in message.content.lower():
        await general_bot.add_reaction(message, "arch", "231823001912475648")
    if "gentoo" in message.content.lower():
        await general_bot.add_reaction(message, "gentoo", "231823001912475648")
    if "perl" in message.content.lower():
        await general_bot.add_reaction(message, "perl", "231823001912475648")
    if "google" in message.content.lower():
        await general_bot.add_reaction(message, "goolag", "231823001912475648")
    if "facebook" in message.content.lower() or "FB_IMG_" in message.content or len(message.attachments) > 0 and "FB_IMG_" in message.attachments[0]["url"]:
        await general_bot.add_reaction(message, "facebad", "231823001912475648")
    if "void" in message.content.lower():
        await general_bot.add_reaction(message, "void", "231823001912475648")
    if "eend" in message.content.lower():
        await general_bot.add_reaction(message, "wceend", "231823001912475648")
    if "kde" in message.content.lower():
        await general_bot.add_reaction(message, "kde", "231823001912475648")
    if "nvidia" in message.content.lower() or "novideo" in message.content.lower():
        await general_bot.add_reaction(message, "novideo", "231823001912475648")
    if "bosch" in message.content.lower():
        await general_bot.add_reaction(message, "bosch", "231823001912475648")
    if "hln" in message.content.lower() or "het laatste nieuws" in message.content.lower():
        await general_bot.add_reaction(message, "clickbait", "231823001912475648")
    if "ubuntu" in message.content.lower():
        await general_bot.add_reaction(message, "ubuntu", "231823001912475648")
    if message.content.lower() == "rigged":
        await general_bot.add_reaction(message, "carat", "231823001912475648")
    if "😂" in message.content.lower():
        await general_bot.add_reaction(message, "nojoy", "231823001912475648")
    if "opel" in message.content.lower():
        await general_bot.add_reaction(message, "opel", "231823001912475648")
    if "owo" in message.content.lower() or "o wo" in message.content.lower() or "ow o" in message.content.lower() or "o w o" in message.content.lower():
        await general_bot.add_reaction(message, "owo", "231823001912475648")
    if len(message.attachments) > 0 and message.channel.id == "224930984762540032" and message.author.id == "156329412126572544":
        await general_bot.add_reaction(message, "9gag", "231823001912475648")
    if len(message.attachments) == 1 and "height" in message.attachments[0] and "width" in message.attachments[0] and (message.attachments[0]["filename"].endswith(".png") or message.attachments[0]["filename"].endswith(".jpg")):
        await general_bot.ifunny_test(message)												# check if ifunny logo is present (currently broken)
    update_db(message)
    await bot.process_commands(message)
    return


@bot.event
async def on_reaction_add(reaction, user):
    if bot._skip_check(user, bot.user):  # don't check on yourself
        return
    # NO JOY
    if "😂" in reaction.emoji:
        await general_bot.add_reaction(reaction.message, "nojoy", "231823001912475648")
    # COIN DROP
    if len(reaction.message.embeds) == 1 and reaction.message.embeds[0]["title"] == "Coin Drop":
        timestamp = reaction.message.timestamp
        channel = reaction.message.channel
        await bot.delete_message(reaction.message)
        await economy_bot.coin_drop(user.id, user.name, timestamp, channel)
    # GALGJE
    elif len(reaction.message.embeds) == 1 and reaction.message.embeds[0]["title"] == "Galgje":
        await galgje_bot.user_reacted(reaction, user)
    # BLACKJACK
    elif len(reaction.message.embeds) == 1 and reaction.message.embeds[0]["title"] == "BlackJack" and (user.id != "338099908210851840" and user.id != "285157874479661058"):
        await economy_bot.reaction_added(reaction, user)
    # BATTLESHIP
    elif len(reaction.message.embeds) == 1 and reaction.message.embeds[0]["title"] == "Battleship: your waters.":
        await battleship_bot.evalReaction(reaction)
    # REDDIT
    elif len(reaction.message.embeds) == 1 and reaction.message.embeds[0]["title"] == "/r/(not)TheOnion?":
        await reddit_bot.user_reacted(reaction, user)
    return


@bot.event
async def on_reaction_remove(reaction, user):
    if "😂" in reaction.emoji:
        await general_bot.remove_reaction(reaction.message, "nojoy", "231823001912475648")

# -----------------------------------GENERAL_BOT------------------------------------------------------------------------
@bot.command(pass_context=True)
async def Reverse(ctx, *args):
    await general_bot.reverse(ctx, *args)


@bot.command(pass_context=True)
async def Pepe(ctx, *args):
    await general_bot.pepe(ctx, *args)


@bot.command(pass_context=True)
async def EyeBleach(ctx, *args):
    await general_bot.eyebleach(ctx, *args)


@bot.command(pass_context=True)
async def Smug(ctx, *args):
    await general_bot.smug(ctx, *args)


@bot.command(pass_context=True)
async def echo(ctx, *args):
    await general_bot.echo(ctx, *args)


@bot.command(pass_context=True)
async def star(ctx, *args):
    await general_bot.star(ctx, *args)


@bot.command(pass_context=True)
async def ping(ctx, *args):
    await bot.say("pong")


@bot.command(pass_context=True)
async def fortune(ctx, *args):
    await general_bot.fortune(ctx, *args)

@bot.command(pass_context=True)
async def eightBall(ctx, *args):
    await general_bot.eightBall(ctx, *args)

@bot.command(pass_context=True)
async def blinCat(ctx, *args):
    await bot.send_file(ctx.message.channel, "/home/glael/glaelbot/blincat.jpg")


# -----------------------------------ECONOMY_BOT------------------------------------------------------------------------
@bot.command(pass_context=True)
async def economy(ctx, *args):
    await economy_bot.economy(ctx, *args)


@bot.command(pass_context=True)
async def bjrank(ctx, *args):
    await economy_bot.bjrank(ctx, *args)


@bot.command(pass_context=True)
async def bjdice(ctx, *args):
    await economy_bot.bjdice(ctx, *args)


@bot.command(pass_context=True)
async def blackj(ctx, *args):
    await economy_bot.blackj(ctx, *args)


@bot.command(pass_context=True)
async def setEconomy(ctx, *args):
    await economy_bot.set_economy(ctx, *args)


# ------------------------------------GALGJE_BOT------------------------------------------------------------------------
@bot.command(pass_context=True)
async def galgje(ctx, *args):
    await galgje_bot.galgje(ctx, *args)


# ---------------------------------MINESWEEPER_BOT----------------------------------------------------------------------
@bot.command(pass_context=True)
async def MineSweeper(ctx, *args):
    await minesweeper_bot.print_minefield(ctx, *args)


# ---------------------------------BATTLESHIP_BOT-----------------------------------------------------------------------
@bot.command(pass_context=True)
async def BattleShip(ctx, *args):
    await battleship_bot.startNewGame(ctx, *args)


@bot.command(pass_context=True)
async def ResetBattleShip(ctx, *args):
    await battleship_bot.resetBattleShip(ctx, *args)


# ----------------------------------REDDIT_BOT--------------------------------------------------------------------------
@bot.command(pass_context=True)
async def notTheOnion(ctx, *args):
    await reddit_bot.notTheOnion(ctx, *args)

# -------------------------------------TIMERS---------------------------------------------------------------------------
async def randombjevent():
    await bot.wait_until_ready()
    channel = discord.Object(id='367274120930394112')
#    channel = discord.Object(id='372472584228438017')
    while not bot.is_closed:
        await asyncio.sleep(random.randint(3600, 9000))  # task runs at most every hour, probably less. Will always run on startup
        testEmbed = discord.Embed()
        testEmbed.title = "Coin Drop"
        testEmbed.colour = discord.Colour.blue()
        testEmbed.description = "Oops! i dropped some coins!\nThe first to react with 🅱 gets 50 free bj$."
        message = await bot.send_message(channel, embed=testEmbed)
        await bot.add_reaction(message, "🅱")
#        await asyncio.sleep(random.randint(3600, 9000))  # task runs at most every hour, probably less. Will always run on startup

bot.loop.create_task(randombjevent())

async def randomchronoevent():
    await bot.wait_until_ready()
    channel = discord.Object(id='233229470062870529')
    while not bot.is_closed:
        with urllib.request.urlopen("https://api.chrono.gg/shop") as url:
            data = json.loads(url.read().decode())
            firstId = data[0]['_id']
            f = open('/home/glael/glaelbot/chronoshopid.txt', 'r+')
            fileId = f.read()

            if fileId != firstId:
                await bot.send_message(channel, "New games were added to the chrono.gg shop: https://chrono.gg/shop")
                f.seek(0)
                f.write(firstId)
            f.close()
        await asyncio.sleep(3600)

bot.loop.create_task(randomchronoevent())

file = open("/home/glael/glaelbot/key.txt", "r")
bot.run(file.read().rstrip('\n'))
