import threading

import discord
from discord.ext.commands import Bot
from EconomyBot import EconomyBot
from GalgjeBot import GalgjeBot
from GeneralBot import GeneralBot
from BattleshipBot import BattleshipBot
import asyncio
import random

bot = Bot(command_prefix="")
economy_bot = EconomyBot(bot)
galgje_bot = GalgjeBot(bot)
general_bot = GeneralBot(bot)
battleship_bot = BattleshipBot(bot)







# -----------------------------------GENERAL STUFF----------------------------------------------------------------------
@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name="glael.ddns.net"))
    battleship_bot.generateEmoji()
    print("starting...")


@bot.event
async def on_message(message):
    if bot._skip_check(message.author, bot.user):  											# don't check on yourself
        return
    if message.channel.id == "433179719471726602":											# ignore discordrpg channel
        return
    if message.channel.id in ["418130378243440645", "367274120930394112", "231823001912475648"] and len(message.content) > 0:		# process battleship commands
        await battleship_bot.evalMessage(message)
    if "plop" in message.content.lower() or "kabouter" in message.content.lower():							# "plop" or "kabouter" => react with plopworst emoji
        await general_bot.add_reaction(message, "plopworst", "223911633682956290")
    if "(╯°□°）╯︵ ┻━┻" in message.content:												# tableflip => put table back
        await bot.send_message(message.channel, "┬─┬ノ( º _ ºノ)")
    if "mekker".lower() in message.content.lower():  											# "mekker" => reply with goat image
        await bot.send_file(message.channel, "/home/pi/Documents/glaelbot/goat.jpg")
    if "filii" in message.content.lower():  												# "filii" => reply with poop emoji
        await bot.add_reaction(message, "💩")
    if ("linux" in message.content.lower()) and not ("gnu" in message.content.lower()):							# "linux" without "gnu" => reply with stallman emoji
        await general_bot.add_reaction(message, "stallman", "231823001912475648")
    if "pxl" in message.content.lower():												# "pxl" => reply with planb emoji
        await general_bot.add_reaction(message, "planb", "231823001912475648")
    if "triggered" in message.content.lower():												# "triggered" => reply with reee emoji
        await general_bot.add_reaction(message, "reee", "231823001912475648")
    if "wifi" in message.content.lower():												# "wifi" => reply with feelsUhasseltMan emoji
        await general_bot.add_reaction(message, "FeelsUhasseltMan", "231823001912475648")
    if len(message.attachments) == 1 and "height" in message.attachments[0] and "width" in message.attachments[0] and (message.attachments[0]["filename"].endswith(".png") or message.attachments[0]["filename"].endswith(".jpg")):
        await general_bot.ifunny_test(message)												# check if ifunny logo is present (currently broken)
    await bot.process_commands(message)
    return


@bot.event
async def on_reaction_add(reaction, user):
    if bot._skip_check(user, bot.user):  # don't check on yourself
        return
    # COIN DROP
    if len(reaction.message.embeds) == 1 and reaction.message.embeds[0]["title"] == "Coin Drop":
        await bot.delete_message(reaction.message)
        await economy_bot.coin_drop(user.id, user.name)
    # GALGJE
    elif len(reaction.message.embeds) == 1 and reaction.message.embeds[0]["title"] == "Galgje":
        await galgje_bot.user_reacted(reaction, user)
    # BLACKJACK
    if len(reaction.message.embeds) == 1 and reaction.message.embeds[0]["title"] == "BlackJack" and (user.id != "338099908210851840" and user.id != "285157874479661058"):
        await economy_bot.reaction_added(reaction, user)
    # BATTLESHIP
    if len(reaction.message.embeds) == 1 and reaction.message.embeds[0]["title"] == "Battleship: your waters.":
        await battleship_bot.evalReaction(reaction)
    return


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


# ---------------------------------BATTLESHIP_BOT-----------------------------------------------------------------------
@bot.command(pass_context=True)
async def BattleShip(ctx, *args):
    await battleship_bot.startNewGame(ctx, *args)


@bot.command(pass_context=True)
async def ResetBattleShip(ctx, *args):
    await battleship_bot.resetBattleShip(ctx, *args)


# -------------------------------------TIMERS---------------------------------------------------------------------------
async def randombjevent():
    await bot.wait_until_ready()
    channel = discord.Object(id='367274120930394112')
    while not bot.is_closed:
        await asyncio.sleep(random.randint(3600, 9000))  # task runs at most every hour, probably less. Will always run on startup
        testEmbed = discord.Embed()
        testEmbed.title = "Coin Drop"
        testEmbed.colour = discord.Colour.blue()
        testEmbed.description = "Oops! i dropped some coins!\nThe first to react with 🅱 gets 50 free bj$."
        message = await bot.send_message(channel, embed=testEmbed)
        await bot.add_reaction(message, "🅱")


bot.loop.create_task(randombjevent())


file = open("/home/pi/Documents/glaelbot/key.txt", "r")
bot.run(file.read().rstrip('\n'))